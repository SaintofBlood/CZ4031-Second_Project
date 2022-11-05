import time
import traceback
from functools import partial

from PyQt5 import QtWidgets, uic, Qt, QtSvg, QtCore
import sys, psycopg2

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QGroupBox, QVBoxLayout, QTextEdit, QLabel, \
    QSplashScreen
import sys
import json
import simplejson as json_test
from annotation import *
from preprocessing import *
from blockdiag import parser, builder, drawer
import psycopg2.extensions as ext


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi("TEST.ui", self)

        self.setWindowTitle("CZ 4031 Proj II")

        #Connect buttons to code
        self.connection_btn.clicked.connect(self.Sql_Inicalize_Conn)
        self.sql_btn.clicked.connect(self.Execute_SQL_Command)
       # self.dQp1.clicked.connect(self.displayDiagram)

        self.conn = 123


        #for x in range(0, 10, 1):
        #   tab1 = QtWidgets.QWidget()
        #   tab1.layout = QVBoxLayout(self)
        #   groupbox = QGroupBox("Annotation")
        #   groupbox.setObjectName = "Annotation"
        #   vbox = QVBoxLayout()
        #   groupbox.setLayout(vbox)
        #   TEXT = QTextEdit()
        #   TEXT.setText("XD123231321231213")
        #   TEXT.setReadOnly(True)
        #   BUTTON = QPushButton("Display Phisical Query Plan")
        #   vbox.addWidget(TEXT)
        #   self.AddToTab(tab1, groupbox)
        #   self.AddToTab(tab1, BUTTON)
        #   tab1.setLayout(tab1.layout)
        #   self.tabWidget.addTab(tab1, str(x))


          #  print(self.fiutek)

        self.show()

    def AddToTab(self, tab, obj):
        tab.layout.addWidget(obj)

#SQL Connection
    def Sql_Inicalize_Conn(self):
        print("Clicked!")

        try:
            self.ConnectToPostgreSQL()

            self.status_d.setStyleSheet("color: green; font-weight: 600")
            self.status_d.setText("Connected!")
            self.sql_btn.setEnabled(True)

            self.conn.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)



#Execute SQL Command
    def Execute_SQL_Command(self):
       # try:

        self.FlushData()
        self.ConnectToPostgreSQL()

        tab_INFO = QtWidgets.QWidget()
        tab_INFO.layout = QVBoxLayout()

        tab_INFO_text = QLabel("START FETCHING PLANS \n It might freeze APP , wait!!")
        tab_INFO_text.setStyleSheet("color: red")
        tab_INFO_text.setAlignment(QtCore.Qt.AlignCenter)
        tab_INFO_text.setFont(QFont('Arial', 20))
        tab_INFO.setLayout(tab_INFO.layout)

        self.AddToTab(tab_INFO, tab_INFO_text)
        self.tabWidget.addTab(tab_INFO, "INFO")

        QApplication.processEvents()



        self.cursor = self.conn.cursor()
        postgreSQL_select_Query = self.sql_qr_txt.toPlainText()
        result = execute_originalquery(self.cursor, postgreSQL_select_Query)
        #print(result_oryg_JSON)
        # if no join in QEP, shrink off and on config list
        if check_for_join(result):
            self.plans_list = generate_aqp(result, self.cursor,
                                                       postgreSQL_select_Query, self.conn, True)
        else:
            self.plans_list = generate_aqp(result, self.cursor,
                                                       postgreSQL_select_Query, self.conn, False)
        # For checking
        self.plans_list = repackage_output(self.plans_list)

        print("MILESTONE")

        self.tabWidget.removeTab(0)

        x = 0
        for SQL_STRING in self.plans_list:
            print(SQL_STRING)
            final_V2 = json_test.dumps(SQL_STRING)
           # final_V2 = final_V2[3:len(final_V2) - 3]
            final_OBJ_TEST = json.loads(final_V2)
            print(final_OBJ_TEST)
            #final_obj = json.loads(str(SQL_STRING[1:len(SQL_STRING) - 1]).replace('\n', ''))
            #final_obj = json.loads(SQL_STRING[1:len(str(SQL_STRING)) - 1].replace('\n', ''))
            descriptions = get_text(final_OBJ_TEST)
            print(descriptions)
            result = ""
            for description in descriptions:
                result = result + description + "\n"
            print(result)
            #head = parse_json(final_obj)
            print("-----------------------------------")
            tab1 = QtWidgets.QWidget()
            tab1.layout = QVBoxLayout()
            groupbox = QGroupBox("Annotation")
            groupbox.setObjectName = "Annotation"
            vbox = QVBoxLayout()
            groupbox.setLayout(vbox)
            TEXT = QTextEdit()
            TEXT.setReadOnly(True)
            TEXT.setText(result)
            BUTTON = QPushButton("Display Phisical Query Plan")
            BUTTON.clicked.connect(partial(self.displayDiagram, x))
            vbox.addWidget(TEXT)
            self.AddToTab(tab1, groupbox)
            self.AddToTab(tab1, BUTTON)
            tab1.setLayout(tab1.layout)
            if x == 0:
                self.tabWidget.addTab(tab1, "QEP")
            else:
                self.tabWidget.addTab(tab1, "AEP " + str(x))
            x += 1
            self.TerminateConnectionToPostgreSQL()

        #except (Exception, psycopg2.DatabaseError) as error:
        #    print("ERRRRRRRRRRRR " , error)
        #    self.TerminateConnectionToPostgreSQL()
        #    self.FlushData()

    #Display diagram button
    def displayDiagram(self, number):

        #SQL_STRING = self.plans_list_JSON[number]
