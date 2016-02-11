# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql, QtCore


class NumberDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None, withComma=True, numDigits=2):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.withComma = withComma
        self.numDigits = numDigits
        self.strformat = withComma and '{:,.%sf}' % self.numDigits or ('{:.%sf}' % self.numDigits)

    def displayText(self, QVariant, QLocale):
        v, s = QVariant.toDouble()
        return s and self.strformat.format(v) or 'NaN'


class DateDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)

    def displayText(self, QVariant, QLocale):
        v = QVariant.toDate()
        return v.toString(QtCore.Qt.ISODate)


class ViewBase(QtGui.QTableView):
    def __init__(self, query, header, menu=False, parent=None):
        QtGui.QTableView.__init__(self, parent)
        self.query = query
        self.header = header

        self.dataModel = QtSql.QSqlQueryModel()
        self.dataModel.setQuery(self.query)
        for i, h in enumerate(self.header):
            self.dataModel.setHeaderData(i, QtCore.Qt.Horizontal, h)

        self.proxyModel = QtGui.QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setSourceModel(self.dataModel)

        self.setModel(self.proxyModel)
        self.verticalHeader().hide()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtGui.QTableView.SelectRows)


        if menu:
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.showRightClickMenu)
            self.buildMenu()

    def buildMenu(self):
        raise NotImplemented()

    def showRightClickMenu(self):
        self.menu.exec_(QtGui.QCursor.pos())

    def refresh(self):
        self.dataModel.query().exec_()

class ViewBaseSet:
    def __init__(self, vb, parent=None):
        self.vb = vb

        self.sortCol = QtGui.QComboBox()
        self.sortCol.addItems(self.vb.header)
        self.sortCol.currentIndexChanged.connect(self.filterColumnChanged)

        self.sortContent = QtGui.QLineEdit()
        self.sortContent.textChanged.connect(self.filterRegExpChanged)

        self.btnRefresh = QtGui.QPushButton(u'刷新')
        self.btnRefresh.clicked.connect(self.vb.refresh)

    def filterRegExpChanged(self):
        syntax_nr = QtCore.QRegExp.FixedString
        syntax = QtCore.QRegExp.PatternSyntax(syntax_nr)
        regExp = QtCore.QRegExp(self.sortContent.text(), QtCore.Qt.CaseInsensitive, syntax)
        self.vb.proxyModel.setFilterRegExp(regExp)

    def filterColumnChanged(self):
        self.vb.proxyModel.setFilterKeyColumn(self.sortCol.currentIndex())