# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainformbNthZy.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSplitter, QStackedWidget, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1170, 826)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, 3, 0)
        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(4, -1, 4, 0)
        self.header = QWidget(self.widget_2)
        self.header.setObjectName(u"header")
        self.header.setMaximumSize(QSize(16777215, 32))

        self.verticalLayout_2.addWidget(self.header)

        self.splitter = QSplitter(self.widget_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(240, 0))
        self.widget.setMaximumSize(QSize(280, 16777215))
        self.widget.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0.499096, y1:1, x2:0.487062, y2:0, stop:0 rgba(49, 49, 49, 255), stop:1 rgba(38, 38, 38, 255));")
        self.verticalLayout_6 = QVBoxLayout(self.widget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.systeminfoswidget = QWidget(self.widget)
        self.systeminfoswidget.setObjectName(u"systeminfoswidget")
        self.systeminfoswidget.setStyleSheet(u"border: 2px solid #555;\n"
"border-radius:10px;\n"
"background-color:transparent;")

        self.verticalLayout_6.addWidget(self.systeminfoswidget)

        self.group_nav = QWidget(self.widget)
        self.group_nav.setObjectName(u"group_nav")
        self.verticalLayout = QVBoxLayout(self.group_nav)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(12, -1, 12, -1)
        self.btnNavClean = QPushButton(self.group_nav)
        self.btnNavClean.setObjectName(u"btnNavClean")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnNavClean.sizePolicy().hasHeightForWidth())
        self.btnNavClean.setSizePolicy(sizePolicy)
        self.btnNavClean.setMinimumSize(QSize(0, 58))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.btnNavClean.setFont(font)
        self.btnNavClean.setStyleSheet(u"QPushButton {\n"
"    background-color: #4a4a4a;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #3c3c3c;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"\n"
"/* quand le bouton est press\u00e9 */\n"
"QPushButton:pressed {\n"
"    background-color: #055a8a;\n"
"}\n"
"")

        self.verticalLayout.addWidget(self.btnNavClean)

        self.btnNavDisk = QPushButton(self.group_nav)
        self.btnNavDisk.setObjectName(u"btnNavDisk")
        self.btnNavDisk.setMinimumSize(QSize(0, 58))
        self.btnNavDisk.setFont(font)
        self.btnNavDisk.setStyleSheet(u"QPushButton {\n"
"    background-color: #4a4a4a;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #3c3c3c;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"\n"
"/* quand le bouton est press\u00e9 */\n"
"QPushButton:pressed {\n"
"    background-color: #055a8a;\n"
"}\n"
"")

        self.verticalLayout.addWidget(self.btnNavDisk)

        self.btnNavStart = QPushButton(self.group_nav)
        self.btnNavStart.setObjectName(u"btnNavStart")
        self.btnNavStart.setMinimumSize(QSize(0, 58))
        self.btnNavStart.setFont(font)
        self.btnNavStart.setStyleSheet(u"QPushButton {\n"
"    background-color: #4a4a4a;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #3c3c3c;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"\n"
"/* quand le bouton est press\u00e9 */\n"
"QPushButton:pressed {\n"
"    background-color: #055a8a;\n"
"}\n"
"")

        self.verticalLayout.addWidget(self.btnNavStart)

        self.btnNavWin = QPushButton(self.group_nav)
        self.btnNavWin.setObjectName(u"btnNavWin")
        self.btnNavWin.setMinimumSize(QSize(0, 58))
        self.btnNavWin.setFont(font)
        self.btnNavWin.setStyleSheet(u"QPushButton {\n"
"    background-color: #4a4a4a;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #3c3c3c;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"\n"
"/* quand le bouton est press\u00e9 */\n"
"QPushButton:pressed {\n"
"    background-color: #055a8a;\n"
"}\n"
"")

        self.verticalLayout.addWidget(self.btnNavWin)


        self.verticalLayout_6.addWidget(self.group_nav)

        self.statsinfoswidget = QWidget(self.widget)
        self.statsinfoswidget.setObjectName(u"statsinfoswidget")
        self.statsinfoswidget.setStyleSheet(u"border: 2px solid #555;\n"
"border-radius:10px;\n"
"background-color:transparent;")

        self.verticalLayout_6.addWidget(self.statsinfoswidget)

        self.splitter.addWidget(self.widget)
        self.widget_3 = QWidget(self.splitter)
        self.widget_3.setObjectName(u"widget_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy1)
        self.widget_3.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0.499096, y1:1, x2:0.487062, y2:0, stop:0 rgba(49, 49, 49, 255), stop:1 rgba(38, 38, 38, 255));")
        self.verticalLayout_3 = QVBoxLayout(self.widget_3)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, -1, 0, 0)
        self.stackedWidget = QStackedWidget(self.widget_3)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setFrameShadow(QFrame.Shadow.Plain)
        self.win_page = QWidget()
        self.win_page.setObjectName(u"win_page")
        self.stackedWidget.addWidget(self.win_page)
        self.cleaner_page = QWidget()
        self.cleaner_page.setObjectName(u"cleaner_page")
        self.verticalLayout_4 = QVBoxLayout(self.cleaner_page)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.widget_9 = QWidget(self.cleaner_page)
        self.widget_9.setObjectName(u"widget_9")
        self.widget_9.setMaximumSize(QSize(16777215, 36))
        self.widget_9.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0.499096, y1:1, x2:0.487062, y2:0, stop:0 rgba(49, 49, 49, 255), stop:1 rgba(38, 38, 38, 255));\n"
