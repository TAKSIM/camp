# -*- coding: utf-8 -*-
from WindPy import *
from PyQt4 import QtGui, QtSql, QtCore
import datetime
from inst.lifecycle import Deal

class DepoPanel(QtGui.QDialog):
    def __init__(self, user, books, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'同业存款')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.setFixedSize(200,250)
        self.user = user

        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'交易日'), 0,0,1,1)
        self.tradeDate = QtGui.QDateEdit(datetime.datetime.today())
        self.tradeDate.setCalendarPopup(True)
        layout.addWidget(self.tradeDate, 0, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'账簿'), 1, 0, 1, 1)
        self.books = QtGui.QComboBox()
        self.books.addItems([b.name_cn_short for b in books])
        layout.addWidget(self.books, 1, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'规模（万元）'), 2, 0, 1, 1)
        self.amount = QtGui.QLineEdit()
        layout.addWidget(self.amount, 2, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'收益率（%）'), 3, 0, 1, 1)
        self.price = QtGui.QLineEdit()
        layout.addWidget(self.price, 3, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'到期日'),4,0,1,1)
        self.matDate = QtGui.QDateEdit(datetime.datetime.today())
        self.matDate.setCalendarPopup(True)
        layout.addWidget(self.matDate,4,1,1,2)
        layout.addWidget(QtGui.QLabel(u'计息方式'),5,0,1,1)
        self.dcc = QtGui.QComboBox()
        self.dcc.addItem('Act/360')
        layout.addWidget(self.dcc, 5, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'备注'), 6,0,1,1)
        self.comment = QtGui.QLineEdit()
        layout.addWidget(self.comment, 6,1,1,2)

        buttonLayout = QtGui.QHBoxLayout()
        self.ok = QtGui.QPushButton(u'确定')
        self.ok.clicked.connect(self.bookToDB)
        self.cancel = QtGui.QPushButton(u'取消')
        self.cancel.clicked.connect(self.close)
        buttonLayout.addWidget(self.ok)
        buttonLayout.addWidget(self.cancel)
        layout.addLayout(buttonLayout,7,0,1,3)

        self.setLayout(layout)

    def bookToDB(self):
        if self.matDate <= self.tradeDate:
            QtGui.QMessageBox.about(self, u"错误", u"到期日需要晚于交易日")
        else:
            pass
            today = self.tradeDate.date().toPyDate()
                # amount = float(self.amount.text()) * 10000.
                # comment = self.comment.text()
                # d = Deal(self.user, self.books.currentIndex(), u'同业存款', today, today, amount)


class MmfPanel(QtGui.QDialog):
    def __init__(self, books, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'货币基金')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.setFixedSize(200,250)

        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'交易日'),0,0,1,1)
        self.tradeDate = QtGui.QDateEdit(datetime.datetime.today())
        self.tradeDate.setCalendarPopup(True)
        layout.addWidget(self.tradeDate,0,1,1,2)
        layout.addWidget(QtGui.QLabel(u'账簿'),1,0,1,1)
        self.books = QtGui.QComboBox()
        self.books.addItems([b.name_cn_short for b in books])
        layout.addWidget(self.books, 1,1,1,2)
        layout.addWidget(QtGui.QLabel(u'基金代号'),2,0,1,1)
        self.code = QtGui.QLineEdit()
        self.code.textChanged.connect(self.updateName)
        layout.addWidget(self.code,2,1,1,2)
        layout.addWidget(QtGui.QLabel(u'基金名称'),3,0,1,1)
        self.name = QtGui.QLineEdit()
        self.name.setEchoMode(False)
        layout.addWidget(self.name,3,1,1,2)
        layout.addWidget(QtGui.QLabel(u'规模（万元）'),4,0,1,1)
        self.amount = QtGui.QLineEdit()
        layout.addWidget(self.amount,4,1,1,2)
        layout.addWidget(QtGui.QLabel(u'备注'),5,0,1,1)
        self.comment = QtGui.QLineEdit()
        layout.addWidget(self.comment,5,1,1,2)

        buttonLayout = QtGui.QHBoxLayout()
        self.ok = QtGui.QPushButton(u'确定')
        self.cancel = QtGui.QPushButton(u'取消')
        self.cancel.clicked.connect(self.close)
        buttonLayout.addWidget(self.ok)
        buttonLayout.addWidget(self.cancel)
        layout.addLayout(buttonLayout,6,0,1,3)

        self.setLayout(layout)

    def updateName(self):
        code = str(self.code.text())
        name = w.wss(code, 'Name', 'tradeDate={0}'.format(datetime.datetime.today(), '%Y%m%d'), 'credibility=1')


