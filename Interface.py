import sys
import json
import simplejson as json_test
import traceback
from functools import partial
from blockdiag import parser, builder, drawer

#GUI
from PyQt5 import QtWidgets, QtSvg, QtCore, QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QApplication, QGroupBox, QVBoxLayout, QTextEdit, QLabel, QWidget, QHBoxLayout, QSizePolicy

#Rest
from Annotation import *
from Preprocessing import *

PREDEFINED_SQL_QUERIES = [
    ["""SELECT *
FROM 
     orders,
     customer
WHERE
     c_custkey = o_custkey
AND
     c_name = 'Name'
ORDER BY
      c_phone  
    """],
    ["""SELECT
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
    avg(l_quantity) as avg_qty,
    avg(l_extendedprice) as avg_price,
    avg(l_discount) as avg_disc,
    count(*) as count_order
FROM
    lineitem
WHERE
    l_shipdate <= date '1998-12-01' - interval '90' day
GROUP BY
    l_returnflag,
    l_linestatus
ORDER BY
    l_returnflag,
    l_linestatus;"""],
    ["""SELECT
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) as revenue,
    o_orderdate,
    o_shippriority
FROM
    customer,
    orders,
    lineitem
WHERE
    c_mktsegment = 'BUILDING'
    AND c_custkey = o_custkey
    AND l_orderkey = o_orderkey
    AND o_orderdate < date '1995-03-15'
    AND l_shipdate > date '1995-03-15'
GROUP BY
    l_orderkey,
    o_orderdate,
    o_shippriority
ORDER BY
    revenue desc,
    o_orderdate
LIMIT 20;
"""],
    ["""SELECT
    n_name,
    sum(l_extendedprice * (1 - l_discount)) as revenue
FROM
    customer,
    orders,
    lineitem,
    supplier,
    nation,
    region
WHERE
    c_custkey = o_custkey
    AND l_orderkey = o_orderkey
    AND l_suppkey = s_suppkey
    AND c_nationkey = s_nationkey
    AND s_nationkey = n_nationkey
    AND n_regionkey = r_regionkey
    AND r_name = 'ASIA'
    AND o_orderdate >= date '1994-01-01'
    AND o_orderdate < date '1994-01-01' + interval '1' year
GROUP BY
    n_name
ORDER BY
    revenue desc;"""],
    ["""SELECT
    sum(l_extendedprice * l_discount) as revenue
FROM
    lineitem
WHERE
    l_shipdate >= date '1994-01-01'
    AND l_shipdate < date '1994-01-01' + interval '1' year
    AND l_discount between 0.06 - 0.01 AND 0.06 + 0.01
    AND l_quantity < 24;"""],
    ["""SELECT
    c_custkey,
    c_name,
    sum(l_extendedprice * (1 - l_discount)) as revenue,
    c_acctbal,
    n_name,
    c_address,
    c_phone,
    c_comment
FROM
    customer,
    orders,
    lineitem,
    nation
WHERE
    c_custkey = o_custkey
    AND l_orderkey = o_orderkey
    AND o_orderdate >= date '1993-10-01'
    AND o_orderdate < date '1993-10-01' + interval '3' month
    AND l_returnflag = 'R'
    AND c_nationkey = n_nationkey
GROUP BY
    c_custkey,
    c_name,
    c_acctbal,
    c_phone,
    n_name,
    c_address,
    c_comment
ORDER BY
    revenue desc
LIMIT 20;"""],
    ["""SELECT
    l_shipmode,
    sum(case
        when o_orderpriority = '1-URGENT'
            OR o_orderpriority = '2-HIGH'
            then 1
        else 0
    end) as high_line_count,
    sum(case
        when o_orderpriority <> '1-URGENT'
            AND o_orderpriority <> '2-HIGH'
            then 1
        else 0
    end) AS low_line_count
FROM
    orders,
    lineitem
WHERE
    o_orderkey = l_orderkey
    AND l_shipmode in ('MAIL', 'SHIP')
    AND l_commitdate < l_receiptdate
    AND l_shipdate < l_commitdate
    AND l_receiptdate >= date '1994-01-01'
    AND l_receiptdate < date '1994-01-01' + interval '1' year
GROUP BY
    l_shipmode
ORDER BY
    l_shipmode;"""],



  ]



