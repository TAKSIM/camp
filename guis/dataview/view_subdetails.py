# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql, QtCore
from view_base import ViewBase, ViewBaseSet, NumberDelegate, DateDelegate


class LiabilityView(ViewBase):
    def __init__(self, parent=None):
        ViewBase.__init__(self,
            query = 'select d.EXP_DATE, '
                    'd.AMOUNT*(1+d.EXP_RETURN*(datediff(d.EXP_DATE, d.SETTLE_DATE)+1)/36500.0), '
                    'c.TYPE_NAME, '
                    'd.CLIENT_NAME, '
                    's.TYPE_NAME, '
                    'd.SUB_CODE, '
                    'd.AMOUNT, '
                    'd.EXP_RETURN, '
                    'd.SUB_DATE, '
                    'd.SETTLE_DATE, '
                    'datediff(d.EXP_DATE, d.SETTLE_DATE)+1, '
                    'e.OPS_NAME '
                    'from liability d '
                    'left outer join sale_type s on s.ID=d.SALE_TYPE '
                    'left outer join expops_type e on e.id=d.EXP_OPS '
                    'left outer join client_type c on c.id=d.CLIENT_TYPE',
            header = [u'封闭期到期日', # 0
                      u'到期本息', # 1
                      u'客户类型', # 2
                      u'委托人名称', # 3
                      u'销售类型', # 4
                      u'申请书编码', # 5
                      u'认购金额(元)', # 6
                      u'预期收益率(%)', # 7
                      u'认购日', # 8
                      u'封闭期起始日' , # 9
                      u'期限', # 10
                      u'到期操作'], # 11
            menu    = True,
            parent  = parent)

        self.sortByColumn(0, QtCore.Qt.DescendingOrder)
        nfAmt = NumberDelegate(parent=self, withComma=True, numDigits=0)
        nfPct = NumberDelegate(parent=self, withComma=False, numDigits=2)
        df = DateDelegate(parent=self)
        self.setItemDelegateForColumn(0, df)
        self.setItemDelegateForColumn(1, nfAmt)
        self.setItemDelegateForColumn(6, nfAmt)
        self.setItemDelegateForColumn(7, nfPct)
        self.setItemDelegateForColumn(8, df)
        self.setItemDelegateForColumn(9, df)

    def buildMenu(self):
        self.menu = QtGui.QMenu()
        actRemoveRow = QtGui.QAction(u'删除本条记录', self, triggered=self.removeRow)
        self.menu.addAction(actRemoveRow)

    def removeRow(self):
        rowIndex = self.currentIndex().row()
        subcode = self.model().index(rowIndex, 5).data().toString()
        reply = QtGui.QMessageBox.question(self, u'删除本条记录',
                                           u'申请书编号：%s'% subcode,
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            q = QtSql.QSqlQuery()
            try:
                q.exec_("""DELETE FROM LIABILITY WHERE SUB_CODE='%s'""" % subcode)
                QtSql.QSqlDatabase().commit()
                self.model().removeRow(rowIndex)
                self.refresh()
            except Exception, e:
                print e.message
                QtSql.QSqlDatabase().rollback()



class LiabilityViewSet(ViewBaseSet):
    def __init__(self, parent=None):
        ViewBaseSet.__init__(self, LiabilityView(), parent)