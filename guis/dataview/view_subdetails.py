# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql, QtCore
from view_base import ViewBase, ViewBaseSet, NumberDelegate, DateDelegate, ProgressBarDelegate, ColorHighlightText
from guis.panel.panel_newsub import ConfirmSub


class SubDataModel(QtSql.QSqlQueryModel):
    def __init__(self, parent=None):
        super(SubDataModel, self).__init__(parent=parent)

    def data(self, index, int_role=None):
        if int_role == QtCore.Qt.TextAlignmentRole and index.column() in [2, 7, 8, 10]:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        elif int_role == QtCore.Qt.BackgroundColorRole:
            if self.data(self.index(index.row(), 12), QtCore.Qt.DisplayRole).toString().isEmpty():  # if settle date is not confirmed
                return ColorHighlightText

        return super(SubDataModel, self).data(index, int_role)

    def setData(self, index, value, int_role=None):
        return super(SubDataModel, self).setData(index, value, int_role)


class LiabilityView(ViewBase):
    def __init__(self, sysdate, user, parent=None):
        super(LiabilityView, self).__init__(
            header = [u'认购日', # 0
                      u'封闭期到期日', # 1
                      u'到期本息', # 2
                      u'客户类型', # 3
                      u'委托人名称', # 4
                      u'销售类型', # 5
                      u'申请书编码', # 6
                      u'认购金额(元)', # 7
                      u'预期收益率(%)', # 8
                      u'封闭期起始日' , # 9
                      u'期限', # 10
                      u'备注', # 11
                      u'到账日' # 12
                      ],
            tablename=u'申购信息',
            datatypes='ddfssssffdisd',
            datamodel=SubDataModel(),
            asOfDate=sysdate,
            menu=True,
            parent=parent)
        self.user = user

        self.sortByColumn(0, QtCore.Qt.DescendingOrder)
        nfAmt = NumberDelegate(parent=self, withComma=True, numDigits=0)
        nfPct = NumberDelegate(parent=self, withComma=False, numDigits=2)
        df = DateDelegate(parent=self)
        pb = ProgressBarDelegate(0,600000000, parent=self)

        self.setItemDelegateForColumn(0, df)
        self.setItemDelegateForColumn(1, df)
        self.setItemDelegateForColumn(2, pb)
        self.setItemDelegateForColumn(7, nfAmt)
        self.setItemDelegateForColumn(8, nfPct)
        self.setItemDelegateForColumn(9, df)
        self.setItemDelegateForColumn(12, df)

    def build_query(self):
        self.query = ''.join([  'select d.SUB_DATE,',
                                'd.EXP_DATE, ',
                                'd.AMOUNT*(1+d.EXP_RETURN*(datediff(d.EXP_DATE, d.SETTLE_DATE)+1)/36500.0), ',
                                'c.TYPE_NAME, ',
                                'd.CLIENT_NAME, ',
                                's.TYPE_NAME, ',
                                'd.SUB_CODE, ',
                                'd.AMOUNT, ',
                                'd.EXP_RETURN, ',
                                'd.SETTLE_DATE, ',
                                'datediff(d.EXP_DATE, d.SETTLE_DATE)+1, ',
                                'd.COMMENT, ',
                                'd.CONFIRM_DATE ',
                                'from liability d ',
                                'left outer join sale_type s on s.ID=d.SALE_TYPE ',
                                'left outer join client_type c on c.id=d.CLIENT_TYPE',
                                """ WHERE EXP_DATE>='%s'""" % self.asOfDate])

    def buildMenu(self):
        self.menu = QtGui.QMenu()
        actRemoveRow = QtGui.QAction(u'删除本条记录', self, triggered=self.removeRow)
        actConfirm = QtGui.QAction(u'确认到账', self, triggered=self.confirmSub)
        self.menu.addAction(actConfirm)
        self.menu.addAction(actRemoveRow)

    def removeRow(self):
        rowIndex = self.currentIndex().row()
        subcode = self.model().index(rowIndex, 6).data().toString()
        confdate = self.model().index(rowIndex, 12).data().toString()
        if confdate.isEmpty():
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
        else:
            QtGui.QMessageBox.warning(self, u'非常规操作', u'资金已经确认到账（申请书编号：%s，到账日：%s），若确实需要删除此条记录，请联系系统管理员' % (subcode, confdate))

    def confirmSub(self):
        rowIndex = self.currentIndex().row()
        subcode = self.model().index(rowIndex, 6).data().toString()
        confdate = self.model().index(rowIndex, 12).data().toString()
        if confdate.isEmpty():
            startdate = self.model().index(rowIndex, 9).data().toDate().toPyDate()
            cs = ConfirmSub(subcode, self.user, startdate)
            if cs.exec_():
                self.refresh()
        else:
            QtGui.QMessageBox.warning(self, u'非常规操作', u'资金已经确认到账（申请书编号：%s，到账日：%s），若确实需要调整到账日及现金流，请联系系统管理员' % (subcode, confdate))
        

class LiabilityViewSet(ViewBaseSet):
    def __init__(self, sysdate, user, parent=None):
        super(LiabilityViewSet, self).__init__(LiabilityView(sysdate, user), parent)
        self.cbShowLiveOnly = QtGui.QCheckBox(u'只显示未到期')
        self.cbShowLiveOnly.setChecked(True)
        self.cbShowLiveOnly.stateChanged.connect(self.showlive_switch)
        self.sortCol.setCurrentIndex(3)

    def showlive_switch(self):
        constraint = """ WHERE EXP_DATE>='%s'""" % self.vb.sysdate
        if self.cbShowLiveOnly.isChecked():
            self.vb.query = self.vb.query + constraint
        else:
            self.vb.query = self.vb.query[:len(self.vb.query)-len(constraint)]
        self.vb.dataModel.setQuery(self.vb.query)

