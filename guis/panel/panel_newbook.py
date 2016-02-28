# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql
import datetime
from panel_base import PanelBase


class NewBook(PanelBase):
    def __init__(self, parent=None):
        super(NewBook, self).__init__(parent)
        self.setWindowTitle(u'新账簿')
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'账簿全称'),0,0,1,1)
        self.fullname = QtGui.QLineEdit()
        layout.addWidget(self.fullname, 0,1,1,1)
        layout.addWidget(QtGui.QLabel(u'账簿简称'), 1,0,1,1)
        self.shortname = QtGui.QLineEdit()
        layout.addWidget(self.shortname, 1,1,1,1)
        layout.addWidget(QtGui.QLabel(u'主交易员'),2,0,1,1)
        self.trader = QtGui.QComboBox()
        q = QtSql.QSqlQuery('SELECT NAME FROM USERS WHERE ROLE=1')
        users=[]
        while q.next():
            users.append(q.value(0).toString())
        self.trader.addItems(users)
        layout.addWidget(self.trader,2,1,1,1)
        layout.addWidget(QtGui.QLabel(u'万得代码'),3,0,1,1)
        self.windcode = QtGui.QLineEdit()
        layout.addWidget(self.windcode, 3,1,1,1)
        layout.addWidget(QtGui.QLabel(u'起始日'), 4,0,1,1)
        self.startdate = QtGui.QDateEdit(datetime.date.today())
        self.startdate.setCalendarPopup(True)
        layout.addWidget(self.startdate,4,1,1,1)
        layout_okcancel = QtGui.QHBoxLayout()
        layout_okcancel.addWidget(self.cancel)
        layout_okcancel.addWidget(self.ok)
        layout.addLayout(layout_okcancel,5,0,1,2)
        self.setLayout(layout)

    def toDB(self):
        fullname=self.fullname.text()
        shortname = self.shortname.text()
        windcode = self.windcode.text()
        user = self.trader.currentText()
        startdate = self.startdate.date().toPyDate()
        userid = None
        q = QtSql.QSqlQuery("""SELECT ID FROM USERS WHERE NAME='%s'""" % user)
        while q.next():
            userid = q.value(0).toString()
        if userid:
            try:
                q.exec_("""INSERT INTO BOOKS VALUES ('%s','%s','%s','%s','%s',)""" % (shortname, fullname, startdate, userid, windcode))
                QtSql.QSqlDatabase().commit()
            except Exception, e:
                print e.message
                QtSql.QSqlDatabase().rollback()
        else:
            QtGui.QMessageBox.warning(self, u'错误', u'无法查到交易员信息')
