# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql, QtCore
from view_base import ViewBase, ViewBaseSet

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
            header = [u'封闭期到期日',
                      u'到期本息',
                      u'客户类型',
                      u'委托人名称',
                      u'销售类型',
                      u'申请书编码',
                      u'认购金额(元)',
                      u'预期收益率(%)',
                      u'认购日',
                      u'封闭期起始日' ,
                      u'期限',
                      u'到期操作'],
            parent = parent)

        self.sortByColumn(0, QtCore.Qt.DescendingOrder)


class LiabilityViewSet(ViewBaseSet):
    def __init__(self, parent=None):
        ViewBaseSet.__init__(self, LiabilityView(), parent)