class BondPanel(QtGui.QDialog):
    def __init__(self, books, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'债券现券')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.setFixedSize(800,300)

        layout = QtGui.QHBoxLayout()

        gbInfo = QtGui.QGroupBox(u'基本信息')
        infoLayout = QtGui.QGridLayout()
        infoLayout.addWidget(QtGui.QLabel(u'代码'),0,0,1,1)
        self.code = QtGui.QLineEdit()
        self.code.returnPressed.connect(self.updateInfo)
        infoLayout.addWidget(self.code,0,1,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'简称'),0,2,1,1)
        self.name = QtGui.QLineEdit()
        self.name.setEnabled(False)
        infoLayout.addWidget(self.name,0,3,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'发行人'),1,0,1,1)
        self.issuer = QtGui.QLineEdit()
        self.issuer.setEnabled(False)
        infoLayout.addWidget(self.issuer,1,1,1,3)
        infoLayout.addWidget(QtGui.QLabel(u'类别'),2,0,1,1)
        self.bondType = QtGui.QLineEdit()
        self.bondType.setEnabled(False)
        infoLayout.addWidget(self.bondType,2,1,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'到期日'),2,2,1,1)
        self.matDate = QtGui.QDateEdit()
        self.matDate.setEnabled(False)
        infoLayout.addWidget(self.matDate,2,3,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'期限（年）'),3,0,1,1)
        self.length = QtGui.QLineEdit()
        self.length.setEnabled(False)
        infoLayout.addWidget(self.length,3,1,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'剩余（年）'),3,2,1,1)
        self.ttm = QtGui.QLineEdit()
        self.ttm.setEnabled(False)
        infoLayout.addWidget(self.ttm,3,3,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'当期票息（%）'),4,0,1,1)
        self.coupon = QtGui.QLineEdit()
        self.coupon.setEnabled(False)
        infoLayout.addWidget(self.coupon,4,1,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'利率类型'),4,2,1,1)
        self.couponType = QtGui.QLineEdit()
        self.couponType.setEnabled(False)
        infoLayout.addWidget(self.couponType,4,3,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'久期'),5,0,1,1)
        self.moddur = QtGui.QLineEdit()
        self.moddur.setEnabled(False)
        infoLayout.addWidget(self.moddur,5,1,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'市场'),5,2,1,1)
        self.mkt = QtGui.QLineEdit()
        self.mkt.setEnabled(False)
        infoLayout.addWidget(self.mkt,5,3,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'主体评级'),6,0,1,1)
        self.ratingIssuer = QtGui.QLineEdit()
        self.ratingIssuer.setEnabled(False)
        infoLayout.addWidget(self.ratingIssuer,6,1,1,1)
        infoLayout.addWidget(QtGui.QLabel(u'债项评级'),6,2,1,1)
        self.ratingBond = QtGui.QLineEdit()
        self.ratingBond.setEnabled(False)
        infoLayout.addWidget(self.ratingBond,6,3,1,1)
        gbInfo.setLayout(infoLayout)
        layout.addWidget(gbInfo)

        gbTrade = QtGui.QGroupBox(u'交易')
        tradeLayout = QtGui.QGridLayout()
        tradeLayout.addWidget(QtGui.QLabel(u'交易日'),0,0,1,1)
        self.tradeDate = QtGui.QDateEdit(datetime.datetime.today())
        self.tradeDate.setCalendarPopup(True)
        tradeLayout.addWidget(self.tradeDate,0,1,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'账簿'),1,0,1,1)
        self.books = QtGui.QComboBox()
        self.books.addItems([b.name_cn_short for b in books])
        tradeLayout.addWidget(self.books,1,1,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'方向'),1,2,1,1)
        self.dir = QtGui.QComboBox()
        self.dir.addItems([u'买入',u'卖出'])
        tradeLayout.addWidget(self.dir,1,3,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'金额（万元）'),2,0,1,1)
        self.amount = QtGui.QLineEdit()
        tradeLayout.addWidget(self.amount,2,1,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'成交T+'),2,2,1,1)
        self.settle = QtGui.QLineEdit('0')
        self.settle.setValidator(QtGui.QIntValidator())
        tradeLayout.addWidget(self.settle,2,3,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'估值'),3,0,1,1)
        self.value = QtGui.QLineEdit()
        self.value.setEnabled(False)
        tradeLayout.addWidget(self.value,3,1,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'估值日'),3,2,1,1)
        self.vdate = QtGui.QDateEdit(datetime.datetime.today()-datetime.timedelta(days=1))
        self.vdate.setCalendarPopup(True)
        self.vdate.dateChanged.connect(self.updateValue)
        tradeLayout.addWidget(self.vdate,3,3,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'净价'),4,0,1,1)
        self.clean = QtGui.QLineEdit()
        tradeLayout.addWidget(self.clean,4,1,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'到期收益率(%)'),4,2,1,1)
        self.ytm = QtGui.QLineEdit()
        tradeLayout.addWidget(self.ytm,4,3,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'全价'),5,0,1,1)
        self.full = QtGui.QLineEdit()
        tradeLayout.addWidget(self.full,5,1,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'应计利息'),5,2,1,1)
        self.ai = QtGui.QLineEdit()
        self.ai.setEnabled(False)
        tradeLayout.addWidget(self.ai,5,3,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'备注'),0,2,1,1)
        self.comment = QtGui.QLineEdit()
        tradeLayout.addWidget(self.comment,0,3,1,1)

        buttonLayout = QtGui.QHBoxLayout()
        self.ok = QtGui.QPushButton(u'确定')
        self.cancel = QtGui.QPushButton(u'取消')
        self.cancel.clicked.connect(self.close)
        buttonLayout.addWidget(self.ok)
        buttonLayout.addWidget(self.cancel)
        tradeLayout.addLayout(buttonLayout, 6,2,1,2)

        gbTrade.setLayout(tradeLayout)
        layout.addWidget(gbTrade)

        self.setLayout(layout)

    def updateInfo(self):
        infolist = ['sec_name', # 证券简称
                    'issuerupdated', # 发行人
                    'windl1type', # 债券类别
                    'maturitydate', # 到期日
                    'term', # 发行期限
                    'couponrate', # 票息
                    'interesttype', # 利率类型
                    'exch_city', # 市场
                    'latestissurercreditrating', # 主体评级
                    'amount', # 债项评级
                    'lastdate_cnbd' # 最新估值日
                    ]
        data = w.wss(str(self.code.text()), infolist, 'tradeDate={0}'.format(format(datetime.datetime.today(), '%Y%m%d')), 'credibility=1')
        if data.ErrorCode == 0:
            self.name.setText(data.Data[0][0])
            self.issuer.setText(data.Data[1][0])
            self.bondType.setText(data.Data[2][0])
            self.matDate.setDate(data.Data[3][0])
            self.length.setText(format(data.Data[4][0], '.2f'))
            self.coupon.setText(format(data.Data[5][0], '.3f'))
            self.couponType.setText(data.Data[6][0])
            self.mkt.setText(data.Data[7][0])
            self.ratingIssuer.setText(str(data.Data[8][0]))
            self.ratingBond.setText(str(data.Data[9][0]))
            self.ttm.setText(format((data.Data[3][0]-datetime.datetime.today()).days/365.0, '.2f'))
            lastVDate = data.Data[10][0]
            self.vdate.setDate(lastVDate)
        else:
            QtGui.QMessageBox.information(self, u'万得数据错误', str(data.ErrorCode))
        v = w.wss(str(self.code.text()), ['yield_cnbd','modidura_cnbd'],'tradeDate={0}'.format(format(lastVDate,'%Y%m%d')), 'credibility=1')
        if v.ErrorCode == 0:
            self.value.setText(format(v.Data[0][0], '.3f'))
            self.moddur.setText(format(v.Data[1][0], '.3f'))
        else:
            QtGui.QMessageBox.information(self, u'万得数据错误', str(v.ErrorCode))

    def updateValue(self):
        newDate = self.vdate.date()
        data = w.wss(str(self.code.text()),['yield_cnbd'],'tradeDate={0}'.format(newDate.toString('yyyyMMdd')), 'credibility=1')
        if data.ErrorCode == 0 and data.Data[0][0]:
            self.value.setText(format(data.Data[0][0],'.4f'))

