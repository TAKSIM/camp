# -*- coding: utf-8 -*-
from view_base import ViewBase, ViewBaseSet, NumberDelegate, DateDelegate, DateTimeDelegate
from PyQt4 import QtCore, QtGui, QtSql
import datetime
from trade import Trade
from guis.settings import ColorHighlightText, ColorBlueBar


class TradeDataModel(QtSql.QSqlQueryModel):
    def __init__(self, sysdate, parent=None):
        super(TradeDataModel, self).__init__(parent=parent)
        self.asOfDate = sysdate

    def data(self, index, int_role=None):
        if int_role == QtCore.Qt.TextAlignmentRole and index.column() in [7, 8, 9]:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        elif int_role == QtCore.Qt.BackgroundColorRole:
            if self.data(self.index(index.row(), 12), QtCore.Qt.DisplayRole).toString().isEmpty():  # if settle date is not confirmed
                return ColorHighlightText
            elif self.data(self.index(index.row(), 0), QtCore.Qt.DisplayRole).toDateTime().toPyDateTime().date() == self.asOfDate:
                return ColorBlueBar
        elif int_role == QtCore.Qt.DecorationRole and index.column() == 15:
            if not self.data(self.index(index.row(), 15), QtCore.Qt.DisplayRole).toString().isEmpty() or str(self.data(self.index(index.row(), 3), QtCore.Qt.DisplayRole).toString()) in ['CASH_IB', 'CASH_EX']:  # order file saved or unnecessary
                return QtGui.QIcon('guis/icons/greencheck.png')
            else:
                return QtGui.QIcon('guis/icons/redcross.png')
        else:
            return super(TradeDataModel, self).data(index, int_role)

    def setData(self, index, value, int_role=None):
        return super(TradeDataModel, self).setData(index, value, int_role)


