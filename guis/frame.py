# -*- coding: utf-8 -*-
from login import LoginPage
import env
from inst.lifecycle import Book, Deal
from PyQt4 import Qt, QtGui, QtCore, QtSql
from dataview.view_subdetails import LiabilityViewSet
from dataview.view_books import BookViewSet
from panel.panel_log import LogPanel, LogStream
from WindPy import *
from matplotlibwidget import MatplotlibWidget
import ctypes
import sys
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('myappid')


class Desktop(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.td = datetime.today()
        self.initDB()
        login = LoginPage()
        if login.exec_():
            self.user = env.User(str(login.username.text()))
            self.initFromDB()
            self.log = LogPanel()
            self.logstream = LogStream()
            self.logstream.message.connect(self.log.on_stream_update)
            sys.stdout = self.logstream

            self.createAction()
            self.createMenu()
            self.createSystemTray()
            self.createPages()

            layout = QtGui.QHBoxLayout()
            self.centralWidget = QtGui.QWidget()
            self.centralWidget.setLayout(layout)
            self.setCentralWidget(self.centralWidget)
            self.treecontrol = TreeControl()
            self.treecontrol.clickSignal.connect(self.switchLayout)
            layout.addWidget(self.treecontrol)
            layout.addLayout(self.stackedLayout)

            self.centralWidget = QtGui.QWidget()
            self.centralWidget.setLayout(layout)
            self.setCentralWidget(self.centralWidget)
            self.resize(800, 600)
            self.setWindowTitle(u'固定收益部交易管理平台 - {0}'.format(self.user.name))
            self.setWindowIcon(QtGui.QIcon(env.sysIcon))

            self.show()
            self.statusBar().showMessage(u'启动万得链接')
            #w.start()
            self.statusBar().showMessage(u'准备就绪')
        else:
            QtGui.qApp.quit()

    def createPages(self):
        self.stackedLayout = QtGui.QStackedLayout()
        # acct overview
        self.acctview = QtGui.QLabel(u'账户总览')
        self.stackedLayout.addWidget(self.acctview)

        # trade details
        self.tradedetails = QtGui.QLabel(u'交易明细')
        self.stackedLayout.addWidget(self.tradedetails)

        # book details
        self.bookdetails = QtGui.QWidget()
        layout_bookdetails = QtGui.QGridLayout()
        self.bvs = BookViewSet()
        layout_bookdetails.addWidget(self.bvs.btnRefresh,0,0,1,1)
        self.newbook = QtGui.QPushButton(u'添加账簿')
        self.newbook.clicked.connect(self.showNewBook)
        layout_bookdetails.addWidget(self.newbook,0,1,1,1)
        layout_bookdetails.addWidget(self.bvs.vb,1,0,1,6)
        self.bookdetails.setLayout(layout_bookdetails)
        self.stackedLayout.addWidget(self.bookdetails)

        # subscription overview
        self.suboverview = QtGui.QWidget()
        layout_suboverview = self.createSubOverviewPage()
        self.suboverview.setLayout(layout_suboverview)
        self.stackedLayout.addWidget(self.suboverview)

        # subscription details
        self.subdetails = QtGui.QWidget()
        layout_subdetails = QtGui.QGridLayout()
        self.newsub = QtGui.QPushButton(u'添加认购信息')
        self.newsub.clicked.connect(self.showNewSub)
        self.lvs = LiabilityViewSet()
        layout_subdetails.addWidget(self.lvs.btnRefresh, 0, 0, 1, 1)
        layout_subdetails.addWidget(self.lvs.cbShowLiveOnly, 0, 1, 1, 1)
        layout_subdetails.addWidget(self.newsub, 0, 2, 1, 1)
        layout_subdetails.addWidget(QtGui.QLabel(u'筛选列'), 0, 3, 1, 1)
        layout_subdetails.addWidget(self.lvs.sortCol, 0, 4, 1, 1)
        layout_subdetails.addWidget(QtGui.QLabel(u'列包含'), 0, 5, 1, 1)
        layout_subdetails.addWidget(self.lvs.sortContent, 0, 6, 1, 1)
        layout_subdetails.addWidget(self.lvs.vb, 1, 0, 1, 7)
        self.subdetails.setLayout(layout_subdetails)
        self.stackedLayout.addWidget(self.subdetails)

        # credit research
        self.bondpool = QtGui.QLabel(u'债券池')
        self.stackedLayout.addWidget(self.bondpool)

        # risk control
        self.risk = QtGui.QLabel(u'待开发')
        self.stackedLayout.addWidget(self.risk)

    def createSubOverviewPage(self):
        layout = QtGui.QGridLayout()
        q = QtSql.QSqlQuery("""select client_type, sum(amount) from liability where exp_date>='%s' group by client_type"""%self.td)
        byInstTypeLabels = []
        byInstTypeValues = []
        while q.next():
            byInstTypeLabels.append(q.value(0).toString())
            byInstTypeValues.append(q.value(1).toDouble()[0]/100000000.)
        fw = MatplotlibWidget(parent=self, width=1, height=1, title='TEST ONLY')
        subplot = fw.figure.add_subplot(111)
        subplot.pie(byInstTypeValues, labels=byInstTypeLabels, autopct='%1.1f%%')
        fw.draw()
        layout.addWidget(fw,0,0,1,1)
        return layout

    def showNewSub(self):
        from guis.panel.panel_newsub import NewSubscription
        ns = NewSubscription()
        if ns.exec_():
            pass

    def showNewBook(self):
        from guis.panel.panel_newbook import NewBook
        nb = NewBook()
        if nb.exec_():
            pass

    def switchLayout(self, itemName):
        if itemName == Qt.QString(u'账户总览'):
            self.stackedLayout.setCurrentWidget(self.acctview)
        elif itemName == Qt.QString(u'交易明细'):
            self.stackedLayout.setCurrentWidget(self.tradedetails)
        elif itemName == Qt.QString(u'账簿信息'):
            self.stackedLayout.setCurrentWidget(self.bookdetails)
        elif itemName == Qt.QString(u'负债总览'):
            self.stackedLayout.setCurrentWidget(self.suboverview)
        elif itemName == Qt.QString(u'申购明细'):
            self.stackedLayout.setCurrentWidget(self.subdetails)
        elif itemName == Qt.QString(u'债券池'):
            self.stackedLayout.setCurrentWidget(self.bondpool)

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
            self.books.append(Book(q.value(0).toString(),
                                   q.value(1).toString(),
                                   q.value(2).toDate().toPyDate(),
                                   q.value(3).toString(),
                                   q.value(4).toString()))

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
        m1.addAction(self.showLogAction)
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
        self.showLogAction = QtGui.QAction(u'显示日志', self, triggered=self.log.show)
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
            bookID = bond.books.currentIndex()
            instID = str(bond.code.text())
            bookDate = bond.tradeDate.date()
            daysToSettle = int(bond.settle.text())
            if daysToSettle == 0:
                settleDate = bookDate
            else:
                settleDate = w.tdaysoffset(daysToSettle, bookDate).Data[0][0].date()
            amount = float(bond.amount.text())*10000.

            #user, bookID, instID, bookDate, settleDate, amount, tradePrice

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


class TreeControl(QtGui.QTreeWidget):
    clickSignal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setHeaderHidden(True)
        self.addItems(self.invisibleRootItem())
        self.itemClicked.connect(self.handleClicked)
        self.setMaximumWidth(120)

    def addItems(self, parent):
        assets_item = self.addParent(parent, u'资产' )
        self.addChild(assets_item, u'账户总览')
        self.addChild(assets_item, u'交易明细')
        self.addChild(assets_item, u'账簿信息')

        liability_item = self.addParent(parent, u'负债')
        self.addChild(liability_item, u'负债总览')
        self.addChild(liability_item, u'申购明细')

        credit_item = self.addParent(parent, u'信用研究')
        self.addChild(credit_item, u'债券池')

        risk_item = self.addParent(parent, u'风险控制')


    def addParent(self, parent, title):
        item = QtGui.QTreeWidgetItem(parent, [title])
        item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
        item.setExpanded(True)
        return item

    def addChild(self, parent, title):
        item = QtGui.QTreeWidgetItem(parent, [title])
        return item

    def handleClicked(self, item):
        si = self.selectedItems()[0].text(0)
        self.clickSignal.emit(si)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    f = Desktop()
    sys.exit(app.exec_())