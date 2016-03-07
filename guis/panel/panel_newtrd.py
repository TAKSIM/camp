# -*- coding: utf-8 -*-
from panel_base import PanelBase
from PyQt4 import QtGui, QtSql, QtCore
from WindPy import *


class NewTrade(PanelBase):
    def __init__(self, user, sysdate, secinfo, dateCalc, parent=None):
        super(NewTrade, self).__init__(parent=parent)
        self.user = user
        self.sysdate = sysdate
        self.secinfo = secinfo
        self.dateCalc = dateCalc
        self.setWindowTitle(u'新交易')
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'代码'), 0, 0, 1, 1)
        self.code = QtGui.QLineEdit()
        codeComp = QtGui.QCompleter(secinfo.keys())
        codeComp.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        codeComp.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.code.setCompleter(codeComp)
        self.code.returnPressed.connect(self.updateInfo)
        layout.addWidget(self.code, 0, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'市场'), 1, 0, 1, 1)
        self.exchange = QtGui.QLineEdit()
        self.exchange.setReadOnly(True)
        layout.addWidget(self.exchange, 1, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'类别'), 2, 0, 1, 1)
        self.prdtype = QtGui.QLineEdit()
        self.prdtype.setReadOnly(True)
        layout.addWidget(self.prdtype, 2, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'名称'), 3, 0, 1, 1)
        self.secname = QtGui.QLineEdit()
        self.secname.setReadOnly(True)
        layout.addWidget(self.secname, 3, 1, 1, 1)
        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(self.ok)
        btnLayout.addWidget(self.cancel)
        layout.addLayout(btnLayout, 4, 0, 1, 2)
        self.setLayout(layout)

    def updateInfo(self):
        c = self.code.text()
        if c in self.secinfo:
            n, t, e = self.secinfo[c]
            self.secname.setText(n)
            self.prdtype.setText(t)
            self.exchange.setText(e)
        else:
            gotinfo = False
            infolist = ['sec_name', 'sec_type', 'exch_city']
            result = w.wss(unicode(c), infolist, 'tradeDate={0}'.format(format(self.sysdate, '%Y%m%d')))
            if result:
                if result.ErrorCode == 0:
                    self.secname.setText(result.Data[0][0])
                    self.prdtype.setText(result.Data[1][0])
                    self.exchange.setText(result.Data[2][0])
                    self.secinfo[c] = (self.secname.text(), self.prdtype.text(), self.exchange.text())
                    q = QtSql.QSqlQuery()
                    try:
                        q.exec_("""INSERT INTO SECINFO VALUES ('%s','%s','%s','%s')""" % (c, self.secname.text(), self.prdtype.text(), self.exchange.text()))
                        QtSql.QSqlDatabase().commit()
                        gotinfo = True
                    except Exception, e:
                        print e.message
                        QtSql.QSqlDatabase().rollback()
            if not gotinfo:
                self.secname.setText(u'未知')
                self.prdtype.setText(u'未知')
                self.exchange.setText(u'未知')

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Enter or QKeyEvent.key() == QtCore.Qt.Key_Return:
            QKeyEvent.ignore()

    def toDB(self):
        sectype = unicode(self.prdtype.text())
        if sectype in [u'国债', u'金融债', u'短期融资券', u'企债', u'资产支持证券', u'央行票据', u'普通可转债', u'存款证', u'可分离交易可转债']:
            from panel_newbond import NewBond
            nb = NewBond(self.user, self.sysdate, self.code.text(), self.dateCalc)
            if nb.exec_():
                pass
        elif sectype in [u'国债回购', u'企债回购', u'买断式回购']:
            pass
        elif sectype == u'开放式基金':
            pass
        elif sectype == u'普通股':
            QtGui.QMessageBox.warning(self, u'错误', u'普通股交易暂未开通')
        else:
            QtGui.QMessageBox.warning(self, u'错误', u'暂未支持此类证券的交易，请联系系统管理员')

