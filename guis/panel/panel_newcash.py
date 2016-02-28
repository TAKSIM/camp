# -*- coding: utf-8 -*-
from panel_base import PanelBase
from PyQt4 import QtGui, QtSql
import datetime
from trade import CashTrade


class NewCash(PanelBase):
    def __init__(self, user, parent=None):
        PanelBase.__init__(self, parent=parent)
        self.setWindowTitle(u'现金流调整')
        self.user = user
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'日期'), 0, 0, 1, 1)
        self.settleDate = QtGui.QDateTimeEdit(datetime.datetime.now())
        self.settleDate.setCalendarPopup(True)
        layout.addWidget(self.settleDate, 0, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'账簿'), 1, 0, 1, 1)
        books = []
        q = QtSql.QSqlQuery('SELECT NAME_CN FROM BOOKS ORDER BY ID')
        while q.next():
            books.append(q.value(0).toString())
        self.books = QtGui.QComboBox()
        self.books.addItems(books)
        layout.addWidget(self.books, 1, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'账户'), 2, 0, 1, 1)
        self.account = QtGui.QComboBox()
        self.account.addItems([u'银行间账户', u'交易所账户'])
        layout.addWidget(self.account, 2, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'金额'), 3, 0, 1, 1)
        self.amount = QtGui.QLineEdit()
        self.amount.setValidator(QtGui.QDoubleValidator())
        layout.addWidget(self.amount, 3, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'原因'), 4, 0, 1, 1)
        self.comment = QtGui.QLineEdit()
        layout.addWidget(self.comment, 4, 1, 1, 1)
        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(self.ok)
        btnLayout.addWidget(self.cancel)
        layout.addLayout(btnLayout, 5, 0, 1, 2)
        self.setLayout(layout)

    def check_validity(self, raiseWarning=False):
        if self.comment.text().isEmpty():
            if raiseWarning:
                QtGui.QMessageBox.warning(self, u'提示', u'现金流调整的原因不能为空')
            return False
        # TODO: add cash position check
        return True

    def toDB(self):
        ct = CashTrade(book=self.books.currentIndex(),
                       trader=self.user,
                       tradeDateTime=self.settleDate.dateTime().toPyDateTime(),
                       amount=self.amount.text().toDouble()[0],
                       instCode=self.account.currentIndex()==0 and 'CASH_IB' or 'CASH_EX',
                       refTrade='',
                       comment=self.comment.text())
        ct.toDB()
