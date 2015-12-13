# -*- coding: utf-8 -*-
from login import LoginPage
import env
from inst.lifecycle import Book, Deal
from PyQt4 import Qt, QtGui, QtCore, QtSql
import sorttest
from WindPy import *

def createLabel(text):
    label = QtGui.QLabel(text)
    label.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
    return label

class Desktop(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.initDB()
        login = LoginPage()
        if login.exec_():
            self.user = env.User(str(login.username.text()))
            self.initFromDB()

            self.createToolBox()
            self.createAction()
            self.createMenu()
            self.createSystemTray()

            self.msgPanel = sorttest.Window()
            layout = QtGui.QVBoxLayout()
            mainLayout = QtGui.QHBoxLayout()
            mainLayout.addWidget(self.toolBox)
            self.panel = QtGui.QWidget()
            self.layoutOverview = self.createOverviewLayout()
            self.panel.setLayout(self.layoutOverview)

            mainLayout.addWidget(self.panel)
            layout.addLayout(mainLayout)
            layout.addWidget(self.msgPanel)

            self.centralWidget = QtGui.QWidget()
            self.centralWidget.setLayout(layout)
            self.setCentralWidget(self.centralWidget)
            self.resize(800, 600)
            self.setWindowTitle(u'固定收益部交易管理平台 - {0}'.format(self.user.name))
            self.setWindowIcon(QtGui.QIcon(env.sysIcon))

            self.show()
            self.statusBar().showMessage(u'启动万得链接')
            w.start()
            self.statusBar().showMessage(u'准备就绪')
        else:
            QtGui.qApp.quit()

    def initDB(self, host='caitcfid.mysql.rds.aliyuncs.com', port=3306, dbname='secs'):
        self.db = QtSql.QSqlDatabase.addDatabase('QMYSQL')
        self.db.setHostName(host)
        self.db.setPort(port)
        self.db.setDatabaseName(dbname)
        self.db.setUserName('hewei')
        self.db.setPassword('wehea1984')
        if not self.db.open():
            raise Exception(u'无法连接数据库')

    def initFromDB(self):
        self.loadBooks()
        self.loadDeals()
        self.loadHolidays()

    def loadBooks(self):
        self.books = []
        q = QtSql.QSqlQuery()
        q.exec_('SELECT * FROM BOOKS')
        while q.next():
            self.books.append(Book(q.value(0).toInt()[0],
                                   q.value(1).toString(),
                                   q.value(2).toString(),
                                   q.value(3).toString(),
                                   q.value(4).toDate()))

    def loadDeals(self):
        q = QtSql.QSqlQuery()
        self.deals = []
        q.exec_('SELECT * FROM DEALS')
        while q.next():
            d = str(q.value(0).toString())
            b = q.value(1).toInt()[0]
            self.deals.append(Deal(d, b))

    def loadHolidays(self):
        q = QtSql.QSqlQuery()
        self.hols = []
        q.exec_(u"'SELECT HOLDATE FROM HOLIDAYS WHERE HOLSTATUS<>'工作'")
        while q.next():
            self.hols.append(q.value(0).toDate().toPyDate())
        self.workdays=[]
        q.exec_(u"'SELECT HOLDATE FROM HOLIDAYS WHERE HOLSTATUS='工作'")
        while q.next():
            self.workdays.append(q.value(0).toDate().toPyDate())

    def createMenu(self):
        self.mb = self.menuBar()
        m1 = self.mb.addMenu(u'&系统')
        m1.addAction(self.holAction)
        m1.addAction(self.refreshAction)
        m1.addAction(self.exitAction)

        m2 = self.mb.addMenu(u'&交易')
        m2.addAction(self.tradeBond)
        m2.addAction(self.tradeDepo)
        m2.addAction(self.tradeMmf)

        m3 = self.mb.addMenu(u'&帮助')
        m3.addAction(self.aboutAction)

    def createAction(self):
        self.exitAction = QtGui.QAction(QtGui.QIcon(r'icons\exit.png'), u'退出', self, triggered=QtGui.qApp.quit)
        self.refreshAction = QtGui.QAction(QtGui.QIcon(r'icons\refresh.png'), u'刷新', self, triggered=self.refresh, shortcut='F5')
        self.holAction = QtGui.QAction(QtGui.QIcon(r'icons\settings.png'), u'假期设置', self, shortcut='Ctrl+H', triggered=self.showHolidayPanel)

        self.tradeBond = QtGui.QAction(u'债券', self, shortcut='Ctrl+B', triggered=self.showBondPanel)
        self.tradeDepo = QtGui.QAction(u'同业存款', self, shortcut='Ctrl+D', triggered=self.showDepoPanel)
        self.tradeMmf = QtGui.QAction(u'货币基金', self, shortcut='Ctrl+M', triggered=self.showMmfPanel)

        self.aboutAction = QtGui.QAction(u"关于CAMP", self, triggered=self.about)

        self.minimize = QtGui.QAction(u'最小化', self, triggered=self.hide)
        self.maximize = QtGui.QAction(u'最大化',self, triggered=self.showMaximized)
        self.restore = QtGui.QAction(u'还原', self, triggered=self.showNormal)

    def showDepoPanel(self):
        import tradepanel
        depo = tradepanel.DepoPanel(self.user, self.books)
        if depo.exec_():
            pass

    def showBondPanel(self):
        import tradepanel
        bond = tradepanel.BondPanel(self.books)
        if bond.exec_():
            pass

    def showMmfPanel(self):
        import tradepanel
        mmf = tradepanel.MmfPanel(self.books)
        if mmf.exec_():
            pass

    def showHolidayPanel(self):
        import tradepanel
        hol = tradepanel.HolidayPanel()
        if hol.exec_():
            pass

    def refresh(self):
        self.eventModel.query().exec_()

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
            # QtGui.QMessageBox.information(self, u"最小化",
            #         u"系统将最小化至系统托盘，如果退出请选择“系统->退出”")
            self.hide()
            event.ignore()

    def about(self):
         QtGui.QMessageBox.about(self, u"关于CAMP", u"长安信托固定收益部交易管理平台")

    def createToolBox(self):
        assetWidget = QtGui.QWidget()
        assetLayout = self.createAssetButtons()
        assetWidget.setLayout(assetLayout)

        liabilityWidget = QtGui.QWidget()
        liabilityLayout = self.createLiabilityButtons()
        liabilityWidget.setLayout(liabilityLayout)

        creditWidget = QtGui.QWidget()
        riskWidget = QtGui.QWidget()
        self.toolBox = QtGui.QToolBox()
        #self.toolBox.setFixedWidth(120)
        self.toolBox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored))
        self.toolBox.setMinimumWidth(assetWidget.sizeHint().width())
        self.toolBox.addItem(assetWidget, u'  资    产')
        self.toolBox.addItem(liabilityWidget, u"  负    债")
        self.toolBox.addItem(creditWidget, u'  信用研究')
        self.toolBox.addItem(riskWidget, u'  风险控制')

    def createLiabilityButtons(self):
        layout = QtGui.QGridLayout()
        self.btLiability = QtGui.QToolButton()
        self.btLiability.setToolButtonStyle(3)
        self.btLiability.setText(u'申购明细')
        self.btLiability.setIcon(QtGui.QIcon('icons/note.png'))
        self.btLiability.setIconSize(Qt.QSize(32,28))
        layout.addWidget(self.btLiability,0,0,1,1)
        return layout

    def createAssetButtons(self):
        layout = QtGui.QGridLayout()
        self.btOverview = QtGui.QToolButton()
        self.btOverview.setToolButtonStyle(3)
        self.btOverview.setIcon(QtGui.QIcon('icons/global'))
        self.btOverview.setText(u'账户总览')
        self.btOverview.setIconSize(Qt.QSize(32,28))
        layout.addWidget(self.btOverview,0,0,1,1)

        self.btTrades = QtGui.QToolButton()
        self.btTrades.setToolButtonStyle(3)
        self.btTrades.setIcon(QtGui.QIcon('icons/items'))
        self.btTrades.setText(u'交易明细')
        self.btTrades.setIconSize(Qt.QSize(32,28))
        layout.addWidget(self.btTrades,1,0,1,1)
        return layout

    def createOverviewLayout(self):
        layout = QtGui.QVBoxLayout()

        self.gbFilter = QtGui.QGroupBox(u'筛选条件')
        layoutFilter = QtGui.QHBoxLayout()
        layoutFilter.setAlignment(QtCore.Qt.AlignLeft)
        # book filter
        layoutBooks = QtGui.QHBoxLayout()
        layoutBooks.addWidget(QtGui.QLabel(u'账簿'))
        dbBooks = QtGui.QComboBox()
        dbBooks.addItems([b.name_cn_short for b in self.books])
        layoutBooks.addWidget(dbBooks)
        layoutFilter.addLayout(layoutBooks)
        # show expired trades
        showExpTrds = QtGui.QCheckBox(u'显示已平仓的交易')
        showExpTrds.setChecked(False)
        layoutFilter.addWidget(showExpTrds)

        self.gbFilter.setLayout(layoutFilter)
        layout.addWidget(self.gbFilter)

        self.actView = QtGui.QTableView()
        self.eventModel = QtSql.QSqlQueryModel()
        self.eventModel.setQuery('SELECT INST_ID, EVENT_TYPE, REF_AMOUNT, REF_YIELD, COMMENT, SIGNER, TIME_STAMP FROM EVENTS')
        self.actView.setModel(self.eventModel)
        self.eventModel.setHeaderData(0, QtCore.Qt.Horizontal, u'代码')
        self.eventModel.setHeaderData(1, QtCore.Qt.Horizontal, u'类型')
        self.eventModel.setHeaderData(2, QtCore.Qt.Horizontal, u'金额')
        self.eventModel.setHeaderData(3, QtCore.Qt.Horizontal, u'收益率')
        self.eventModel.setHeaderData(4, QtCore.Qt.Horizontal, u'备注')
        self.eventModel.setHeaderData(5, QtCore.Qt.Horizontal, u'用户')
        self.eventModel.setHeaderData(6, QtCore.Qt.Horizontal, u'时间')
        self.actView.resizeColumnsToContents()
        self.actView.resizeRowsToContents()
        self.actView.verticalHeader().hide()
        # self.actView.setColumnCount(5)
        # self.actView.setHorizontalHeaderLabels([u'仓位',u'数量',u'买/卖',u'开仓价格',u'到期收益率'])
        # self.actView.resizeColumnsToContents()
        # self.actView.resizeRowsToContents()

        layout.addWidget(self.actView)
        return layout

    def changeAssetPage(self, current, previous):
        if not current:
            current = previous
        if self.toolBox.currentIndex()==0:
            self.assetWidgets.setCurrentIndex(self.assetBtns.row(current))

    def changeLiabilityPage(self, current, previous):
        if not current:
            current = previous
        self.lbWidgets.setCurrentIndex(self.lbBtns.row(current))

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

class LiabilityOverviewPage(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel(u'申购记录'))
        self.setLayout(layout)