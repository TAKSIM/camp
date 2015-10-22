# -*- coding: utf-8 -*-
import env
from login import LoginPage
from PyQt4 import QtGui, QtCore

class Desktop(QtGui.QMainWindow):

    launch = QtCore.pyqtSignal()

    def __init__(self, dbconn):
        QtGui.QMainWindow.__init__(self)
        self.dbconn = dbconn
        self.launch.connect(self.show)
        self.initFromDB()

        self.BuildAssetWidget() # asset widget
        self.BuildLiabilityWidget() # liability widget

        self.createToolBox()
        self.createAction()
        self.createMenu()
        self.createSystemTray()

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.toolBox)
        layout.addWidget(self.aw)
        layout.addWidget(self.lw)
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(layout)

        self.resize(800, 600)
        self.setWindowTitle(u'CAMP - 固定收益部交易管理平台')
        self.setWindowIcon(QtGui.QIcon(r'icons\todo.png'))

        self.statusBar().showMessage(u'准备就绪')

        self.login = LoginPage(dbconn)

    def initFromDB(self):
        self.books = env.LoadBooks(self.dbconn)

    def createMenu(self):
        self.mb = self.menuBar()
        m1 = self.mb.addMenu(u'&系统')
        m1.addAction(self.exitAction)

        m2 = self.mb.addMenu(u'&交易')
        m2.addAction(self.tradeBond)

        m3 = self.mb.addMenu(u'&显示')
        m3.addAction(self.showAsset)
        m3.addAction(self.showLiability)

        m4 = self.mb.addMenu(u'&帮助')
        m4.addAction(self.aboutAction)

    def createAction(self):
        self.exitAction = QtGui.QAction(QtGui.QIcon(r'icons\exit.png'), u'退出', self, triggered=QtGui.qApp.quit)
        self.tradeBond = QtGui.QAction(u'债券', self, shortcut='Ctrl+T')
        self.showAsset = QtGui.QAction(u'显示资产表', self, shortcut='Ctrl+A', triggered=self.aw.show)
        self.showLiability = QtGui.QAction(u'显示负债表', self, shortcut='Ctrl+L', triggered=self.lw.show)
        self.aboutAction = QtGui.QAction(u"关于CAMP", self, triggered=self.about)

        self.minimize = QtGui.QAction(u'最小化', self, triggered=self.hide)
        self.maximize = QtGui.QAction(u'最大化',self, triggered=self.showMaximized)
        self.restore = QtGui.QAction(u'还原', self, triggered=self.showNormal)

    def createSystemTray(self):
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.minimize)
        self.trayIconMenu.addAction(self.maximize)
        self.trayIconMenu.addAction(self.restore)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.exitAction)
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QtGui.QIcon('icon/systray.png'))
        self.trayIcon.activated.connect(self.iconActivated)
        self.trayIcon.show()

    def iconActivated(self, reason):
        if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick):
            self.showNormal()

    def closeEvent(self, event):
        if self.trayIcon.isVisible():
            QtGui.QMessageBox.information(self, "Systray",
                    "The program will keep running in the system tray. To "
                    "terminate the program, choose <b>Quit</b> in the "
                    "context menu of the system tray entry.")
            self.hide()
            event.ignore()

    def about(self):
         QtGui.QMessageBox.about(self, u"关于CAMP", u"长安信托固定收益部交易管理平台")

    def BuildAssetWidget(self):
        self.aw = QtGui.QDockWidget(u'资产',self)
        self.aw.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        #self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,w)

    def BuildLiabilityWidget(self):
        self.lw = QtGui.QDockWidget(u'负债',self)
        self.lw.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea,w)

    def createToolBox(self):
        assetWidget = QtGui.QWidget()
        alayout = QtGui.QHBoxLayout()

        bookLayout = QtGui.QHBoxLayout()
        bookLayout.addWidget(QtGui.QLabel(u'帐簿'))
        bookList = QtGui.QComboBox()
        bookList.setEditable(False)
        bookList.addItems([b.name_cn_short for b in self.books])
        bookLayout.addWidget(bookList)

        alayout.addLayout(bookLayout)
        assetWidget.setLayout(alayout)

        liabilityWidget = QtGui.QWidget()
        self.toolBox = QtGui.QToolBox()
        self.toolBox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored))
        self.toolBox.setMinimumWidth(assetWidget.sizeHint().width())
        self.toolBox.addItem(assetWidget, u"资产")
        self.toolBox.addItem(liabilityWidget, u"负债")
