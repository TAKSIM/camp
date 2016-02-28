# -*- coding: utf-8 -*-
from panel_base import PanelBase
from PyQt4 import QtGui, QtSql
import datetime
from trade import CashTrade


class NewIB2EX(PanelBase):
    def __init__(self, sysdate, user, parent=None):
        super(NewIB2EX, self).__init__(parent=parent)
        self.setWindowTitle(u'银证转账')
        self.sysdate = sysdate
        self.user = user
        layout = QtGui.QGridLayout()
        books = []
        q = QtSql.QSqlQuery('SELECT NAME_CN FROM BOOKS ORDER BY ID')
        while q.next():
            books.append(q.value(0).toString())
        self.books = QtGui.QComboBox()
        self.books.addItems(books)
        layout.addWidget(QtGui.QLabel(u'转账日期'), 0, 0, 1, 1)
        self.settleDate = QtGui.QDateTimeEdit(datetime.datetime.now())
        self.settleDate.setCalendarPopup(True)
        layout.addWidget(self.settleDate, 0, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'账簿'), 1, 0, 1, 1)
        layout.addWidget(self.books, 1, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'转账方向'), 2, 0, 1, 1)
        self.ib2ex = QtGui.QComboBox()
        self.ib2ex.addItems([u'银行间-->交易所', u'交易所-->银行间'])
        layout.addWidget(self.ib2ex, 2, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'金额(元)'), 3, 0, 1, 1)
        self.amount = QtGui.QLineEdit()
        self.amount.setValidator(QtGui.QDoubleValidator())
        layout.addWidget(self.amount, 3, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'备注'), 4, 0, 1, 1)
        self.comment = QtGui.QLineEdit()
        layout.addWidget(self.comment, 4, 1, 1, 1)
        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(self.ok)
        btnLayout.addWidget(self.cancel)
        layout.addLayout(btnLayout, 5, 0, 1, 2)
        self.setLayout(layout)

    def toDB(self):
        amount = self.amount.text().toDouble()[0]
        ib2ex = self.ib2ex.currentIndex()==0 and -1. or 1.
        tradeDateTime = self.settleDate.dateTime().toPyDateTime()
        ctIB = CashTrade(book=self.books.currentIndex(),
                        trader=self.user,
                        tradeDateTime=tradeDateTime,
                        amount=amount * ib2ex,
                        instCode='CASH_IB',
                        refTrade='',
                        comment=self.comment.text())
        ctEX = CashTrade(book=self.books.currentIndex(),
                         trader=self.user,
                         tradeDateTime=tradeDateTime,
                         amount=-amount * ib2ex,
                         instCode='CASH_EX',
                         refTrade='',
                         comment=self.comment.text())
        ctIB.toDB()
        ctEX.toDB()

    def check_validity(self, raiseWarning=False):
        return True  # TODO: check cash limit