class UI_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("CZ 4031 Proj II")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(528, 677)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 511, 121))
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(9, 16, 501, 101))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setHorizontalSpacing(4)
        self.formLayout.setVerticalSpacing(3)
        self.formLayout.setObjectName("formLayout")
        self.label_7 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.ip_add = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.ip_add.setObjectName("ip_add")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.ip_add)
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.username = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.username.setObjectName("username")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.username)
        self.label_3 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.passwd = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.passwd.setObjectName("passwd")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.passwd)
        self.label_4 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.db_name = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.db_name.setObjectName("db_name")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.db_name)
        self.horizontalLayout_3.addLayout(self.formLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout.setContentsMargins(4, -1, 5, 8)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_8 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setScaledContents(False)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setWordWrap(False)
        self.label_8.setIndent(0)
        self.label_8.setObjectName("label_8")
        self.verticalLayout.addWidget(self.label_8)
        self.status_d = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.status_d.setFont(font)
        self.status_d.setStyleSheet("border: 2px solid red")
        self.status_d.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.status_d.setLineWidth(2)
        self.status_d.setMidLineWidth(0)
        self.status_d.setTextFormat(QtCore.Qt.RichText)
        self.status_d.setAlignment(QtCore.Qt.AlignCenter)
        self.status_d.setObjectName("status_d")
        self.verticalLayout.addWidget(self.status_d)
        self.connection_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.connection_btn.setObjectName("connection_btn")
        self.verticalLayout.addWidget(self.connection_btn)
        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 2)
        self.verticalLayout.setStretch(2, 3)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.horizontalLayout_3.setStretch(0, 7)
        self.horizontalLayout_3.setStretch(1, 3)
        self.sql_qr_txt = QtWidgets.QTextEdit(self.centralwidget)
        self.sql_qr_txt.setGeometry(QtCore.QRect(10, 170, 511, 171))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.sql_qr_txt.setFont(font)
        self.sql_qr_txt.setObjectName("sql_qr_txt")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 390, 511, 231))
        self.tabWidget.setObjectName("tabWidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 2, 2))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.layoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 630, 511, 25))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.layoutWidget_2)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.aepList = QtWidgets.QComboBox(self.layoutWidget_2)
        self.aepList.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.aepList.sizePolicy().hasHeightForWidth())
        self.aepList.setSizePolicy(sizePolicy)
        self.aepList.setObjectName("aepList")
        self.horizontalLayout_2.addWidget(self.aepList)
        self.CmpQuery = QtWidgets.QPushButton(self.layoutWidget_2)
        self.CmpQuery.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CmpQuery.sizePolicy().hasHeightForWidth())
        self.CmpQuery.setSizePolicy(sizePolicy)
        self.CmpQuery.setObjectName("CmpQuery")
        self.horizontalLayout_2.addWidget(self.CmpQuery)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 140, 511, 25))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.QueryList = QtWidgets.QComboBox(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QueryList.sizePolicy().hasHeightForWidth())
        self.QueryList.setSizePolicy(sizePolicy)
        self.QueryList.setObjectName("QueryList")
        self.horizontalLayout.addWidget(self.QueryList)
        self.LoadQuery = QtWidgets.QPushButton(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LoadQuery.sizePolicy().hasHeightForWidth())
        self.LoadQuery.setSizePolicy(sizePolicy)
        self.LoadQuery.setObjectName("LoadQuery")
        self.LoadQuery.setEnabled(False)
        self.horizontalLayout.addWidget(self.LoadQuery)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 350, 511, 31))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.sql_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.sql_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sql_btn.sizePolicy().hasHeightForWidth())
        self.sql_btn.setSizePolicy(sizePolicy)
        self.sql_btn.setObjectName("sql_btn")
        self.horizontalLayout_4.addWidget(self.sql_btn)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 8)
        self.horizontalLayout_4.setStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)



        self.setCont(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CZ 4031 Proj II"))
        self.groupBox.setTitle(_translate("MainWindow", "SQL Connection"))
        self.label_7.setText(_translate("MainWindow", "Ip Address:"))
        self.ip_add.setText(_translate("MainWindow", "localhost"))
        self.label.setText(_translate("MainWindow", "Username:"))
        #self.username.setText(_translate("MainWindow", "type username...."))
        self.label_3.setText(_translate("MainWindow", "Password:"))
        #self.passwd.setText(_translate("MainWindow", "type password...."))
        self.label_4.setText(_translate("MainWindow", "Database Name:"))
        #self.db_name.setText(_translate("MainWindow", "type database name...."))
        self.label_8.setText(_translate("MainWindow", "Connection Status:"))
        self.status_d.setText(_translate("MainWindow",
                                         "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                         "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                         "p, li { white-space: pre-wrap; }\n"
                                         "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
                                         "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0004;\">-Disconnected-</span></p></body></html>"))
        self.connection_btn.setText(_translate("MainWindow", "Connect"))
        self.sql_qr_txt.setHtml(_translate("MainWindow",
                                           "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
                                           "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">SELECT * FROM region</p></body></html>"))
        self.label_5.setText(_translate("MainWindow", "Compare QEP with other AEP: "))
        self.CmpQuery.setText(_translate("MainWindow", "Compare"))
        self.label_2.setText(_translate("MainWindow", "Select Query:"))
        self.LoadQuery.setText(_translate("MainWindow", "Load Query"))
        self.sql_btn.setText(_translate("MainWindow", "Execute SQL Query"))
        
        self.username.setPlaceholderText("Type username....")
        self.passwd.setPlaceholderText("Type password....")
        self.db_name.setPlaceholderText("Type database name....")
        
        MainWindow.setFixedSize(MainWindow.size())

    def setCont(self, MainWindow):

        #Connect buttons to code
        self.connection_btn.clicked.connect(self.Sql_Inicalize_Conn)
        self.sql_btn.clicked.connect(self.Execute_SQL_Command)
        self.LoadQuery.clicked.connect(self.printSelectedQuery)
        self.CmpQuery.clicked.connect(self.compareQuerry)

        #Set int value so python won't be angry about it
        self.conn = 123
        self.LoadSQLQueries(PREDEFINED_SQL_QUERIES)


    def AddToTab(self, tab, obj):
        tab.layout.addWidget(obj)

    def LoadSQLQueries(self, queries):

        counter = 0
        for query in queries:
            self.QueryList.addItem("Query no: " + str(counter), query)
            counter += 1

    def printSelectedQuery(self):

        final_s = ""

        for line in self.QueryList.itemData(self.QueryList.currentIndex()):
            final_s += line

        self.sql_qr_txt.setText(final_s)

    def compareQuerry(self):



        print(self.plans_list[self.aepList.currentIndex()])

        string = (get_diff(self.plans_list[0], self.plans_list[self.aepList.currentIndex()]))

        print(string)

        main = QVBoxLayout()



        layout = QHBoxLayout()

        layout1 = QHBoxLayout()

        w1 = QWebEngineView()


        fetch = self.plans_list[0]

        final_V2 = json_test.dumps(fetch)

        final_OBJ_TEST = json.loads(final_V2)

        head = parse_json(final_OBJ_TEST)

        diag_txt = generate_blockdiag(head)

        tree = parser.parse_string(diag_txt)

        diagram = builder.ScreenNodeBuilder.build(tree)

        draw = drawer.DiagramDraw('SVG', diagram)
        draw.draw()
        data = (draw.save())

        w1.setHtml(data)

        svg_bytes = bytearray(data, encoding='utf-8')

        renderer = QtSvg.QSvgRenderer(svg_bytes)

        w1.resize(renderer.viewBox().size())

        layout.addWidget(w1, 5)

        w3 = QTextEdit()

        w2 = QWebEngineView()

        fetch = self.plans_list[self.aepList.currentIndex() + 1]

        final_V2 = json_test.dumps(fetch)

        final_OBJ_TEST = json.loads(final_V2)

        head = parse_json(final_OBJ_TEST)

        diag_txt = generate_blockdiag(head)

        tree = parser.parse_string(diag_txt)

        diagram = builder.ScreenNodeBuilder.build(tree)

        draw = drawer.DiagramDraw('SVG', diagram)
        draw.draw()
        data = (draw.save())

        w2.setHtml(data)

        svg_bytes = bytearray(data, encoding='utf-8')

        renderer = QtSvg.QSvgRenderer(svg_bytes)

        w2.resize(renderer.viewBox().size())

        layout.addWidget(w2, 5)

        w3 = QTextEdit()

        w3.setMaximumHeight(200)

        w3.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        w3.setText(string)

        layout1.addWidget(w3, 10)

        main.addLayout(layout)
        main.addLayout(layout1, stretch=1)

        self.window = QWidget()

        self.window.setLayout(main)

        self.window.resize(renderer.viewBox().width() * 2, renderer.viewBox().height() * 1.5)

        main.setStretch(5, 1)
        self.window.show()


#SQL Connection
    def Sql_Inicalize_Conn(self):
        #print("Clicked!")

        try:
            self.ConnectToPostgreSQL()

            self.status_d.setText("Connected!")
            self.status_d.setStyleSheet("border: 1px solid green; color: green; font-weight: 600")
            self.sql_btn.setEnabled(True)
            self.LoadQuery.setEnabled(True)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)



#Execute SQL Command
    def Execute_SQL_Command(self):
       # try:

        self.FlushData()
        self.ConnectToPostgreSQL()

        QApplication.processEvents()

        self.tabWidget.removeTab(0) # //PyQT5 bug?

        QApplication.processEvents()

        tab_INFO = QtWidgets.QWidget()
        tab_INFO.layout = QVBoxLayout()

        tab_INFO_text = QLabel("START FETCHING PLANS \n It might freeze APP, wait!!")
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

        # if no join in QEP, shrink off and on config list
        if check_for_join(result):
            self.plans_list = generate_aqp(result, self.cursor,
                                                       postgreSQL_select_Query, self.conn, True)
        else:
            self.plans_list = generate_aqp(result, self.cursor,
                                                       postgreSQL_select_Query, self.conn, False)
        # For checking

        self.testList = self.plans_list.copy()
        self.plans_list = repackage_output(self.plans_list)


        self.tabWidget.removeTab(0)
        self.CleanUI()
        QApplication.processEvents()

        if(len(self.plans_list) > 1):
            self.aepList.setEnabled(True)
            self.CmpQuery.setEnabled(True)

        x = 0
        for SQL_STRING in self.plans_list:
            final_V2 = json_test.dumps(SQL_STRING)

            final_OBJ_TEST = json.loads(final_V2)
            descriptions = get_text(final_OBJ_TEST)

            result = ""
            for description in descriptions:
                result = result + description + "\n"

            print(result + " \n-----------------------------------")

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

            if x > 0:
                self.aepList.addItem("AEP " + str(x), self.testList[x])


            x += 1


        self.TerminateConnectionToPostgreSQL()


    #Display diagram button
    def displayDiagram(self, number):

        fetch = self.plans_list[number]

        final_V2 = json_test.dumps(fetch)

        final_OBJ_TEST = json.loads(final_V2)

        head = parse_json(final_OBJ_TEST)

        diag_txt = generate_blockdiag(head)

        tree = parser.parse_string(diag_txt)

        diagram = builder.ScreenNodeBuilder.build(tree)

        draw = drawer.DiagramDraw('SVG', diagram)
        draw.draw()
        data = (draw.save())


        self.webView = QWebEngineView()
        self.webView.setHtml(data)

        svg_bytes = bytearray(data,  encoding='utf-8')

        renderer = QtSvg.QSvgRenderer(svg_bytes)

        self.webView.resize(renderer.viewBox().size())


        self.webView.show()

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

        for x in range(0, self.aepList.count()):
            self.aepList.removeItem(x)

        QApplication.processEvents()

    def FlushData(self):

        self.plans_list_JSON = {}
        self.plans_list = {}

        self.CleanUI()



def MainGUILoop():

    #Enable error stack in PyQt5

    if QtCore.QT_VERSION >= 0x50501:
        def excepthook(type_, value, traceback_):
            traceback.print_exception(type_, value, traceback_)
            QtCore.qFatal('')

        sys.excepthook = excepthook

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UI_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

    app.exec()
