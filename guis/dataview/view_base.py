# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql, QtCore
import xlsxwriter


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

class ProgressBarDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, min_value, max_value, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent=parent)
        self.min_value = min_value
        self.max_value = max_value

    def paint(self, painter, option, index):
        item_var = index.data(QtCore.Qt.DisplayRole)
        item_str = item_var.toPyObject()
        opts = QtGui.QStyleOptionProgressBarV2()
        opts.rect = option.rect
        opts.minimum = self.min_value
        opts.maximum = self.max_value
        opts.text = '{:,.0f}'.format(item_str)
        opts.textAlignment = QtCore.Qt.AlignCenter
        opts.textVisible = True
        opts.progress = int(item_str)
        QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_ProgressBar, opts, painter)


class ViewBase(QtGui.QTableView):
    def __init__(self, query, header, tablename, datatypes, menu=False, parent=None):
        # data types: s: string, d: date, t: datetime, f: float, i: int
        QtGui.QTableView.__init__(self, parent)
        self.query = query
        self.header = header
        self.tablename = tablename
        self.datatypes = datatypes

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

    def convert_to_output(self, vtype, value):
        if vtype=='s':
            return unicode(value.toString())
        elif vtype=='d':
            return str(value.toDate().toString(QtCore.Qt.ISODate))
        elif vtype=='t':
            return str(value.toDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        elif vtype=='f':
            v, s = value.toDouble()
            return s and v or 'NaN'
        elif vtype=='i':
            v, s = value.toInt()
            return s and v or 'NaN'

    def buildMenu(self):
        raise NotImplemented()

    def showRightClickMenu(self):
        self.menu.exec_(QtGui.QCursor.pos())

    def refresh(self):
        self.dataModel.query().exec_()

    def exportToExcel(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, u'保存文件', '', 'Excel File (*.xlsx)')
        if fn != '':
            try:
                wb = xlsxwriter.Workbook(str(fn))
                ws = wb.add_worksheet(self.tablename)
                ws.write_row(0, 0, self.header)
                numCols = len(self.header)
                for i in range(self.model().rowCount()):
                    for j in range(numCols):
                        ws.write(i+1, j, self.convert_to_output(self.datatypes[j], self.model().index(i,j).data()))
                wb.close()
                QtGui.QMessageBox.about(self, u'完成', u'保存文件成功')
            except Exception, e:
                QtGui.QMessageBox.warning(self, u'错误', u'无法保存文件，请检查文件是否被占用')
                print e.message

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

        self.btnExportToExcel = QtGui.QPushButton(u'导出至Excel')
        self.btnExportToExcel.clicked.connect(self.vb.exportToExcel)

    def filterRegExpChanged(self):
        syntax_nr = QtCore.QRegExp.FixedString
        syntax = QtCore.QRegExp.PatternSyntax(syntax_nr)
        regExp = QtCore.QRegExp(self.sortContent.text(), QtCore.Qt.CaseInsensitive, syntax)
        self.vb.proxyModel.setFilterRegExp(regExp)

    def filterColumnChanged(self):
        self.vb.proxyModel.setFilterKeyColumn(self.sortCol.currentIndex())