class HolidayPanel(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'假期设置')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.setMaximumWidth(200)
        layout = QtGui.QVBoxLayout()
        self.holData = QtSql.QSqlTableModel()
        self.holData.setTable('holidays')
        self.holData.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.holData.select()
        self.holData.setHeaderData(0, QtCore.Qt.Horizontal, u'日期')
        self.holData.setHeaderData(1, QtCore.Qt.Horizontal, u'假期')
        self.holData.setHeaderData(2, QtCore.Qt.Horizontal, u'状态')
        self.holView = QtGui.QTableView()
        self.holView.setModel(self.holData)
        self.holView.resizeColumnsToContents()
        self.holView.resizeRowsToContents()
        self.holView.verticalHeader().hide()

        buttonLayout = QtGui.QHBoxLayout()
        self.btAdd = QtGui.QPushButton(u'添加假期')
        self.btAdd.clicked.connect(self.newHol)
        self.btConf = QtGui.QPushButton(u'确认修改')
        self.btConf.clicked.connect(self.submit)
        self.btCancel = QtGui.QPushButton(u'取消')
        self.btCancel.clicked.connect(self.close)
        buttonLayout.addWidget(self.btAdd)
        buttonLayout.addWidget(self.btConf)
        buttonLayout.addWidget(self.btCancel)
        layout.addLayout(buttonLayout)

        layout.addWidget(self.holView)
        self.setLayout(layout)

    def submit(self):
        self.holData.submitAll()

    def newHol(self):
        nh = NewHolPanel()
        if nh.exec_():
            date = nh.date.date()
            name = nh.nameList.currentText()
            status = nh.statusList.currentText()
            q = QtSql.QSqlQuery()
            try:
                q.exec_("""INSERT INTO HOLIDAYS VALUES ('%s','%s','%s')""" % (date.toPyDate(), name, status))
                QtSql.QSqlDatabase().commit()
            except Exception, e:
                print e.message
                QtSql.QSqlDatabase().rollback()