class TradeView(ViewBase):
    def __init__(self, sysdate, user, oss, parent=None):
        super(TradeView, self).__init__(
                          header=[u'交易日', # 0
                                  u'账簿', # 1
                                  u'下单', # 2
                                  u'代码', # 3
                                  u'名称', u'类别', u'市场', # 4 5 6
                                  u'数量', # 7
                                  u'成交全价', # 8
                                  u'收益率', # 9
                                  u'到期日', # 10
                                  u'成交交割日', # 11
                                  u'成交确认',  # 12
                                  u'备注', # 13
                                  u'交易编码',  # 14
                                  u'指令上传'],  # 15
                          tablename=u'交易明细',
                          datatypes='tssssssfffddsss',
                          datamodel=TradeDataModel(sysdate),
                          asOfDate=sysdate,
                          menu=True,
                          parent=parent)
        self.user = user
        self.oss = oss
        self.sortByColumn(0, QtCore.Qt.DescendingOrder)
        #self.hideColumn(11)
        self.hideColumn(14)
        nfAmt = NumberDelegate(parent=self, withComma=True, numDigits=0)
        nfPct = NumberDelegate(parent=self, withComma=False, numDigits=2)
        df = DateDelegate(parent=self)
        dtf = DateTimeDelegate(parent=self)

        self.setItemDelegateForColumn(0, dtf)
        self.setItemDelegateForColumn(7, nfAmt)
        self.setItemDelegateForColumn(8, nfPct)
        self.setItemDelegateForColumn(9, nfPct)
        self.setItemDelegateForColumn(10, df)
        self.setItemDelegateForColumn(11, df)

    def build_query(self):
        self.query = ''.join([  'SELECT t.TRADE_DATETIME, ',
                                'b.NAME_CN, ',
                                'u.NAME, ',
                                't.INST_CODE, ',
                                's.SEC_NAME, s.SEC_TYPE, s.EXCHANGE, ',
                                't.AMOUNT, ',
                                't.PRICE, ',
                                't.REF_YIELD, ',
                                't.MATURITY_DATE, ',
                                't.SETTLE_DATE, ',
                                't.SETTLED_BY, ',
                                't.COMMENT, ',
                                't.TRADE_ID, ',
                                't.ORDER_SAVED ',
                                'FROM TRADES t ',
                                'LEFT OUTER JOIN BOOKS b on b.ID=t.BOOK ',
                                'LEFT OUTER JOIN USERS u on u.ID=t.TRADER ',
                                'LEFT OUTER JOIN SECINFO s on s.SEC_CODE=t.INST_CODE ',
                                """ WHERE t.TRADE_DATETIME<='%s'""" % datetime.datetime(self.asOfDate.year, self.asOfDate.month, self.asOfDate.day, 23, 59, 59) ])

    def buildMenu(self):
        self.menu = QtGui.QMenu()
        actConfirmSettle = QtGui.QAction(u'确认成交', self, triggered=self.confirmSettle)
        actDeleteTrade = QtGui.QAction(u'删除此条交易', self, triggered=self.deleteTrade)
        actConfirmExpSettle = QtGui.QAction(u'确认到期交割', self, triggered=self.confirmExpSettle)
        actDownloadOrder = QtGui.QAction(u'下载交易指令', self, triggered=self.downloadOrder)
        actUploadOrder = QtGui.QAction(u'上传交易指令', self, triggered=self.uploadOrder)
        actPrintOrder = QtGui.QAction(u'打印交易指令', self, triggered=self.printOrder)
        self.menu.addAction(actConfirmSettle)
        self.menu.addAction(actDeleteTrade)
        self.menu.addAction(actConfirmExpSettle)
        self.menu.addAction(actDownloadOrder)
        self.menu.addAction(actUploadOrder)
        self.menu.addAction(actPrintOrder)

    def date_update(self, newDate):
        self.asOfDate = newDate
        self.dataModel.asOfDate = newDate
        self.build_query()
        self.refresh()

    def downloadOrder(self):
        rowIndex = self.currentIndex().row()
        tradeID = self.model().index(rowIndex, 14).data().toString()
        localDir = QtGui.QFileDialog.getExistingDirectory(self, u'选择下载地址', 'C:/', QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks)
        if not localDir.isEmpty():
            book = self.model().index(rowIndex, 1).data().toString()
            trader = self.model().index(rowIndex, 2).data().toString()
            instname = self.model().index(rowIndex, 4).data().toString()
            td = self.model().index(rowIndex, 0).data().toDateTime().toString('yyyyMMdd')
            fname = '-'.join([unicode(s) for s in [book, trader, instname, td]])
            s = self.oss.download_trade_order(str(tradeID), unicode(localDir), fname=fname, withProgressBar=False)
            if s:
                QtGui.QMessageBox.about(self, u'交易指令下载', u'下载完毕')
            else:
                QtGui.QMessageBox.warning(self, u'交易指令下载', u'无法找到此笔交易的指令')

    def uploadOrder(self):
        fn = QtGui.QFileDialog.getOpenFileName(self, u'选取指令文件', '.')
        if not fn.isEmpty():
            rowIndex = self.currentIndex().row()
            tradeID = self.model().index(rowIndex, 14).data().toString()
            s = self.oss.upload_trade_order(str(tradeID), unicode(fn))
            if s:
                q = QtSql.QSqlQuery()
                query = """UPDATE TRADES SET ORDER_SAVED='%s' WHERE TRADE_ID='%s'""" % (datetime.datetime.now(), tradeID)
                q.exec_(query)
                #print query
                QtSql.QSqlDatabase().commit()
                QtGui.QMessageBox.about(self, u'交易指令上传', u'上传成功')
            else:
                QtGui.QMessageBox.warning(self, u'交易指令上传', u'上传失败，请联系开发人员解决问题')

    def printOrder(self):
        pass

    def confirmSettle(self):
        rowIndex = self.currentIndex().row()
        tradeID = self.model().index(rowIndex, 14).data().toString()
        trd = Trade.fromDB(tradeID)
        if trd:
            trd.settle(self.user.id)
        else:
            QtGui.QMessageBox.warning(self, u'错误', u'无法从数据库读取该笔交易')

    def confirmExpSettle(self):
        rowIndex = self.currentIndex().row()
        tradeID = self.model().index(rowIndex, 14).data().toString()
        trd = Trade.fromDB(tradeID)
        if trd:
            if self.asOfDate != trd.maturityDate:
                QtGui.QMessageBox.warning(self, u'注意', u'当前日期与预期到期交割日不同，将按预期到期日交割')
            trd.expsettle(self.user.id)
        else:
            QtGui.QMessageBox.warning(self, u'错误', u'无法从数据库读取该笔交易')

    def deleteTrade(self):
        rowIndex = self.currentIndex().row()
        tradeID = self.model().index(rowIndex, 14).data().toString()
        q = QtSql.QSqlQuery()
        try:
            query = """DELETE FROM TRADES WHERE TRADE_ID='%s'""" % tradeID
            q.exec_(query)
            #print query
            QtSql.QSqlDatabase().commit()
            self.refresh()
        except Exception, e:
            print e.message
            QtSql.QSqlDatabase().rollback()


class TradeViewSet(ViewBaseSet):
    def __init__(self, sysdate, user, oss, parent = None):
        super(TradeViewSet, self).__init__(TradeView(sysdate, user, oss), parent=parent)
        self.sortCol.setCurrentIndex(1)