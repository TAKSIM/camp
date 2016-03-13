# -*- coding: utf-8 -*-
from view_base import ViewBase, ViewBaseSet, NumberDelegate, DateDelegate, DateTimeDelegate, QueryModelBase
from PyQt4 import QtCore, QtGui, QtSql
import datetime
from trade import Trade


class TradeDataModel(QtSql.QSqlQueryModel):
    def __init__(self, parent=None):
        super(TradeDataModel, self).__init__(parent=parent)

    def data(self, index, int_role=None):
        if int_role == QtCore.Qt.TextAlignmentRole and index.column() in [7, 8, 9]:
            return QtCore.Qt.AlignRight
        else:
            return super(TradeDataModel, self).data(index, int_role)

    def setData(self, index, value, int_role=None):
        return super(TradeDataModel, self).setData(index, value, int_role)


class TradeView(ViewBase):
    def __init__(self, sysdate, user, parent=None):
        super(TradeView, self).__init__(
                          query='SELECT t.TRADE_DATETIME, '
                                'b.NAME_CN, '
                                'u.NAME, '
                                't.INST_CODE, '
                                's.SEC_NAME, s.SEC_TYPE, s.EXCHANGE, '
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
                          datamodel=TradeDataModel(),
                          menu=True,
                          parent=parent)
        self.sysdate = sysdate
        self.user = user

        #self.verticalHeader().setDefaultSectionSize(15)
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
        trd = Trade.fromDB(tradeID)
        if trd:
            trd.settle(self.user.id)
        else:
            QtGui.QMessageBox.warning(self, u'错误', u'无法从数据库读取该笔交易')

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
        super(TradeViewSet, self).__init__(TradeView(sysdate, user), parent=parent)
        self.sortCol.setCurrentIndex(1)