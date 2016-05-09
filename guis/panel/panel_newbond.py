# -*- coding: utf-8 -*-
from panel_base import PanelBase
from PyQt4 import QtGui, QtSql
import datetime
from WindPy import w
from trade import BondTrade
from instrument import CashBond

class NewBond(PanelBase):
    def __init__(self, user, sysdate, code, dateCalc, parent=None):
        super(NewBond, self).__init__(viewOnly=True, parent=parent)
        self.setWindowTitle(u'债券交易')
        self.sysdate = sysdate
        self.user = user
        self.dateCalc = dateCalc
        self.inst = CashBond(code)
        layout = QtGui.QGridLayout()
        gbInfo = QtGui.QGroupBox(u'基本信息')
        gbInfo.setLayout(self.inst.gui(readonly=True, asOfDate=sysdate))
        layout.addWidget(gbInfo, 0, 0, 1, 4)

        gbTrade = QtGui.QGroupBox(u'交易')
        tradeLayout = QtGui.QGridLayout()
        tradeLayout.addWidget(QtGui.QLabel(u'交易日'),0, 0, 1, 1)
        self.tradeDateTime = QtGui.QDateTimeEdit(datetime.datetime.now())
        self.tradeDateTime.setCalendarPopup(True)
        self.tradeDateTime.dateTimeChanged.connect(self.on_tradedate_change)
        tradeLayout.addWidget(self.tradeDateTime, 0, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'账簿'), 1, 0, 1, 1)
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
        tradeLayout.addWidget(QtGui.QLabel(u'久期'), 4, 0, 1, 1)
        self.moddur = QtGui.QLineEdit()
        self.moddur.setReadOnly(True)
        tradeLayout.addWidget(self.moddur, 4, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'到期收益率(%)'), 4, 2, 1, 1)
        self.ytm = QtGui.QLineEdit()
        tradeLayout.addWidget(self.ytm, 4, 3, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'净价'), 5, 0, 1, 1)
        self.clean = QtGui.QLineEdit()
        tradeLayout.addWidget(self.clean, 5, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'全价'), 5, 2, 1, 1)
        self.full = QtGui.QLineEdit()
        tradeLayout.addWidget(self.full, 5, 3, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'备注'), 6, 0, 1, 1)
        self.comment = QtGui.QLineEdit()
        tradeLayout.addWidget(self.comment, 6, 1, 1, 1)
        tradeLayout.addWidget(QtGui.QLabel(u'应计利息'), 6, 2, 1, 1)
        self.ai = QtGui.QLineEdit()
        self.ai.setReadOnly(True)
        tradeLayout.addWidget(self.ai, 6, 3, 1, 1)
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

    def on_tradedate_change(self):
        self.updateSettleDate()

    def updateInfo(self):
        infolist = [
                    'lastdate_cnbd' # 最新估值日
                    ]
        data = w.wss(str(self.inst.code), infolist, 'tradeDate={0}'.format(format(datetime.datetime.today(), '%Y%m%d')), 'credibility=1')
        if data.ErrorCode == 0:
            lastVDate = data.Data[0][0]
            self.vdate.setDate(lastVDate)
        else:
            QtGui.QMessageBox.information(self, u'万得数据错误', str(data.ErrorCode))
        v = w.wss(str(self.inst.code), ['yield_cnbd', 'modidura_cnbd'], 'tradeDate={0}'.format(format(lastVDate,'%Y%m%d')), 'credibility=1')
        if v and v.ErrorCode == 0:
            self.value.setText(format(v.Data[0][0], '.4f'))
            self.moddur.setText(format(v.Data[1][0], '.3f'))
        else:
            QtGui.QMessageBox.information(self, u'万得数据错误', str(v.ErrorCode))

    def updateValue(self):
        newDate = self.vdate.date()
        data = w.wss(str(self.inst.code), ['yield_cnbd', 'modidura_cnbd'], 'tradeDate={0}'.format(newDate.toString('yyyyMMdd')), 'credibility=1')
        if data and data.ErrorCode == 0 and data.Data[0][0]:
            self.value.setText(format(data.Data[0][0], '.4f'))
            self.moddur.setText(format(data.Data[1][0], '.3f'))
        else:
            QtGui.QMessageBox.information(self, u'无数据', u'无对应的万得数据')

    def toDB(self):
        face, _ = self.amount.text().toDouble()
        dir = self.dir.currentIndex()==0 and 1 or -1
        amount = face * 100. * dir  # * 10000 / 100

        bt = BondTrade(self.books.currentIndex(),
                       self.user,
                       self.tradeDateTime.dateTime().toPyDateTime(),
                       self.settleDate.date().toPyDate(),
                       self.code.text(),
                       amount,
                       self.full.text().toDouble()[0],
                       self.ytm.text().toDouble()[0],
                       comment=self.comment.text())
        bt.toDB()

    def check_validity(self, raiseWarning=False):
        return True