class NewHolPanel(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.setWindowTitle(u'新增假期')
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'日期'),0,0,1,1)
        self.date = QtGui.QDateEdit(datetime.datetime.today())
        self.date.setCalendarPopup(True)
        layout.addWidget(self.date,0,1,1,1)
        layout.addWidget(QtGui.QLabel(u'假期'),1,0,1,1)
        self.nameList = QtGui.QComboBox()
        self.nameList.addItems([u'元旦',u'春节',u'清明节',u'劳动节',u'端午节',u'中秋节',u'国庆节',u'其他'])
        self.nameList.setEditable(True)
        layout.addWidget(self.nameList,1,1,1,1)
        layout.addWidget(QtGui.QLabel(u'状态'),2,0,1,1)
        self.statusList = QtGui.QComboBox()
        self.statusList.addItems([u'预期',u'确定',u'工作'])
        layout.addWidget(self.statusList,2,1,1,1)
        self.ok = QtGui.QPushButton(u'确定')
        self.ok.clicked.connect(self.accept)
        layout.addWidget(self.ok,3,0,1,1)
        self.cancel = QtGui.QPushButton(u'取消')
        self.cancel.clicked.connect(self.close)
        layout.addWidget(self.cancel,3,1,1,1)
        self.setLayout(layout)

