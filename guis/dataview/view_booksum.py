# -*- coding: utf-8 -*-
from view_base import ViewBase, ViewBaseSet, NumberDelegate
from PyQt4 import QtGui
import datetime


class PositionView(ViewBase):
    def __init__(self, sysdate, parent=None):
        ViewBase.__init__(self,
            query='SELECT b.NAME_CN, '
                't.INST_CODE, '
                's.NAME, s.SEC_TYPE, s.EXCHANGE, '
                'SUM(t.AMOUNT), '
                'SUM(t.AMOUNT*t.PRICE)/SUM(t.AMOUNT), '
                'SUM(t.AMOUNT*t.PRICE) '
                'FROM TRADES t '
                'LEFT OUTER JOIN BOOKS b ON b.ID=t.BOOK '
                'LEFT OUTER JOIN SECINFO s ON s.SEC_CODE=t.INST_CODE '
                """WHERE t.TRADE_DATETIME<='%s'""" % datetime.datetime(sysdate.year, sysdate.month, sysdate.day, 23, 59, 59),
            header=[u'账簿',  # 0
                    u'代码',  # 1
                    u'名称',  # 2
                    u'类别',  # 3
                    u'市场',  # 4
                    u'数量',  # 5
                    u'平均价格',  # 6
                    u'总成本'],  # 7
            tablename=u'持仓',
            datatypes='sssssfff',
            menu=True,
            parent=parent
        )
        self.sysdate = sysdate
        nfAmt = NumberDelegate(parent=self, withComma=True, numDigits=0)
        self.setItemDelegateForColumn(5, nfAmt)
        self.setItemDelegateForColumn(7, nfAmt)

    def buildMenu(self):
        self.menu = QtGui.QMenu()


class PositionViewSet(ViewBaseSet):
    def __init__(self, sysdate, parent=None):
        ViewBaseSet.__init__(self, vb=PositionView(sysdate), parent=parent)
        self.sortCol.setCurrentIndex(0)
