# -*- coding: utf-8 -*-
from view_base import ViewBase, ViewBaseSet, NumberDelegate
from PyQt4 import QtGui, QtSql, QtCore
import datetime


class PositionDataModel(QtSql.QSqlQueryModel):
    def __init__(self, parent=None):
        super(PositionDataModel, self).__init__(parent=parent)

    def data(self, index, int_role=None):
        if int_role == QtCore.Qt.TextAlignmentRole and index.column() in [5, 6, 7]:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        else:
            return super(PositionDataModel, self).data(index, int_role)

    def setData(self, index, value, int_role=None):
        return super(PositionDataModel, self).setData(index, value, int_role)


class PositionView(ViewBase):
    def __init__(self, sysdate, parent=None):
        super(PositionView, self).__init__(
            query=''.join(['SELECT b.NAME_CN, ',
                't.INST_CODE, ',
                's.SEC_NAME, s.SEC_TYPE, s.EXCHANGE, ',
                'SUM(t.AMOUNT), ',
                'SUM(t.AMOUNT*t.PRICE)/SUM(t.AMOUNT), ',
                'SUM(t.AMOUNT*t.PRICE) ',
                'FROM TRADES t ',
                'LEFT OUTER JOIN BOOKS b ON b.ID=t.BOOK ',
                'LEFT OUTER JOIN SECINFO s ON s.SEC_CODE=t.INST_CODE ',
                """WHERE t.TRADE_DATETIME<='%s' """ % datetime.datetime(sysdate.year, sysdate.month, sysdate.day, 23, 59, 59),
                'GROUP BY t.INST_CODE ']),
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
            datamodel=PositionDataModel(),
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
        super(PositionViewSet, self).__init__(vb=PositionView(sysdate), parent=parent)
        self.sortCol.setCurrentIndex(0)