# class BondPanel(QtGui.QDialog):
#     def __init__(self, parent=None):
#         QtGui.QDialog.__init__(self, parent)
#         self.setWindowTitle(u'债券查询交易')
#         self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
#         self.setFont(QtGui.QFont('SimHei',12, QtGui.QFont.Bold))
#         pe = QtGui.QPalette()
#         pe.setColor(QtGui.QPalette.WindowText, QtGui.QColor(219,123,37))
#         pe.setColor(QtGui.QPalette.Background, QtGui.QColor(10,15,14))
#         self.setPalette(pe)
#
#         #self.setFixedSize(300,250)
#         layout = QtGui.QHBoxLayout()
#         srcLayout = QtGui.QVBoxLayout()
#         trdLayout = QtGui.QVBoxLayout()
#         layout.addLayout(srcLayout)
#         layout.addLayout(trdLayout)
#         self.setLayout(layout)
#
#         self.buildID()
#         self.buildInfo()
#         srcLayout.addWidget(self.gbID)
#         srcLayout.addWidget(self.gbInfo)
#
#         self.buildPrice()
#         self.buildTrade()
#         trdLayout.addWidget(self.gbPrice)
#         trdLayout.addWidget(self.gbTrade)
#
#         self.setLayout(layout)
#
#     def buildID(self):
#         self.gbID = QtGui.QGroupBox(u'代码/名称')
#
#         layout = QtGui.QHBoxLayout()
#         layout.addWidget(QtGui.QLabel(u'代码'))
#         self.leID = QtGui.QLineEdit()
#         layout.addWidget(self.leID)
#         layout.addWidget(QtGui.QLabel(u'名称'))
#         self.leName = QtGui.QLineEdit()
#         layout.addWidget(self.leName)
#
#         self.gbID.setLayout(layout)
#
#     def buildInfo(self):
#         self.gbInfo = QtGui.QGroupBox(u'债券信息')
#
#         layout = QtGui.QGridLayout()
#         layout.addWidget(QtGui.QLabel(u'发行人'),0,0,1,1)
#         self.leIssuer = QtGui.QLineEdit()
#         layout.addWidget(self.leIssuer,0,1,1,3)
#         layout.addWidget(QtGui.QLabel(u'行业'),1,0,1,1)
#         self.leInd = QtGui.QLineEdit()
#         layout.addWidget(self.leInd,1,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'类别'),1,2,1,1)
#         self.leType = QtGui.QLineEdit()
#         layout.addWidget(self.leType,1,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'到期日'),2,0,1,1)
#         self.leMat = QtGui.QDateEdit()
#         self.leMat.setCalendarPopup(True)
#         layout.addWidget(self.leMat,2,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'久期'),2,2,1,1)
#         self.leDur = QtGui.QLineEdit()
#         layout.addWidget(self.leDur,2,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'票息(%)'),3,0,1,1)
#         self.leCoupon = QtGui.QLineEdit()
#         layout.addWidget(self.leCoupon,3,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'付息频率'),3,2,1,1)
#         self.leCouponFreq = QtGui.QLineEdit()
#         layout.addWidget(self.leCouponFreq,3,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'中债估值'),4,0,1,1)
#         self.leValue = QtGui.QLineEdit()
#         layout.addWidget(self.leValue,4,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'估值日'),4,2,1,1)
#         self.leVD = QtGui.QDateEdit()
#         layout.addWidget(self.leVD,4,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'主体评级'),5,0,1,1)
#         self.leIssuerRating = QtGui.QLineEdit()
#         layout.addWidget(self.leIssuerRating,5,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'债项评级'),5,2,1,1)
#         self.leSecRating = QtGui.QLineEdit()
#         layout.addWidget(self.leSecRating,5,3,1,1)
#
#         self.gbInfo.setLayout(layout)
#
#     def buildPrice(self):
#         self.gbPrice = QtGui.QGroupBox(u'价格试算')
#
#         layout = QtGui.QGridLayout()
#         layout.addWidget(QtGui.QLabel(u'到期收益率(%)'),0,0,1,1)
#         self.leYTM = QtGui.QLineEdit()
#         layout.addWidget(self.leYTM,0,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'全价'),0,2,1,1)
#         self.leDP = QtGui.QLineEdit()
#         layout.addWidget(self.leDP,0,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'净价'),1,0,1,1)
#         self.leCP = QtGui.QLineEdit()
#         layout.addWidget(self.leCP,1,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'T+'),1,2,1,1)
#         self.DTS = QtGui.QLineEdit()
#         layout.addWidget(self.DTS,1,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'交易日'),2,0,1,1)
#         self.dpTradeDate = QtGui.QDateEdit(datetime.date.today())
#         layout.addWidget(self.dpTradeDate, 2,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'交割日'),2,2,1,1)
#         self.dpSettleDate = QtGui.QDateEdit(datetime.date.today())
#         layout.addWidget(self.dpSettleDate,2,3,1,1)
#
#         self.gbPrice.setLayout(layout)
#
#     def buildTrade(self):
#         self.gbTrade = QtGui.QGroupBox(u'交易')
#
#         layout = QtGui.QGridLayout()
#
#
#         self.gbTrade.setLayout(layout)
#
#     def trade(self):
#         print 'hello'

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    m = BondPanel()
    m.show()
    sys.exit(app.exec_())
