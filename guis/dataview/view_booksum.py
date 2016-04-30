# -*- coding: utf-8 -*-
from view_base import ViewBase, ViewBaseSet, NumberDelegate
from PyQt4 import QtGui, QtSql, QtCore
import datetime
from guis.settings import ColorHighlightText

class PositionDataModel(QtSql.QSqlQueryModel):
    def __init__(self, sysdate, parent=None):
        super(PositionDataModel, self).__init__(parent=parent)
        self.asOfDate = sysdate

    def data(self, index, int_role=None):
        if int_role == QtCore.Qt.TextAlignmentRole and index.column() in [5, 6, 7]:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        elif int_role == QtCore.Qt.BackgroundColorRole:
            if self.data(self.index(index.row(), 8), QtCore.Qt.DisplayRole).toDate().toPyDate() <= self.asOfDate:
                return ColorHighlightText

        return super(PositionDataModel, self).data(index, int_role)

    def setData(self, index, value, int_role=None):
        return super(PositionDataModel, self).setData(index, value, int_role)


class PositionView(ViewBase):
    def __init__(self, sysdate, parent=None):
        super(PositionView, self).__init__(
            header=[u'账簿',  # 0
                    u'代码',  # 1
                    u'名称',  # 2
                    u'类别',  # 3
                    u'市场',  # 4
                    u'数量',  # 5
                    u'平均价格',  # 6
                    u'总成本',  # 7
                    u'到期日'],  # 8
            tablename=u'持仓',
            datatypes='sssssfffd',
            asOfDate=sysdate,
            datamodel=PositionDataModel(sysdate),
            menu=True,
            parent=parent
        )
        nfAmt = NumberDelegate(parent=self, withComma=True, numDigits=0)
        self.setItemDelegateForColumn(5, nfAmt)
        self.setItemDelegateForColumn(7, nfAmt)

    def date_update(self, newDate):
        self.asOfDate = newDate
        self.dataModel.asOfDate = newDate
        self.build_query()
        self.refresh()

    def buildMenu(self):
        self.menu = QtGui.QMenu()
        actConfirmExpSettle = QtGui.QAction(u'确认到期交割', self, triggered=self.confirmExpSettle)
        self.menu.addAction(actConfirmExpSettle)

    def build_query(self):
        self.query=''.join(['SELECT b.NAME_CN, ',
                't.INST_CODE, ',
                's.SEC_NAME, s.SEC_TYPE, s.EXCHANGE, ',
                'SUM(t.AMOUNT), ',
                'SUM(t.AMOUNT*t.PRICE)/SUM(t.AMOUNT), ',
                'SUM(t.AMOUNT*t.PRICE), ',
                't.MATURITY_DATE ',
                'FROM TRADES t ',
                'LEFT OUTER JOIN BOOKS b ON b.ID=t.BOOK ',
                'LEFT OUTER JOIN SECINFO s ON s.SEC_CODE=t.INST_CODE ',
                """WHERE t.TRADE_DATETIME<='%s' AND t.EXP_SETTLED_BY IS NULL """ % datetime.datetime(self.asOfDate.year, self.asOfDate.month, self.asOfDate.day, 23, 59, 59),
                'GROUP BY t.BOOK, t.INST_CODE ',
                'HAVING SUM(t.AMOUNT)<>0'])

    def confirmExpSettle(self):
        rowIndex = self.currentIndex().row()
        code = self.model().index(rowIndex, 1).data().toString()
        if str(code) in ['CASH_EX', 'CASH_IB']:
            QtGui.QMessageBox.warning(self, u'提示', u'现金头寸不涉及到期交割')
        else:
            name = self.model().index(rowIndex, 2).data().toString()
            if QtGui.QMessageBox.question(self, u'到期交割', u'确认 <b>'+unicode(name)+u'</b> 到期交割？') == QtGui.QMessageBox.Yes:
                mkt = self.model().index(rowIndex, 4).data().toString()
                cash_code = mkt==QtCore.QString(u'银行间债券') and 'CASH_IB' or 'CASH_EX'



class PositionViewSet(ViewBaseSet):
    def __init__(self, sysdate, parent=None):
        super(PositionViewSet, self).__init__(vb=PositionView(sysdate), parent=parent)
        self.sortCol.setCurrentIndex(0)
