# -*- coding: utf-8 -*-
import env
from login import LoginPage
from PyQt4 import Qt, QtGui, QtCore
import sorttest

def createLabel(text):
    label = QtGui.QLabel(text)
    label.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
    return label

class Desktop(QtGui.QMainWindow):

    launch = QtCore.pyqtSignal()

    def __init__(self, dbconn, user):
        QtGui.QMainWindow.__init__(self)
        self.dbconn = dbconn
        self.user = user
        self.launch.connect(self.show)
        self.initFromDB()

        self.createToolBox()
        self.createAction()
        self.createMenu()
        self.createSystemTray()

        self.infoPanel = sorttest.Window()
        layout = QtGui.QVBoxLayout()
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.toolBox)
        mainLayout.addWidget(self.assetWidgets)
        layout.addLayout(mainLayout)
        layout.addWidget(self.infoPanel)

        self.centralWidget = QtGui.QWidget()
        self.centralWidget.setLayout(layout)
        self.setCentralWidget(self.centralWidget)
        self.resize(800, 600)
        self.setWindowTitle(u'固定收益部交易管理平台 - {0}'.format(self.user.name))
        self.setWindowIcon(QtGui.QIcon(env.sysIcon))

        self.statusBar().showMessage(u'准备就绪')
        self.login = LoginPage(self.dbconn)

    def initFromDB(self):
        self.books = env.LoadBooks(self.dbconn)

    def createMenu(self):
        self.mb = self.menuBar()
        m1 = self.mb.addMenu(u'&系统')
        m1.addAction(self.exitAction)

        m2 = self.mb.addMenu(u'&交易')
        m2.addAction(self.tradeBond)

        m3 = self.mb.addMenu(u'&帮助')
        m3.addAction(self.aboutAction)

    def createAction(self):
        self.exitAction = QtGui.QAction(QtGui.QIcon(r'icons\exit.png'), u'退出', self, triggered=QtGui.qApp.quit)
        self.tradeBond = QtGui.QAction(u'债券', self, shortcut='Ctrl+T')
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
        self.trayIcon.setIcon(QtGui.QIcon(env.sysIcon))
        self.trayIcon.activated.connect(self.iconActivated)
        self.trayIcon.show()

    def createWidgets(self):

        self.centralWidget = QtGui.QWidget()
        self.infoWidget = QtGui.QWidget()
        self.infoWidget.setWindowTitle(u'交易信息')
        self.mainPanel = QtGui.QWidget()
        self.mainPanel.setWindowTitle(u'主面板')

        self.bookList = QtGui.QComboBox()
        self.bookList.setEditable(False)
        self.bookList.addItems([b.name_cn_short for b in self.books])
        self.bookLabel = QtGui.QLabel(u'账簿')
        self.bookLayout = QtGui.QHBoxLayout()
        self.bookLayout.addWidget(self.bookLabel)
        self.bookLayout.addWidget(self.bookList)

    def setupLayout(self):
        self.setCentralWidget(self.centralWidget)
        self.layout = QtGui.QVBoxLayout()
        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(self.toolBox)
        self.mainLayout.addWidget(self.mainPanel)
        self.mainPanel.setLayout(self.bookLayout)
        self.layout.addLayout(self.mainLayout)
        self.layout.addWidget(self.infoWidget)
        self.centralWidget.setLayout(self.layout)

    def iconActivated(self, reason):
        if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick):
            self.showNormal()

    def closeEvent(self, event):
        if self.trayIcon.isVisible():
            QtGui.QMessageBox.information(self, u"最小化",
                    u"系统将最小化至系统托盘，如果退出请选择“系统->退出”")
            self.hide()
            event.ignore()

    def about(self):
         QtGui.QMessageBox.about(self, u"关于CAMP", u"长安信托固定收益部交易管理平台")

    def createToolBox(self):
        assetWidget = QtGui.QWidget()
        self.createAssetButtons()
        assetLayout = QtGui.QVBoxLayout()
        assetLayout.addWidget(self.assetBtns)
        assetWidget.setLayout(assetLayout)

        liabilityWidget = QtGui.QWidget()
        creditWidget = QtGui.QWidget()
        riskWidget = QtGui.QWidget()
        self.toolBox = QtGui.QToolBox()
        self.toolBox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored))
        self.toolBox.setMinimumWidth(assetWidget.sizeHint().width())
        self.toolBox.addItem(assetWidget, u"资产")
        self.toolBox.addItem(liabilityWidget, u"负债")
        self.toolBox.addItem(creditWidget, u'信用研究')
        self.toolBox.addItem(riskWidget, u'风险控制')

        #p = self.toolBox.palette()
        #p.setColor(self.toolBox.backgroundRole(), QtGui.QColor('grey'))
        #self.toolBox.setPalette(p)

    def createAssetButtons(self):
        self.assetBtns = QtGui.QListWidget()
        self.assetBtns.setViewMode(QtGui.QListView.IconMode)
        self.assetBtns.setIconSize(QtCore.QSize(32, 28))
        self.assetBtns.setMovement(QtGui.QListView.Static)
        self.assetBtns.setMaximumWidth(80)
        self.assetBtns.setSpacing(12)
        self.assetBtns.setCurrentRow(0)

        overview = QtGui.QListWidgetItem(self.assetBtns)
        overview.setIcon(QtGui.QIcon('icons/global.png'))
        overview.setText(u"账户总览")
        overview.setTextAlignment(QtCore.Qt.AlignHCenter)
        overview.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        overview = QtGui.QListWidgetItem(self.assetBtns)
        overview.setIcon(QtGui.QIcon('icons/items.png'))
        overview.setText(u"交易记录")
        overview.setTextAlignment(QtCore.Qt.AlignHCenter)
        overview.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.assetWidgets = QtGui.QStackedWidget()
        self.assetWidgets.addWidget(AssetOverviewPage())
        self.assetWidgets.addWidget(TradeDetailsPage())

        self.assetBtns.currentItemChanged.connect(self.changePage)

    def changePage(self, current, previous):
        if not current:
            current = previous
        self.assetWidgets.setCurrentIndex(self.assetBtns.row(current))

class AssetOverviewPage(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel(u'资产概览'))
        self.setLayout(layout)

class TradeDetailsPage(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel(u'交易明细'))
        self.setLayout(layout)