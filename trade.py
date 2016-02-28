# -*- coding: utf-8 -*-
import hashlib
from PyQt4 import QtSql


class Trade:
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            book, trader, tradeDateTime, settleDate, instCode, amount, price = args
            self.book = book
            self.trader = trader
            self.tradeDateTime = tradeDateTime
            self.settleDate = settleDate
            self.instCode = instCode
            self.amount = amount
            self.price = price
            self.collateralized = kwargs.get('collateralized', False)
            self.refTrade = kwargs.get('refTrade', '')
            self.refYield = kwargs.get('refYield', 0.)
            self.settledBy = kwargs.get('settledBy', '')
            self.comment = kwargs.get('comment', '')
            self.maturityDate = kwargs.get('maturityDate', None)
            self.tradeID = kwargs.get('tradeID', None)
            if not self.tradeID:
                m = hashlib.sha1()
                m.update(str(self.trader) + str(self.tradeDateTime) + unicode(self.comment).encode('GB2312') + str(self.amount) + str(self.refTrade) + str(self.price) + str(self.refYield) + str(self.maturityDate))
                self.tradeID = m.hexdigest()
        elif len(args) == 1:
            self.tradeID = args[0]

    def toDB(self):
        q = QtSql.QSqlQuery()
        try:
            query = """INSERT INTO TRADES VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (self.tradeID, self.book, self.trader, self.tradeDateTime, self.settleDate, self.instCode, self.amount, self.price, int(self.collateralized), self.refTrade, self.refYield, self.settledBy, self.comment, self.maturityDate)
            q.exec_(query)
            #print query
            QtSql.QSqlDatabase().commit()
        except Exception, e:
            print e.message
            QtSql.QSqlDatabase().rollback()

    def fromDB(self):
        if self.tradeID:
            q = QtSql.QSqlQuery("""SELECT * FROM TRADES WHERE TRADE_ID='%s'""" % self.tradeID)
            while q.next():
                self.book = q.value(1).toInt()[0]
                self.trader = str(q.value(2).toString())
                self.tradeDateTime = q.value(3).toDateTime().toPyDateTime()
                self.settleDate = q.value(4).toDate().toPyDate()
                self.instCode = str(q.value(5).toString())
                self.amount = q.value(6).toDouble()[0]
                self.price = q.value(7).toDouble()[0]
                self.collateralized = bool(q.value(8).toInt()[0])
                self.refTrade = str(q.value(9).toString())
                self.refYield = q.value(10).toDouble()[0]
                self.settledBy = str(q.value(11).toString())
                self.comment = str(q.value(12).toString())
                md = q.value(13).toDate()
                self.maturityDate = md and md.toPyDate() or ''
                return True
        return False

    def settle(self, trader):
        q = QtSql.QSqlQuery()
        try:
            query = """UPDATE TRADES SET SETTLED_BY='%s' WHERE TRADE_ID='%s'""" % (self.settledBy, self.tradeID)
            q.exec_(query)
            #print query
            QtSql.QSqlDatabase().commit()
            self.settledBy = trader
        except Exception, e:
            print e.message
            QtSql.QSqlDatabase().rollback()

    def value(self, asOfDate):
        raise NotImplemented()

    def isSettled(self):
        return len(self.settledBy) > 0


class CashTrade(Trade):
    def __init__(self, book, trader, tradeDateTime, amount, instCode='CASH_IB', refTrade='', comment='', tradeID=None):
        Trade.__init__(self, book, trader, tradeDateTime, tradeDateTime.date(), instCode, amount, 1.0,
                       collateralized=False, refTrade=refTrade, refYield=0, settledBy=trader, comment=comment, tradeID=tradeID)

    def value(self, asOfDate):
        return asOfDate < self.settleDate and self.amount or 0.


class DepoTrade(Trade):
    def __init__(self, book, trader, tradeDateTime, amount, rtn, maturityDate, dcc='Act/360', settledBy='', comment='', tradeID=None):
        Trade.__init__(self, book, trader, tradeDateTime, tradeDateTime.date(), 'IBDP', amount, 1.0,
                       collateralized=False, refTrade='', refYield=rtn, settledBy=settledBy, comment=comment, maturityDate=maturityDate, tradeID=tradeID)

    def totalReturn(self):
        return (self.maturityDate - self.settleDate).days / 360.0 * self.refYield / 100.0 * self.amount

    def value(self, asOfDate):
        if self.isSettled():
            if asOfDate > self.settleDate:
                expdate = asOfDate > self.maturityDate and self.maturityDate or asOfDate
                return (expdate-self.settleDate).days/360.*self.refYield/100.*self.amount
        return 0.

    def settle(self, trader):
        Trade.settle(self, trader=trader)
        ct = CashTrade(self.book, trader, self.tradeDateTime, -self.amount, instCode='CASH_IB', refTrade=self.tradeID, comment=u'同存存出')
        ct.toDB()







