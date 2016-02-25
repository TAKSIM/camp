# -*- coding: utf-8 -*-
from login import LoginPage
import datetime
import env
from inst.lifecycle import Book, Deal
from PyQt4 import Qt, QtGui, QtCore, QtSql
from dataview.view_subdetails import LiabilityViewSet
from dataview.view_books import BookViewSet
from panel.panel_log import LogPanel, LogStream
from env import WindStartThread
import pandas as pd
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as figureCanvas
import seaborn as sns
import matplotlib.pyplot as plt
import ctypes
from settings import ColorWhite, ColorHighlightText
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('myappid')


class Desktop(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.td = datetime.date.today()
        self.initDB()
        login = LoginPage()
        if login.exec_():
            self.user = env.User(str(login.username.text()))
            self.initFromDB()
            self.log = LogPanel()
            self.logstream = LogStream()
            self.logstream.message.connect(self.log.on_stream_update)
            sys.stdout = self.logstream

            self.sysdate = QtGui.QDateEdit(datetime.date.today())
            self.sysdate.setCalendarPopup(True)
            self.sysdate.setFixedWidth(120)
            self.sysdate.dateChanged.connect(self.on_sysdate_change)
            self.sysdate.setToolTip(u'系统日期')

            self.createAction()
            self.createMenu()
            self.createSystemTray()

            layout = QtGui.QGridLayout()
            self.centralWidget = QtGui.QWidget()
            self.centralWidget.setLayout(layout)
            self.setCentralWidget(self.centralWidget)
            self.treecontrol = TreeControl()
            self.treecontrol.clickSignal.connect(self.switchLayout)
            self.createPages()
            self.topLayout = QtGui.QHBoxLayout()

            self.topLayout.addWidget(self.sysdate, alignment=QtCore.Qt.AlignLeft)
            layout.addLayout(self.topLayout, 0, 0, 1, 7)
            layout.addWidget(self.treecontrol, 1, 0, 20, 1)
            layout.addLayout(self.stackedLayout, 1, 1, 20, 6)

            self.centralWidget = QtGui.QWidget()
            self.centralWidget.setLayout(layout)
            self.setCentralWidget(self.centralWidget)
            self.resize(800, 600)
            self.setWindowTitle(u'固定收益部交易管理平台 - {0}'.format(self.user.name))
            self.setWindowIcon(QtGui.QIcon(env.sysIcon))

            self.show()
            self.statusBar().showMessage(u'启动万得链接...')
            wst = WindStartThread()
            wst.finished.connect(self.windlaunched)
            wst.start()
        else:
            login.close()
            self.close()
            QtGui.qApp.quit()

    def windlaunched(self):
        self.statusBar().showMessage(u'万得连接成功')

    def on_sysdate_change(self):
        cd = self.sysdate.date().toPyDate()
        td = datetime.date.today()
        p = QtGui.QPalette()
        p.setColor(p.Base, cd==td and ColorWhite or ColorHighlightText)
        self.sysdate.setPalette(p)

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
        self.lvs = LiabilityViewSet(self.td)
        layout_subdetails.addWidget(self.newsub, 0, 0, 1, 1)
        layout_subdetails.addWidget(self.lvs.btnExportToExcel, 0, 1, 1, 1)
        layout_subdetails.addWidget(self.lvs.cbShowLiveOnly, 0, 2, 1, 1)
        layout_subdetails.addWidget(self.lvs.btnRefresh, 0, 3, 1, 1)
        layout_subdetails.addWidget(QtGui.QLabel(u'筛选列'), 0, 4, 1, 1)
        layout_subdetails.addWidget(self.lvs.sortCol, 0, 5, 1, 1)
        layout_subdetails.addWidget(QtGui.QLabel(u'列包含'), 0, 6, 1, 1)
        layout_subdetails.addWidget(self.lvs.sortContent, 0, 7, 1, 1)
        layout_subdetails.addWidget(self.lvs.vb, 1, 0, 1, 8)
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
        w = QtGui.QWidget()
        sns.set(style="whitegrid")
        f, ax = plt.subplots(figsize=(20, 12))
        canvas = figureCanvas(f)
        canvas.setParent(w)
        sns.set(style="whitegrid")
        q = QtSql.QSqlQuery("""SELECT EXP_DATE, SUM(AMOUNT), SUM(AMOUNT*(1+EXP_RETURN*(datediff(EXP_DATE, SETTLE_DATE)+1)/36500.0)) FROM LIABILITY WHERE EXP_DATE>='%s' GROUP BY EXP_DATE ORDER BY EXP_DATE"""%self.td)
        dates, vals = [], []
        x_amt = range(0,1000000000,100000000)
        while q.next():
            dates.append(q.value(0).toDate().toPyDate().isoformat())
            vals.append((q.value(1).toDouble()[0], q.value(2).toDouble()[0]))
        data = pd.DataFrame(vals, index=dates, columns=['Amount', 'Total Return'])
        # Plot the total crashes
        sns.set_color_codes("pastel")
        sns.barplot(x='Total Return', y=dates, data=data,
                    label='Interest', color="b")

        # Plot the crashes where alcohol was involved
        sns.set_color_codes("muted")
        sns.barplot(x='Amount', y=dates, data=data,
                    label="Principal", color="b")

        # Add a legend and informative axis label
        ax.legend(ncol=2, loc="upper right", frameon=True)
        ax.set(ylabel="Maturity Date", title='Liability Overview')
        sns.despine(left=True, bottom=True)

        layout.addWidget(w,0,0,1,1)
        return layout

    def showNewSub(self):
        from guis.panel.panel_newsub import NewSubscription
        ns = NewSubscription()
        if ns.exec_():
            self.lvs.vb.refresh()

    def showNewBook(self):
        from guis.panel.panel_newbook import NewBook
        nb = NewBook()
        if nb.exec_():
            self.bvs.vb.refresh()

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
        self.showLogAction = QtGui.QAction(QtGui.QIcon('icons/info.png'), u'显示日志', self, triggered=self.log.show)
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
        self.lvs.vb.refresh() # liability view

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
        q = QtGui.QMessageBox(QtGui.QMessageBox.Question, u'关闭退出', u'确认关闭退出')
        q.setWindowIcon(QtGui.QIcon(r'icons/tent.png'))
        q.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        q.setButtonText(QtGui.QMessageBox.Yes, u'确定')
        q.setButtonText(QtGui.QMessageBox.No, u'取消')
        answer = q.exec_()
        if answer == QtGui.QMessageBox.Yes:
            self.close()
        else:
            event.ignore()
        # if self.trayIcon.isVisible():
        #     # QtGui.QMessageBox.information(self, u"最小化",
        #     #         u"系统将最小化至系统托盘，如果退出请选择“系统->退出”")
        #     self.hide()
        #     event.ignore()

    def about(self):
         QtGui.QMessageBox.about(self, u"关于CAMP", u"长安信托固定收益部交易管理平台")


class TreeControl(QtGui.QTreeWidget):
    clickSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setHeaderHidden(True)
        self.addItems(self.invisibleRootItem())
        self.itemClicked.connect(self.handleClicked)
        self.setFixedWidth(120)

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