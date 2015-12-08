# -*- coding: utf-8 -*-
from WindPy import *
from PyQt4 import QtGui, QtSql
import datetime

class DepoPanel(QtGui.QDialog):
    def __init__(self, books, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'同业存款')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.setFixedSize(200,250)

        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'交易日'), 0,0,1,1)
        self.tradeDate = QtGui.QDateEdit(datetime.datetime.today())
        self.tradeDate.setCalendarPopup(True)
        layout.addWidget(self.tradeDate, 0, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'账簿'), 1, 0, 1, 1)
        dbBooks = QtGui.QComboBox()
        dbBooks.addItems([b.name_cn_short for b in books])
        layout.addWidget(dbBooks, 1, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'规模（万元）'), 2, 0, 1, 1)
        self.amount = QtGui.QLineEdit()
        layout.addWidget(self.amount, 2, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'收益率（%）'), 3, 0, 1, 1)
        self.price = QtGui.QLineEdit()
        layout.addWidget(self.price, 3, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'到期日'),4,0,1,1)
        self.matDate = QtGui.QDateEdit(datetime.datetime.today())
        self.matDate.setCalendarPopup(True)
        layout.addWidget(self.matDate,4,1,1,2)
        layout.addWidget(QtGui.QLabel(u'计息方式'),5,0,1,1)
        self.dcc = QtGui.QComboBox()
        self.dcc.addItem('Act/360')
        layout.addWidget(self.dcc, 5, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'备注'), 6,0,1,1)
        self.comment = QtGui.QLineEdit()
        layout.addWidget(self.comment, 6,1,1,2)

        buttonLayout = QtGui.QHBoxLayout()
        self.ok = QtGui.QPushButton(u'确定')
        self.ok.clicked.connect(self.bookToDB)
        self.cancel = QtGui.QPushButton(u'取消')
        self.cancel.clicked.connect(self.close)
        buttonLayout.addWidget(self.ok)
        buttonLayout.addWidget(self.cancel)
        layout.addLayout(buttonLayout,7,0,1,3)

        self.setLayout(layout)

    def bookToDB(self):
        if self.matDate <= self.tradeDate:
            QtGui.QMessageBox.about(self, u"错误", u"到期日需要晚于交易日")
        else:
            q = QtSql.QSqlQuery()
            try:
                q.exec_('')
                QtSql.QSqlDatabase().commit()
                self.accept()
            except Exception, e:
                print e.message
                QtSql.QSqlDatabase().rollback()

class MmfPanel(QtGui.QDialog):
    def __init__(self, books, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'货币基金')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.setFixedSize(200,250)

        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'交易日'),0,0,1,1)
        self.tradeDate = QtGui.QDateEdit(datetime.datetime.today())
        self.tradeDate.setCalendarPopup(True)
        layout.addWidget(self.tradeDate,0,1,1,2)
        layout.addWidget(QtGui.QLabel(u'账簿'),1,0,1,1)
        self.books = QtGui.QComboBox()
        self.books.addItems([b.name_cn_short for b in books])
        layout.addWidget(self.books, 1,1,1,2)
        layout.addWidget(QtGui.QLabel(u'基金代号'),2,0,1,1)
        self.code = QtGui.QLineEdit()
        self.code.textChanged.connect(self.updateName)
        layout.addWidget(self.code,2,1,1,2)
        layout.addWidget(QtGui.QLabel(u'基金名称'),3,0,1,1)
        self.name = QtGui.QLineEdit()
        self.name.setEchoMode(False)
        layout.addWidget(self.name,3,1,1,2)
        layout.addWidget(QtGui.QLabel(u'规模（万元）'),4,0,1,1)
        self.amount = QtGui.QLineEdit()
        layout.addWidget(self.amount,4,1,1,2)
        layout.addWidget(QtGui.QLabel(u'备注'),5,0,1,1)
        self.comment = QtGui.QLineEdit()
        layout.addWidget(self.comment,5,1,1,2)

        buttonLayout = QtGui.QHBoxLayout()
        self.ok = QtGui.QPushButton(u'确定')
        self.cancel = QtGui.QPushButton(u'取消')
        self.cancel.clicked.connect(self.close)
        buttonLayout.addWidget(self.ok)
        buttonLayout.addWidget(self.cancel)
        layout.addLayout(buttonLayout,6,0,1,3)

        self.setLayout(layout)

    def updateName(self):
        code = str(self.code.text())
        name = w.wss(code, 'Name', 'rptDate={0}'.format(datetime.datetime.today(), '%Y%m%d'))


class BondPanel(QtGui.QDialog):
    def __init__(self, books, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'货币基金')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))

        layout = QtGui.QGridLayout()

        layout.addWidget(QtGui.QLabel(u'交易日'), 0, 0, 1, 1)
        self.tradeDate = QtGui.QDateEdit(datetime.datetime.today())
        layout.addWidget(self.tradeDate, 0, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'账簿'), 0, 3, 1, 1)
        self.books = QtGui.QComboBox()
        self.books.addItems([b.name_cn_short for b in books])
        layout.addWidget(self.books, 0, 4, 1, 2)
        layout.addWidget(QtGui.QLabel(u'代码'), 1, 0, 1, 1)
        self.code = QtGui.QLineEdit()
        layout.addWidget(self.code, 1, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(u'名称'), 1, 3, 1, 1)
        self.name = QtGui.QLineEdit()
        self.setEnabled(False)
        layout.addWidget(self.name, 1, 4, 1, 2)


        self.setLayout(layout)

