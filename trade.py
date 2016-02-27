# -*- coding: utf-8 -*-
import hashlib
from PyQt4 import QtSql


class Trade:
    def __init__(self, book, trader, tradeDateTime, settleDate, instCode, amount, price, collateralized=False, refTrade='', refYield=0, settledBy='', comment='', maturityDate = '', tradeID=None):
        self.book = book
        self.trader = trader
        self.tradeDateTime = tradeDateTime
        self.settleDate = settleDate
        self.instCode = instCode
        self.amount = amount
        self.price = price
        self.collateralized = collateralized
        self.refTrade = refTrade
        self.refYield = refYield
        self.settledBy = settledBy
        self.comment = comment
        self.maturityDate = maturityDate
        if tradeID:
            self.tradeID = tradeID
        else:
            m = hashlib.sha1()
            m.update(self.trader + str(self.tradeDateTime) + self.comment.encode('GB2312') + str(self.amount) + refTrade + str(self.price) + str(self.refYield) + str(self.maturityDate))
            self.tradeID = m.hexdigest()

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
        Trade.__init__(self,
                       book=book, trader=trader, tradeDateTime=tradeDateTime, settleDate=tradeDateTime.date(),
                       instCode=instCode, amount=amount, price=1.0, collateralized=False, refTrade=refTrade, refYield=0,
                       settledBy=trader, comment=comment, tradeID=tradeID)

    def value(self, asOfDate):
        return asOfDate < self.settleDate and self.amount or 0.


class DepoTrade(Trade):
    def __init__(self, book, trader, tradeDateTime, amount, rtn, maturityDate, dcc='Act/360', settledBy='', comment='', tradeID=None):
        Trade.__init__(self, book=book, trader=trader, tradeDateTime=tradeDateTime, settleDate=tradeDateTime.date(),
                       instCode='IBDP', amount=amount, price=1.0, collateralized=False, refTrade='', refYield=rtn,
                       settledBy=settledBy, comment=comment, maturityDate=maturityDate, tradeID=tradeID)

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







