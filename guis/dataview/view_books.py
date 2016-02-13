# -*- coding: utf-8 -*-
from PyQt4 import QtCore
from view_base import ViewBase, ViewBaseSet, DateDelegate


class BookView(ViewBase):
    def __init__(self, parent=None):
        ViewBase.__init__(self,
                          query='SELECT b.NAME_CN, b.NAME_CN_FULL, b.START_DATE, u.NAME, b.WIND_CODE FROM BOOKS b left outer join USERS u on u.ID=b.TRADER',
                          header=[u'账簿简称', u'账簿全称', u'起始日', u'主交易员', u'万得代码'],
                          menu=False,
                          parent=parent)
        dd = DateDelegate(parent=self)
        self.setItemDelegateForColumn(2, dd)
        self.sortByColumn(2, QtCore.Qt.AscendingOrder)

class BookViewSet(ViewBaseSet):
    def __init__(self, parent=None):
        ViewBaseSet.__init__(self, BookView(), parent)