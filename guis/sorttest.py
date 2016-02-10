# -*- coding: utf-8 -*-
import datetime
import sip

from PyQt4 import QtCore, QtGui
TIME, TRADER, MESSAGE, BOOK = range(4)

class SortFilterProxyModel(QtGui.QSortFilterProxyModel):
    def filterAcceptsRow(self, sourceRow, sourceParent):
        # Do we filter for the date column?
        if self.filterKeyColumn() == TIME:
            # Fetch datetime value.
            index = self.sourceModel().index(sourceRow, TIME, sourceParent)
            data = self.sourceModel().data(index)

            # Return, if regExp match in displayed format.QtCore.Qt.DefaultLocaleShortDate
            return (self.filterRegExp().indexIn(data.toString()) >= 0)


        # Not our business.
        return super(SortFilterProxyModel, self).filterAcceptsRow(sourceRow, sourceParent)

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.proxyModel = SortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyGroupBox = QtGui.QGroupBox("Sorted/Filtered Model")

        self.proxyView = QtGui.QTreeView()
        self.proxyView.setRootIsDecorated(False)
        self.proxyView.setAlternatingRowColors(True)
        self.proxyView.setModel(self.proxyModel)
        self.proxyView.setSortingEnabled(True)

        self.filterPatternLineEdit = QtGui.QLineEdit()
        self.filterPatternLabel = QtGui.QLabel("&Filter pattern:")
        self.filterPatternLabel.setBuddy(self.filterPatternLineEdit)

        self.filterColumnComboBox = QtGui.QComboBox()
        self.filterColumnComboBox.addItem("Time")
        self.filterColumnComboBox.addItem("Trader")
        self.filterColumnComboBox.addItem("Message")
        self.filterColumnComboBox.addItem("Book")
        self.filterColumnLabel = QtGui.QLabel("Filter &column:")
        self.filterColumnLabel.setBuddy(self.filterColumnComboBox)

        self.filterPatternLineEdit.textChanged.connect(self.filterRegExpChanged)
        self.filterColumnComboBox.currentIndexChanged.connect(self.filterColumnChanged)

        proxyLayout = QtGui.QGridLayout()
        proxyLayout.addWidget(self.proxyView, 0, 0, 1, 3)
        proxyLayout.addWidget(self.filterPatternLabel, 1, 0)
        proxyLayout.addWidget(self.filterPatternLineEdit, 1, 1, 1, 2)
        proxyLayout.addWidget(self.filterColumnLabel, 2, 0)
        proxyLayout.addWidget(self.filterColumnComboBox, 2, 1, 1, 2)
        self.setLayout(proxyLayout)

        self.setWindowTitle("Basic Sort/Filter Model")
        self.resize(500, 450)

        self.proxyView.sortByColumn(TIME, QtCore.Qt.AscendingOrder)
        self.filterColumnComboBox.setCurrentIndex(TIME)

    def filterColumnChanged(self):
        self.proxyModel.setFilterKeyColumn(self.filterColumnComboBox.currentIndex())

    def filterRegExpChanged(self):
        syntax_nr = QtCore.QRegExp.FixedString
        syntax = QtCore.QRegExp.PatternSyntax(syntax_nr)
        regExp = QtCore.QRegExp(self.filterPatternLineEdit.text(),
                QtCore.Qt.CaseInsensitive, syntax)
        self.proxyModel.setFilterRegExp(regExp)

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)

def addMessage(model, time, trader, message, book):
    model.insertRow(0)
    model.setData(model.index(0, TIME), time)
    model.setData(model.index(0, TRADER), trader)
    model.setData(model.index(0, MESSAGE), message)
    model.setData(model.index(0, BOOK), book)

def createMailModel(parent):
    model = QtGui.QStandardItemModel(0, 4, parent)

    model.setHeaderData(TIME, QtCore.Qt.Horizontal, u"时间")
    model.setHeaderData(TRADER, QtCore.Qt.Horizontal, u"交易员")
    model.setHeaderData(MESSAGE, QtCore.Qt.Horizontal, u"信息")
    model.setHeaderData(BOOK, QtCore.Qt.Horizontal, u"帐簿")

    addMessage(model, QtCore.QDateTime(QtCore.QDate(2006, 12, 31), QtCore.QTime(17, 3)), u"何伟", "Test trade open", u'映雪')
    addMessage(model, QtCore.QDateTime(QtCore.QDate(2007,10,11),QtCore.QTime(12,12)), u'高固', 'Test trade settle', u'易方达专户')

    return model

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.setSourceModel(createMailModel(window))
    window.show()
    sys.exit(app.exec_())
