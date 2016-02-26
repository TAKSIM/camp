# -*- coding: utf-8 -*-
import hashlib
from PyQt4 import QtSql


class Trade:
    def __init__(self, book, trader, tradeDateTime, settleDate, instCode, amount, price, collateralized=False, refTrade='', refYield=0, settledBy='', comment='', tradeID=None):
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
        if tradeID:
            self.tradeID = tradeID
        else:
            m = hashlib.sha1()
            m.update(self.trader + str(self.tradeDateTime))
            self.tradeID = m.hexdigest()

    def toDB(self):
        q = QtSql.QSqlQuery()
        try:
            query = """INSERT INTO TRADES VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (self.tradeID, self.book, self.trader, self.tradeDateTime, self.settleDate, self.instCode, self.amount, self.price, int(self.collateralized), self.refTrade, self.refYield, self.settledBy, self.comment)
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


class CashTrade(Trade):
    def __init__(self, book, trader, tradeDateTime, amount, instCode='CASH_IB', settledBy='', comment='', tradeID=None):
        Trade.__init__(self,
                       book=book, trader=trader, tradeDateTime=tradeDateTime, settleDate=tradeDateTime.date(),
                       instCode=instCode, amount=amount, price=1.0, collateralized=False, refTrade='', refYield=0,
                       settledBy=settledBy, comment=comment, tradeID=tradeID)