"color:white;")
        self.lblTitreNav = QLabel(self.widget_9)
        self.lblTitreNav.setObjectName(u"lblTitreNav")
        self.lblTitreNav.setGeometry(QRect(30, 0, 271, 20))
        font1 = QFont()
        font1.setPointSize(11)
        font1.setBold(False)
        self.lblTitreNav.setFont(font1)
        self.lblTitreNav.setStyleSheet(u"background-color:transparent;")

        self.verticalLayout_4.addWidget(self.widget_9)

        self.widget_5 = QWidget(self.cleaner_page)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setMinimumSize(QSize(0, 80))
        self.widget_5.setMaximumSize(QSize(16777215, 80))
        self.widget_5.setStyleSheet(u"border: 1px solid #c8c8c8;\n"
"border-radius: 16px;")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.btnScan = QPushButton(self.widget_5)
        self.btnScan.setObjectName(u"btnScan")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btnScan.sizePolicy().hasHeightForWidth())
        self.btnScan.setSizePolicy(sizePolicy2)
        self.btnScan.setMinimumSize(QSize(0, 0))
        self.btnScan.setFont(font)
        self.btnScan.setStyleSheet(u"QPushButton {\n"
"    background-color: #0080d5;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #0763ac;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"\n"
"/* quand le bouton est press\u00e9 */\n"
"QPushButton:pressed {\n"
"    background-color: #055a8a;\n"
"}\n"
"")

        self.horizontalLayout_4.addWidget(self.btnScan)

        self.btnSelectAll = QPushButton(self.widget_5)
        self.btnSelectAll.setObjectName(u"btnSelectAll")
        sizePolicy2.setHeightForWidth(self.btnSelectAll.sizePolicy().hasHeightForWidth())
        self.btnSelectAll.setSizePolicy(sizePolicy2)
        self.btnSelectAll.setMinimumSize(QSize(0, 0))
        self.btnSelectAll.setFont(font)
        self.btnSelectAll.setStyleSheet(u"QPushButton {\n"
"    background-color: #4a4a4a;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #3c3c3c;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"")

        self.horizontalLayout_4.addWidget(self.btnSelectAll)

        self.btnUnSelectAll = QPushButton(self.widget_5)
        self.btnUnSelectAll.setObjectName(u"btnUnSelectAll")
        sizePolicy2.setHeightForWidth(self.btnUnSelectAll.sizePolicy().hasHeightForWidth())
        self.btnUnSelectAll.setSizePolicy(sizePolicy2)
        self.btnUnSelectAll.setMinimumSize(QSize(0, 0))
        self.btnUnSelectAll.setFont(font)
        self.btnUnSelectAll.setStyleSheet(u"QPushButton {\n"
"    background-color: #4a4a4a;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #3c3c3c;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"")

        self.horizontalLayout_4.addWidget(self.btnUnSelectAll)

        self.btnClean = QPushButton(self.widget_5)
        self.btnClean.setObjectName(u"btnClean")
        sizePolicy2.setHeightForWidth(self.btnClean.sizePolicy().hasHeightForWidth())
        self.btnClean.setSizePolicy(sizePolicy2)
        self.btnClean.setMinimumSize(QSize(0, 0))
        self.btnClean.setFont(font)
        self.btnClean.setStyleSheet(u"QPushButton {\n"
"    background-color: #e99f9F;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #6a6a6a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #e88f8F;\n"
"}\n"
"\n"
"\n"
"/* quand le bouton est press\u00e9 */\n"
"QPushButton:pressed {\n"
"    background-color: #e99f8F;\n"
"}\n"
"")

        self.horizontalLayout_4.addWidget(self.btnClean)


        self.verticalLayout_4.addWidget(self.widget_5)

        self.widget_8 = QWidget(self.cleaner_page)
        self.widget_8.setObjectName(u"widget_8")
        self.widget_8.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0.499096, y1:1, x2:0.487062, y2:0, stop:0 rgba(49, 49, 49, 255), stop:1 rgba(38, 38, 38, 255));")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_8)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.widget_6 = QWidget(self.widget_8)
        self.widget_6.setObjectName(u"widget_6")
        self.widget_6.setMaximumSize(QSize(300, 16777215))
        self.widget_6.setStyleSheet(u"border: 1px solid #c8c8c8;\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0.114155 rgba(225, 225, 225, 255), stop:0.488584 rgba(194, 194, 194, 255), stop:0.863014 rgba(225, 225, 225, 255));\n"
"border-radius: 16px;")

        self.horizontalLayout_3.addWidget(self.widget_6)

        self.widget_7 = QWidget(self.widget_8)
        self.widget_7.setObjectName(u"widget_7")
        self.widget_7.setStyleSheet(u"border: 1px solid #c8c8c8;\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0.114155 rgba(225, 225, 225, 255), stop:0.488584 rgba(194, 194, 194, 255), stop:0.863014 rgba(225, 225, 225, 255));\n"
"border-radius: 16px;")

        self.horizontalLayout_3.addWidget(self.widget_7)


        self.verticalLayout_4.addWidget(self.widget_8)

        self.stackedWidget.addWidget(self.cleaner_page)
        self.disk_page = QWidget()
        self.disk_page.setObjectName(u"disk_page")
        self.widget_11 = QWidget(self.disk_page)
        self.widget_11.setObjectName(u"widget_11")
        self.widget_11.setGeometry(QRect(10, 50, 886, 80))
        self.widget_11.setMinimumSize(QSize(0, 80))
        self.widget_11.setMaximumSize(QSize(16777215, 80))
        self.widget_11.setStyleSheet(u"border: 1px solid #c8c8c8;\n"
"border-radius: 16px;")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_11)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.btnScan_2 = QPushButton(self.widget_11)
        self.btnScan_2.setObjectName(u"btnScan_2")
        sizePolicy2.setHeightForWidth(self.btnScan_2.sizePolicy().hasHeightForWidth())
        self.btnScan_2.setSizePolicy(sizePolicy2)
        self.btnScan_2.setMinimumSize(QSize(0, 0))
        self.btnScan_2.setFont(font)
        self.btnScan_2.setStyleSheet(u"QPushButton {\n"
"    background-color: #0080d5;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #0763ac;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"\n"
"/* quand le bouton est press\u00e9 */\n"
"QPushButton:pressed {\n"
"    background-color: #055a8a;\n"
"}\n"
"")

        self.horizontalLayout_5.addWidget(self.btnScan_2)

        self.btnSelectAll_2 = QPushButton(self.widget_11)
        self.btnSelectAll_2.setObjectName(u"btnSelectAll_2")
        sizePolicy2.setHeightForWidth(self.btnSelectAll_2.sizePolicy().hasHeightForWidth())
        self.btnSelectAll_2.setSizePolicy(sizePolicy2)
        self.btnSelectAll_2.setMinimumSize(QSize(0, 0))
        self.btnSelectAll_2.setFont(font)
        self.btnSelectAll_2.setStyleSheet(u"QPushButton {\n"
"    background-color: #4a4a4a;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #3c3c3c;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"")

        self.horizontalLayout_5.addWidget(self.btnSelectAll_2)

        self.btnUnSelectAll_2 = QPushButton(self.widget_11)
        self.btnUnSelectAll_2.setObjectName(u"btnUnSelectAll_2")
        sizePolicy2.setHeightForWidth(self.btnUnSelectAll_2.sizePolicy().hasHeightForWidth())
        self.btnUnSelectAll_2.setSizePolicy(sizePolicy2)
        self.btnUnSelectAll_2.setMinimumSize(QSize(0, 0))
        self.btnUnSelectAll_2.setFont(font)
        self.btnUnSelectAll_2.setStyleSheet(u"QPushButton {\n"
"    background-color: #4a4a4a;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #3a3a3a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #3c3c3c;\n"
"}\n"
"\n"
"/* quand le bouton est actif (v\u00e9rifi\u00e9, checkable) */\n"
"QPushButton:checked {\n"
"    background-color: #0763ac;      /* bleu actif */\n"
"    color: white;\n"
"    border: 2px solid #0a7ad6;\n"
"}\n"
"")

        self.horizontalLayout_5.addWidget(self.btnUnSelectAll_2)

        self.btnClean_2 = QPushButton(self.widget_11)
        self.btnClean_2.setObjectName(u"btnClean_2")
        sizePolicy2.setHeightForWidth(self.btnClean_2.sizePolicy().hasHeightForWidth())
        self.btnClean_2.setSizePolicy(sizePolicy2)
        self.btnClean_2.setMinimumSize(QSize(0, 0))
        self.btnClean_2.setFont(font)
        self.btnClean_2.setStyleSheet(u"QPushButton {\n"
"    background-color: #e99f9F;      /* gris fonc\u00e9 par d\u00e9faut */\n"
"    color: #dddddd;                 /* texte clair */\n"
"    border: 2px solid #6a6a6a;\n"
"    border-radius: 10px;\n"
"    padding: 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* quand le bouton est survol\u00e9 */\n"
"QPushButton:hover {\n"
"    background-color: #e88f8F;\n"
"}\n"
"\n"
"\n"
"/* quand le bouton est press\u00e9 */\n"
"QPushButton:pressed {\n"
"    background-color: #e99f8F;\n"
"}\n"
"")

        self.horizontalLayout_5.addWidget(self.btnClean_2)

        self.stackedWidget.addWidget(self.disk_page)
        self.start_page = QWidget()
        self.start_page.setObjectName(u"start_page")
        self.stackedWidget.addWidget(self.start_page)

        self.verticalLayout_3.addWidget(self.stackedWidget)

        self.splitter.addWidget(self.widget_3)

        self.verticalLayout_2.addWidget(self.splitter)

        self.statuswidget = QWidget(self.widget_2)
        self.statuswidget.setObjectName(u"statuswidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.statuswidget.sizePolicy().hasHeightForWidth())
        self.statuswidget.setSizePolicy(sizePolicy3)
        self.statuswidget.setMinimumSize(QSize(0, 0))
        self.statuswidget.setMaximumSize(QSize(16777215, 50))
        self.statuswidget.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0.499096, y1:1, x2:0.487062, y2:0, stop:0 rgba(49, 49, 49, 255), stop:1 rgba(38, 38, 38, 255));\n"
"color:#f5f5f5;")
        self.horizontalLayout = QHBoxLayout(self.statuswidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lblStatus = QLabel(self.statuswidget)
        self.lblStatus.setObjectName(u"lblStatus")
        self.lblStatus.setStyleSheet(u"background:transparent;\n"
"border:1px solid #ccc;\n"
"border-radius: 6px;\n"
"padding: 0 10px;")

        self.horizontalLayout.addWidget(self.lblStatus)

        self.lblStatus1 = QLabel(self.statuswidget)
        self.lblStatus1.setObjectName(u"lblStatus1")
        self.lblStatus1.setStyleSheet(u"background:transparent;")
        self.lblStatus1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.lblStatus1)

        self.lblStatus2 = QLabel(self.statuswidget)
        self.lblStatus2.setObjectName(u"lblStatus2")
        self.lblStatus2.setStyleSheet(u"background:transparent;")
        self.lblStatus2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.lblStatus2)


        self.verticalLayout_2.addWidget(self.statuswidget)


        self.horizontalLayout_2.addWidget(self.widget_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1170, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btnNavClean.setText(QCoreApplication.translate("MainWindow", u"Nettoyage", None))
        self.btnNavDisk.setText(QCoreApplication.translate("MainWindow", u"Analyse Disque", None))
        self.btnNavStart.setText(QCoreApplication.translate("MainWindow", u"D\u00e9marrage", None))
        self.btnNavWin.setText(QCoreApplication.translate("MainWindow", u"Windows", None))
        self.lblTitreNav.setText(QCoreApplication.translate("MainWindow", u"Nettoyage", None))
        self.btnScan.setText(QCoreApplication.translate("MainWindow", u"Lancer le scan", None))
        self.btnSelectAll.setText(QCoreApplication.translate("MainWindow", u"Tout s\u00e9lectionner", None))
        self.btnUnSelectAll.setText(QCoreApplication.translate("MainWindow", u"Tout d\u00e9s\u00e9lectionner", None))
        self.btnClean.setText(QCoreApplication.translate("MainWindow", u"Nettoyer", None))
        self.btnScan_2.setText(QCoreApplication.translate("MainWindow", u"Lancer le scan", None))
        self.btnSelectAll_2.setText(QCoreApplication.translate("MainWindow", u"Tout s\u00e9lectionner", None))
        self.btnUnSelectAll_2.setText(QCoreApplication.translate("MainWindow", u"Tout d\u00e9s\u00e9lectionner", None))
        self.btnClean_2.setText(QCoreApplication.translate("MainWindow", u"Nettoyer", None))
        self.lblStatus.setText(QCoreApplication.translate("MainWindow", u"Pr\u00eat", None))
        self.lblStatus1.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lblStatus2.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

