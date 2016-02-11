# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql, QtCore


class ViewBase(QtGui.QTableView):
    def __init__(self, query, header, parent=None):
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


class ViewBaseSet:
    def __init__(self, vb, parent=None):
        self.vb = vb

        self.sortCol = QtGui.QComboBox()
        self.sortCol.addItems(self.vb.header)
        self.sortCol.currentIndexChanged.connect(self.filterColumnChanged)

        self.sortContent = QtGui.QLineEdit()
        self.sortContent.textChanged.connect(self.filterRegExpChanged)

    def filterRegExpChanged(self):
        syntax_nr = QtCore.QRegExp.FixedString
        syntax = QtCore.QRegExp.PatternSyntax(syntax_nr)
        regExp = QtCore.QRegExp(self.sortCont.text(), QtCore.Qt.CaseInsensitive, syntax)
        self.vb.proxyModel.setFilterRegExp(regExp)

    def filterColumnChanged(self):
        self.vb.proxyModel.setFilterKeyColumn(self.sortCol.currentIndex())