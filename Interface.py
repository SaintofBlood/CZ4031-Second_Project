from PyQt5 import QtWidgets, uic, Qt, QtSvg
import sys, psycopg2
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi("TEST.ui", self)

        self.setWindowTitle("CZ 4031 Proj II")

        #Connect buttons to code
        self.connection_btn.clicked.connect(self.Sql_Inicalize_Conn)
        self.sql_btn.clicked.connect(self.Execute_SQL_Command)
        self.dQp1.clicked.connect(self.displayDiagram)

        self.conn = 123

        self.show()


#SQL Connection
    def Sql_Inicalize_Conn(self):
        print("Clicked!")

        try:

            self.conn = psycopg2.connect(
                host=self.ip_add.text(),
                database= self.db_name.text(),
                user= self.username.text(),
                password= self.passwd.text())

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if self.conn is not None:
                self.status_d.setStyleSheet("color: green; font-weight: 600")
                self.status_d.setText("Connected!")

                self.sql_btn.setEnabled(True)

#Execute SQL Command
    def Execute_SQL_Command(self):
        try:

            self.cursor = self.conn.cursor()

            postgreSQL_select_Query = self.sql_qr_txt.toPlainText()

            self.cursor.execute(postgreSQL_select_Query)

            mobile_records = self.cursor.fetchall()

            self.annotation1.setText(str(mobile_records))

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

#Display diagram button
    def displayDiagram(self, url):

        self.svgWidget = QtSvg.QSvgWidget('foo.svg')

        self.svgWidget.show()




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