#
        #SQL_STRING = SQL_STRING[0][0]
#
        #final_obj = json.loads(str(SQL_STRING[1:len(SQL_STRING) - 1]).replace('\n', ''))
#
        fetch = self.plans_list[number]



        final_V2 = json_test.dumps(fetch)

        #print("FIRST ONE ", final_obj)
        #print("SECPMD PME ", final_V2)

        final_OBJ_TEST = json.loads(final_V2)

        head = parse_json(final_OBJ_TEST)

        diag_txt = generate_blockdiag(head)

        print(number)

        tree = parser.parse_string(diag_txt)

        diagram = builder.ScreenNodeBuilder.build(tree)

        draw = drawer.DiagramDraw('SVG', diagram, filename="foo.svg")
        draw.draw()
        draw.save()

        self.svgWidget = QtSvg.QSvgWidget('foo.svg')

        self.svgWidget.show()

    def ConnectToPostgreSQL(self):
        self.conn = psycopg2.connect(
            host=self.ip_add.text(),
            database=self.db_name.text(),
            user=self.username.text(),
            password=self.passwd.text())

    def TerminateConnectionToPostgreSQL(self):
        self.conn.close()

    def CleanUI(self):
        for x in range(0, self.tabWidget.count()):
            self.tabWidget.removeTab(x)

    def FlushData(self):

        self.plans_list_JSON = {}

        self.CleanUI()
#Create SVG Diagram

data = """
blockdiag {
  orientation = portrait;

  A[label = "(Projection)"];
  B[label = "(Selection)"];
  C[label = "A conn B"];
  D[label = "Table TEST1"];
  E[label = "Table TEST2"];

  Z[label = "TEST !@#"];

  A -> B -> C -> D[dir = none];
       C -> E [dir = none];
       B -> Z [dir = none];
       A -> Z;
}
"""

#tree = parser.parse_string(data)
#
#diagram = builder.ScreenNodeBuilder.build(tree)
#
#diagram.set_default_fontfamily('sansserif-normal')
#
#draw = drawer.DiagramDraw('SVG', diagram, filename="foo.svg")
#draw.draw()
#draw.save()




def MainGUILoop():

    if QtCore.QT_VERSION >= 0x50501:
        def excepthook(type_, value, traceback_):
            traceback.print_exception(type_, value, traceback_)
            QtCore.qFatal('')

        sys.excepthook = excepthook

    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()


# Alernative? https://plantuml.com/

#Graph checker (generator): http://interactive.blockdiag.com/

# Documentation: http://blockdiag.com/en/blockdiag/introduction.html#setup
# How to embed in pyt: https://stackoverflow.com/questions/67652887/how-to-write-python-code-to-use-blockdiag-package
# Symbols: https://www.guru99.com/relational-algebra-dbms.html#14


#Old code:
        #img = Image.open('foo.png')
        #img.show()
#
        #pixmap = QPixmap('foo.png')
#
        #print(self.textV.width())
#
        #smaller_pixmap = pixmap.scaledToWidth(self.test.width())
#
        #print("XD")
#
        #self.test.setPixmap(smaller_pixmap)
