# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql
import datetime
from panel_base import PanelBase
from trade import DepoTrade


class NewDepo(PanelBase):
    def __init__(self, user, parent=None):
        super(NewDepo, self).__init__(parent=parent)
        self.setWindowTitle(u'同业存款')
        self.user = user
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'交易日'), 0, 0, 1, 1)
        self.tradeDateTime = QtGui.QDateTimeEdit(datetime.datetime.now())
        self.tradeDateTime.setCalendarPopup(True)
        layout.addWidget(self.tradeDateTime, 0, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'账簿'), 1, 0, 1, 1)
        q = QtSql.QSqlQuery('SELECT NAME_CN FROM BOOKS ORDER BY ID')
        books = []
        while q.next():
            books.append(q.value(0).toString())
        self.books = QtGui.QComboBox()
        self.books.addItems(books)
        layout.addWidget(self.books, 1, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'金额'), 2, 0, 1, 1)
        self.amount = QtGui.QLineEdit()
        self.amount.setValidator(QtGui.QDoubleValidator())
        self.amount.textChanged.connect(self.update_total)
        layout.addWidget(self.amount, 2, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'收益率(%)'), 3, 0, 1, 1)
        self.rtn = QtGui.QLineEdit()
        self.rtn.setValidator(QtGui.QDoubleValidator())
        self.rtn.textChanged.connect(self.update_total)
        layout.addWidget(self.rtn, 3, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'到期日'), 4, 0, 1, 1)
        self.expdate = QtGui.QDateEdit(datetime.date.today())
        self.expdate.setCalendarPopup(True)
        self.expdate.dateChanged.connect(self.update_total)
        layout.addWidget(self.expdate, 4, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'计息方式'), 5, 0, 1, 1)
        self.dcc = QtGui.QComboBox()
        self.dcc.addItems(['Act/360'])
        layout.addWidget(self.dcc, 5, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'到期金额'), 6, 0, 1, 1)
        self.total = QtGui.QLineEdit()
        self.total.setReadOnly(True)
        self.total.setValidator(QtGui.QDoubleValidator())
        layout.addWidget(self.total, 6, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'交易对手'), 7, 0, 1, 1)
        self.comment = QtGui.QLineEdit()
        layout.addWidget(self.comment, 7, 1, 1, 1)
        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(self.ok)
        btnLayout.addWidget(self.cancel)
        layout.addLayout(btnLayout, 8, 0, 1, 2)
        self.setLayout(layout)

    def toDB(self):
        dt = DepoTrade(book=self.books.currentIndex(),
                       trader=self.user,
                       tradeDateTime=self.tradeDateTime.dateTime().toPyDateTime(),
                       amount=self.amount.text().toDouble()[0],
                       rtn = self.rtn.text().toDouble()[0],
                       maturityDate=self.expdate.date().toPyDate(),
                       settledBy='',
                       comment=self.comment.text())
        dt.toDB()

    def update_total(self):
        amount, s = self.amount.text().toDouble()
        if s:
            rtn, s = self.rtn.text().toDouble()
            if s:
                startDate = self.tradeDateTime.date().toPyDate()
                endDate = self.expdate.date().toPyDate()
                if endDate > startDate:
                    self.total.setText('{:,.2f}'.format((1+(endDate-startDate).days/360.0*rtn/100.0)*amount))

    def check_validity(self, raiseWarning=False):
        if self.expdate.date().toPyDate() <= self.tradeDateTime.date().toPyDate():
            if raiseWarning: QtGui.QMessageBox.warning(self, u'错误', u'到期日必须晚于交易日')
            return False
        if self.comment.text().isEmpty():
            if raiseWarning: QtGui.QMessageBox.warning(self, u'错误', u'请在备注栏记录交易对手方')
            return False
        return True