# class BondPanel(QtGui.QDialog):
#     def __init__(self, parent=None):
#         QtGui.QDialog.__init__(self, parent)
#         self.setWindowTitle(u'债券查询交易')
#         self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
#         self.setFont(QtGui.QFont('SimHei',12, QtGui.QFont.Bold))
#         pe = QtGui.QPalette()
#         pe.setColor(QtGui.QPalette.WindowText, QtGui.QColor(219,123,37))
#         pe.setColor(QtGui.QPalette.Background, QtGui.QColor(10,15,14))
#         self.setPalette(pe)
#
#         #self.setFixedSize(300,250)
#         layout = QtGui.QHBoxLayout()
#         srcLayout = QtGui.QVBoxLayout()
#         trdLayout = QtGui.QVBoxLayout()
#         layout.addLayout(srcLayout)
#         layout.addLayout(trdLayout)
#         self.setLayout(layout)
#
#         self.buildID()
#         self.buildInfo()
#         srcLayout.addWidget(self.gbID)
#         srcLayout.addWidget(self.gbInfo)
#
#         self.buildPrice()
#         self.buildTrade()
#         trdLayout.addWidget(self.gbPrice)
#         trdLayout.addWidget(self.gbTrade)
#
#         self.setLayout(layout)
#
#     def buildID(self):
#         self.gbID = QtGui.QGroupBox(u'代码/名称')
#
#         layout = QtGui.QHBoxLayout()
#         layout.addWidget(QtGui.QLabel(u'代码'))
#         self.leID = QtGui.QLineEdit()
#         layout.addWidget(self.leID)
#         layout.addWidget(QtGui.QLabel(u'名称'))
#         self.leName = QtGui.QLineEdit()
#         layout.addWidget(self.leName)
#
#         self.gbID.setLayout(layout)
#
#     def buildInfo(self):
#         self.gbInfo = QtGui.QGroupBox(u'债券信息')
#
#         layout = QtGui.QGridLayout()
#         layout.addWidget(QtGui.QLabel(u'发行人'),0,0,1,1)
#         self.leIssuer = QtGui.QLineEdit()
#         layout.addWidget(self.leIssuer,0,1,1,3)
#         layout.addWidget(QtGui.QLabel(u'行业'),1,0,1,1)
#         self.leInd = QtGui.QLineEdit()
#         layout.addWidget(self.leInd,1,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'类别'),1,2,1,1)
#         self.leType = QtGui.QLineEdit()
#         layout.addWidget(self.leType,1,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'到期日'),2,0,1,1)
#         self.leMat = QtGui.QDateEdit()
#         self.leMat.setCalendarPopup(True)
#         layout.addWidget(self.leMat,2,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'久期'),2,2,1,1)
#         self.leDur = QtGui.QLineEdit()
#         layout.addWidget(self.leDur,2,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'票息(%)'),3,0,1,1)
#         self.leCoupon = QtGui.QLineEdit()
#         layout.addWidget(self.leCoupon,3,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'付息频率'),3,2,1,1)
#         self.leCouponFreq = QtGui.QLineEdit()
#         layout.addWidget(self.leCouponFreq,3,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'中债估值'),4,0,1,1)
#         self.leValue = QtGui.QLineEdit()
#         layout.addWidget(self.leValue,4,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'估值日'),4,2,1,1)
#         self.leVD = QtGui.QDateEdit()
#         layout.addWidget(self.leVD,4,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'主体评级'),5,0,1,1)
#         self.leIssuerRating = QtGui.QLineEdit()
#         layout.addWidget(self.leIssuerRating,5,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'债项评级'),5,2,1,1)
#         self.leSecRating = QtGui.QLineEdit()
#         layout.addWidget(self.leSecRating,5,3,1,1)
#
#         self.gbInfo.setLayout(layout)
#
#     def buildPrice(self):
#         self.gbPrice = QtGui.QGroupBox(u'价格试算')
#
#         layout = QtGui.QGridLayout()
#         layout.addWidget(QtGui.QLabel(u'到期收益率(%)'),0,0,1,1)
#         self.leYTM = QtGui.QLineEdit()
#         layout.addWidget(self.leYTM,0,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'全价'),0,2,1,1)
#         self.leDP = QtGui.QLineEdit()
#         layout.addWidget(self.leDP,0,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'净价'),1,0,1,1)
#         self.leCP = QtGui.QLineEdit()
#         layout.addWidget(self.leCP,1,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'T+'),1,2,1,1)
#         self.DTS = QtGui.QLineEdit()
#         layout.addWidget(self.DTS,1,3,1,1)
#         layout.addWidget(QtGui.QLabel(u'交易日'),2,0,1,1)
#         self.dpTradeDate = QtGui.QDateEdit(datetime.date.today())
#         layout.addWidget(self.dpTradeDate, 2,1,1,1)
#         layout.addWidget(QtGui.QLabel(u'交割日'),2,2,1,1)
#         self.dpSettleDate = QtGui.QDateEdit(datetime.date.today())
#         layout.addWidget(self.dpSettleDate,2,3,1,1)
#
#         self.gbPrice.setLayout(layout)
#
#     def buildTrade(self):
#         self.gbTrade = QtGui.QGroupBox(u'交易')
#
#         layout = QtGui.QGridLayout()
#
#
#         self.gbTrade.setLayout(layout)
#
#     def trade(self):
#         print 'hello'

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    m = BondPanel()
    m.show()
    sys.exit(app.exec_())
