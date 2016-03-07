# -*- coding: utf-8 -*-
from panel_base import PanelBase
from PyQt4 import QtGui, QtSql
import datetime
from WindPy import w
from trade import BondTrade


class NewBond(PanelBase):
    def __init__(self, user, sysdate, code, dateCalc, parent=None):
        super(NewBond, self).__init__(viewOnly=True, parent=parent)
        self.setWindowTitle(u'债券交易')
        self.sysdate = sysdate
        self.user = user
        self.dateCalc = dateCalc
        layout = QtGui.QGridLayout()
        gbInfo = QtGui.QGroupBox(u'基本信息')
        infoLayout = QtGui.QGridLayout()
        infoLayout.addWidget(QtGui.QLabel(u'代码'), 0, 0, 1, 1)
        self.code = QtGui.QLineEdit()
        self.code.setText(code)
        self.code.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.code, 0, 1, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'简称'), 0, 2, 1, 1)
        self.name = QtGui.QLineEdit()
        self.name.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.name, 0, 3, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'发行人'), 1, 0, 1, 1)
        self.issuer = QtGui.QLineEdit()
        self.issuer.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.issuer, 1, 1, 1, 3)
        infoLayout.addWidget(QtGui.QLabel(u'类别'), 2, 0, 1, 1)
        self.bondType = QtGui.QLineEdit()
        self.bondType.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.bondType, 2, 1, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'到期日'), 2, 2, 1, 1)
        self.matDate = QtGui.QDateEdit()
        self.matDate.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.matDate, 2, 3, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'期限（年）'), 3, 0, 1, 1)
        self.length = QtGui.QLineEdit()
        self.length.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.length, 3, 1, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'剩余（年）'), 3, 2, 1, 1)
        self.ttm = QtGui.QLineEdit()
        self.ttm.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.ttm, 3, 3, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'当期票息（%）'), 4, 0, 1, 1)
        self.coupon = QtGui.QLineEdit()
        self.coupon.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.coupon, 4, 1, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'利率类型'), 4, 2, 1, 1)
        self.couponType = QtGui.QLineEdit()
        self.couponType.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.couponType, 4, 3, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'久期'), 5, 0, 1, 1)
        self.moddur = QtGui.QLineEdit()
        self.moddur.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.moddur, 5, 1, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'市场'), 5, 2, 1, 1)
        self.mkt = QtGui.QLineEdit()
        self.mkt.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.mkt, 5, 3, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'主体评级'), 6, 0, 1, 1)
        self.ratingIssuer = QtGui.QLineEdit()
        self.ratingIssuer.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.ratingIssuer, 6, 1, 1, 1)
        infoLayout.addWidget(QtGui.QLabel(u'债项评级'), 6, 2, 1, 1)
        self.ratingBond = QtGui.QLineEdit()
        self.ratingBond.setReadOnly(self.viewOnly)
        infoLayout.addWidget(self.ratingBond, 6, 3, 1, 1)
        gbInfo.setLayout(infoLayout)
        layout.addWidget(gbInfo, 0, 0, 1, 4)

        gbTrade = QtGui.QGroupBox(u'交易')
        tradeLayout = QtGui.QGridLayout()
        tradeLayout.addWidget(QtGui.QLabel(u'交易日'),0,0,1,1)
        self.tradeDateTime = QtGui.QDateTimeEdit(datetime.datetime.now())
        self.tradeDateTime.setCalendarPopup(True)
        tradeLayout.addWidget(self.tradeDateTime,0,1,1,1)
        tradeLayout.addWidget(QtGui.QLabel(u'账簿'),1,0,1,1)
        self.books = QtGui.QComboBox()
        q = QtSql.QSqlQuery('SELECT NAME_CN FROM BOOKS ORDER BY ID')
        books = []
        while q.next():
            books.append(q.value(0).toString())
        self.books.addItems(books)
        tradeLayout.addWidget(self.books, 1, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'交易方向'), 0, 2, 1, 1)
        self.dir = QtGui.QComboBox()
        self.dir.addItems([u'买入', u'卖出'])
        tradeLayout.addWidget(self.dir, 0, 3, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'面值（万元）'), 2, 0, 1, 1)
        self.amount = QtGui.QLineEdit()
        tradeLayout.addWidget(self.amount, 2, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'成交T+'), 1, 2, 1, 1)
        self.settle = QtGui.QLineEdit('0')
        self.settle.setValidator(QtGui.QIntValidator())
        self.settle.textChanged.connect(self.updateSettleDate)
        tradeLayout.addWidget(self.settle, 1, 3, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'交割日'), 2, 2, 1, 1)
        self.settleDate = QtGui.QDateEdit(self.sysdate)
        self.settleDate.setCalendarPopup(True)
        tradeLayout.addWidget(self.settleDate, 2, 3, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'估值'), 3, 0, 1, 1)
        self.value = QtGui.QLineEdit()
        self.value.setReadOnly(True)
        tradeLayout.addWidget(self.value, 3, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'估值日'), 3, 2, 1, 1)
        self.vdate = QtGui.QDateEdit(self.sysdate - datetime.timedelta(days=1))
        self.vdate.setCalendarPopup(True)
        self.vdate.dateChanged.connect(self.updateValue)
        tradeLayout.addWidget(self.vdate, 3, 3, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'净价'), 4, 0, 1, 1)
        self.clean = QtGui.QLineEdit()
        tradeLayout.addWidget(self.clean, 4, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'到期收益率(%)'), 4, 2, 1, 1)
        self.ytm = QtGui.QLineEdit()
        tradeLayout.addWidget(self.ytm, 4, 3, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'全价'), 5, 0, 1, 1)
        self.full = QtGui.QLineEdit()
        tradeLayout.addWidget(self.full, 5, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'应计利息'), 5, 2, 1, 1)
        self.ai = QtGui.QLineEdit()
        self.ai.setReadOnly(True)
        tradeLayout.addWidget(self.ai, 5, 3, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'备注'), 6, 0, 1, 1)
        self.comment = QtGui.QLineEdit()
        tradeLayout.addWidget(self.comment, 6, 1, 1, 3)
        gbTrade.setLayout(tradeLayout)
        layout.addWidget(gbTrade, 1, 0, 1, 4)

        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(self.ok)
        btnLayout.addWidget(self.cancel)
        layout.addLayout(btnLayout, 2, 2, 1, 2)

        self.updateInfo()

        self.setLayout(layout)

    def updateSettleDate(self):
        n, _ = self.settle.text().toInt()
        if n == 0:
            self.settleDate.setDate(self.tradeDateTime.dateTime().toPyDateTime().date())
        elif n > 0:
            self.settleDate.setDate(self.dateCalc.NextBusinessDay(self.tradeDateTime.dateTime().toPyDateTime().date(), numDays=n))
        else:
            pass

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
        v = w.wss(str(self.code.text()), ['yield_cnbd', 'modidura_cnbd'], 'tradeDate={0}'.format(format(lastVDate,'%Y%m%d')), 'credibility=1')
        if v.ErrorCode == 0:
            self.value.setText(format(v.Data[0][0], '.3f'))
            self.moddur.setText(format(v.Data[1][0], '.3f'))
        else:
            QtGui.QMessageBox.information(self, u'万得数据错误', str(v.ErrorCode))

    def updateValue(self):
        newDate = self.vdate.date()
        data = w.wss(str(self.code.text()), ['yield_cnbd'], 'tradeDate={0}'.format(newDate.toString('yyyyMMdd')), 'credibility=1')
        if data.ErrorCode == 0 and data.Data[0][0]:
            self.value.setText(format(data.Data[0][0], '.4f'))

    def toDB(self):
        face, _ = self.amount.text().toDouble()
        dir = self.dir.currentIndex()==0 and 1 or -1
        amount = face * 100. * dir  # * 10000 / 100

        bt = BondTrade(self.books.currentIndex(),
                       self.user,
                       self.tradeDate.dateTime().toPyDateTime(),
                       self.settleDate.date().toPyDate(),
                       self.code.text(),
                       amount,
                       self.full.text().toDouble()[0],
                       self.ytm.text().toDouble()[0],
                       comment=self.comment.text())
        bt.toDB()

    def check_validity(self, raiseWarning=False):
        return True