# -*- coding: utf-8 -*-
from view_base import ViewBase, ViewBaseSet, NumberDelegate, DateDelegate, DateTimeDelegate
from PyQt4 import QtCore, QtGui, QtSql
import datetime


class TradeView(ViewBase):
    def __init__(self, sysdate, user, parent=None):
        ViewBase.__init__(self,
                          query='SELECT t.TRADE_DATETIME, '
                                'b.NAME_CN, '
                                'u.NAME, '
                                't.INST_CODE, '
                                's.NAME, s.SEC_TYPE, s.EXCHANGE, '
                                't.AMOUNT, '
                                't.PRICE, '
                                't.REF_YIELD, '
                                't.SETTLE_DATE, '
                                't.COMMENT, '
                                't.TRADE_ID '
                                'FROM TRADES t '
                                'LEFT OUTER JOIN BOOKS b on b.ID=t.BOOK '
                                'LEFT OUTER JOIN USERS u on u.ID=t.TRADER '
                                'LEFT OUTER JOIN SECINFO s on s.SEC_CODE=t.INST_CODE '
                                """ WHERE t.TRADE_DATETIME<='%s'""" % datetime.datetime(sysdate.year, sysdate.month, sysdate.day, 23, 59, 59),
                          header=[u'交易日', # 0
                                  u'账簿', # 1
                                  u'交易员', # 2
                                  u'代码', # 3
                                  u'名称', u'类别', u'市场', # 4 5 6
                                  u'数量', # 7
                                  u'成交全价', # 8
                                  u'收益率', # 9
                                  u'交割日', # 10
                                  u'备注', # 11
                                  u'交易编码'], # 12
                          tablename=u'交易明细',
                          datatypes='tssssssfffdss',
                          menu=True,
                          parent=parent)
        self.sysdate = sysdate
        self.user = user

        self.sortByColumn(0, QtCore.Qt.DescendingOrder)
        nfAmt = NumberDelegate(parent=self, withComma=True, numDigits=0)
        nfPct = NumberDelegate(parent=self, withComma=False, numDigits=2)
        df = DateDelegate(parent=self)
        dtf = DateTimeDelegate(parent=self)

        self.setItemDelegateForColumn(0, dtf)
        self.setItemDelegateForColumn(7, nfAmt)
        self.setItemDelegateForColumn(8, nfAmt)
        self.setItemDelegateForColumn(9, nfPct)
        self.setItemDelegateForColumn(10, df)

    def buildMenu(self):
        self.menu = QtGui.QMenu()
        actConfirmSettle = QtGui.QAction(u'确认交割', self, triggered=self.confirmSettle)
        actDeleteTrade = QtGui.QAction(u'删除此条交易', self, triggered=self.deleteTrade)
        self.menu.addAction(actConfirmSettle)
        self.menu.addAction(actDeleteTrade)

    def confirmSettle(self):
        rowIndex = self.currentIndex().row()
        tradeID = self.model().index(rowIndex, 12).data().toString()
        q = QtSql.QSqlQuery()
        try:
            query = """UPDATE TRADES SET SETTLED_BY='%s' WHERE TRADE_ID='%s'""" % (self.user.id, tradeID)
            q.exec_(query)
            #print query
            QtSql.QSqlDatabase().commit()
        except Exception, e:
            print e.message
            QtSql.QSqlDatabase().rollback()

    def deleteTrade(self):
        rowIndex = self.currentIndex().row()
        tradeID = self.model().index(rowIndex, 12).data().toString()
        q = QtSql.QSqlQuery()
        try:
            query = """DELETE FROM TRADES WHERE TRADE_ID='%s'""" % tradeID
            q.exec_(query)
            #print query
            QtSql.QSqlDatabase().commit()
            self.refresh()
        except Exception, e:
            print e.message
            QtSql.QSqlDatabase().rollback()


class TradeViewSet(ViewBaseSet):
    def __init__(self, sysdate, user, parent = None):
        ViewBaseSet.__init__(self, TradeView(sysdate, user), parent=parent)
        self.sortCol.setCurrentIndex(1)