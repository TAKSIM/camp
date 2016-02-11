#-*- coding:utf8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf-8"))

class DateDelegate(QItemDelegate):
    def __init__(self):
        super(DateDelegate,self).__init__()
        pass

    def createEditor(self,parent,option,index):
        editor = QDateTimeEdit(parent)
        editor.setDisplayFormat("yyyy-MM-dd")
        editor.setCalendarPopup(True)
        editor.installEventFilter(self)
        return editor

    def setEditorData(self,editor,index):
        dateStr = index.model().data(index).toString()
        date = QDate.fromString(dateStr,Qt.ISODate)
        edit = editor
        edit.setDate(date)

    def setModelData(self,editor,model,index):
        date = editor.date()
        model.setData(index,QVariant(date.toString(Qt.ISODate)))

class ComboDelegate(QItemDelegate):
    def __init__(self):
        super(ComboDelegate,self).__init__()
        pass

    def createEditor(self,parent,QStyleOptionViewItem,QModelIndex):
        editor = QComboBox(parent)
        editor.addItem(self.tr("工人"))
        editor.addItem(self.tr("农民"))
        editor.installEventFilter(self)
        return editor

    def setEditorData(self,editor,index):
        str = index.model().data(index).toString()
        i = editor.findText(str)
        editor.setCurrentIndex(i)

    def setModelData(self,editor,model,index):
        str = editor.currentText()
        model.setData(index,str)

    def updateEditorGeometry(self,editor,option,index):
        editor.setGeometry(option.rect)

class SpinDelegate(QItemDelegate):
    def __init__(self):
        super(SpinDelegate,self).__init__()
        pass
    def createEditor(self,parent,QStyleOptionViewItem,QModelIndex):
        editor = QSpinBox(parent)
        editor.installEventFilter(self)
        editor.setMinimum(0)
        editor.setMaximum(10000)
        return editor

    def setEditorData(self,editor,index):
        value = index.model().data(index,Qt.EditRole).toInt()[0]

        editor.setValue(value)

    def setModelData(self,editor,model,index):
        value = editor.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self,editor,option,index):
        editor.setGeometry(option.rect)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    model = QStandardItemModel(4,4)
    tableview = QTableView()
    tableview.setModel(model)

    dateDelegate = DateDelegate()
    comboDelegate = ComboDelegate()
    spinDelegate = SpinDelegate()

    tableview.setItemDelegateForColumn(1,dateDelegate)
    tableview.setItemDelegateForColumn(2,comboDelegate)
    tableview.setItemDelegateForColumn(3,spinDelegate)

    model.setHeaderData(0,Qt.Horizontal,model.tr("Name"))
    model.setHeaderData(1,Qt.Horizontal,model.tr("Birthday"))
    model.setHeaderData(2,Qt.Horizontal,model.tr("Job"))
    model.setHeaderData(3,Qt.Horizontal,model.tr("Income"))

    file = QFile("./image/data.tab")
    if file.open(QFile.ReadOnly|QFile.Text):
        stream = QTextStream(file)
        model.removeRows(0,model.rowCount(QModelIndex()),QModelIndex())
        row = 0

        while True:
            line = stream.readLine()
            if line.isEmpty() is False:
                model.insertRows(row,1,QModelIndex())
                pieces = line.split(",",QString.SkipEmptyParts)

                model.setData(model.index(row,0,QModelIndex()),pieces.takeAt(0))
                model.setData(model.index(row,1,QModelIndex()),pieces.takeAt(0))
                model.setData(model.index(row,2,QModelIndex()),pieces.takeAt(0))
                model.setData(model.index(row,3,QModelIndex()),pieces.takeAt(0))
                row+=1

            else:
                break

    file.close()

    tableview.setWindowTitle(tableview.tr("Delegate"))
    tableview.show()

    sys.exit(app.exec_())
