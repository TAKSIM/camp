# -*- coding: utf-8 -*-
import hashlib
from PyQt4 import QtSql, QtCore
from WindPy import w
import datetime

class Trade(object):
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
                m.update(str(self.trader) + str(self.tradeDateTime) + unicode(self.comment).encode('GBK') + str(self.amount) + str(self.refTrade) + str(self.price) + str(self.refYield) + str(self.maturityDate))
                self.tradeID = m.hexdigest()
        elif len(args) == 1:
            self.tradeID = args[0]

    def toDB(self):
        q = QtSql.QSqlQuery()
        try:
            query = """INSERT INTO TRADES VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (self.tradeID, self.book, self.trader, self.tradeDateTime, self.settleDate, self.instCode, self.amount, self.price, int(self.collateralized), self.refTrade, self.refYield, self.settledBy, self.comment, self.maturityDate, 'NULL', 'NULL')
            q.exec_(query)
            #print query
            QtSql.QSqlDatabase().commit()
        except Exception, e:
            print e.message
            QtSql.QSqlDatabase().rollback()

    @staticmethod
    def fromDB(tradeID):
        q = QtSql.QSqlQuery("""SELECT * FROM TRADES WHERE TRADE_ID='%s'""" % tradeID)
        while q.next():
            book = q.value(1).toInt()[0]
            trader = str(q.value(2).toString())
            tradeDateTime = q.value(3).toDateTime().toPyDateTime()
            settleDate = q.value(4).toDate().toPyDate()
            instCode = str(q.value(5).toString())
            amount = q.value(6).toDouble()[0]
            price = q.value(7).toDouble()[0]
            collateralized = bool(q.value(8).toInt()[0])
            refTrade = str(q.value(9).toString())
            refYield = q.value(10).toDouble()[0]
            settledBy = str(q.value(11).toString())
            comment = unicode(q.value(12).toPyObject())
            md = q.value(13).toDate()
            maturityDate = md and md.toPyDate() or None
            q = QtSql.QSqlQuery("""SELECT SEC_TYPE FROM SECINFO WHERE SEC_CODE='%s'""" % instCode)
            while q.next():
                secname = q.value(0).toString()
                if secname == QtCore.QString(u'现金'):
                    obj = CashTrade(book, trader, tradeDateTime, amount, instCode=instCode, refTrade=refTrade, comment=comment,tradeID=tradeID)
                    return obj
                elif secname == QtCore.QString(u'存款'):
                    obj = DepoTrade(book, trader, tradeDateTime, amount, refYield, maturityDate, dcc='Act/360', settledBy=settledBy, comment=comment, tradeID=tradeID)
                    return obj
                elif secname in [QtCore.QString(u'短期融资券'), QtCore.QString(u'企债')]:
                    obj = BondTrade(book, trader, tradeDateTime, settleDate, instCode, amount, price, refYield, collateralized=collateralized, refTrade=refTrade, settledBy=settledBy, comment=comment, tradeID=tradeID)
                    return obj
                else:
                    raise NotImplementedError('Unknown trade type')

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

    def cashflows(self, asOfDate):
        return {}


class CashTrade(Trade):
    def __init__(self, book, trader, tradeDateTime, amount, instCode='CASH_IB', refTrade='', comment='', tradeID=None):
        super(CashTrade, self).__init__(book, trader, tradeDateTime, tradeDateTime.date(), instCode, amount, 1.0,
                       collateralized=False, refTrade=refTrade, refYield=0, settledBy=trader, comment=comment, tradeID=tradeID)

    def value(self, asOfDate):
        return asOfDate < self.settleDate and self.amount or 0.

    def cashflows(self, asOfDate):
        if asOfDate < self.settleDate:
            return {self.settleDate : self.amount}


class DepoTrade(Trade):
    def __init__(self, book, trader, tradeDateTime, amount, rtn, maturityDate, dcc='Act/360', settledBy='', comment='', tradeID=None):
        super(DepoTrade, self).__init__(book, trader, tradeDateTime, tradeDateTime.date(), 'IBDP', amount, 1.0,
                       collateralized=False, refTrade='', refYield=rtn, settledBy=settledBy, comment=comment, maturityDate=maturityDate, tradeID=tradeID)

    def totalReturn(self):
        return -(self.maturityDate - self.settleDate).days / 360.0 * self.refYield / 100.0 * self.amount

    def cashflows(self, asOfDate):
        if asOfDate < self.settleDate or asOfDate > self.maturityDate:
            return None
        else:
            return {self.maturityDate : self.totalReturn()}

    def value(self, asOfDate):
        if self.isSettled():
            if asOfDate > self.settleDate:
                expdate = asOfDate > self.maturityDate and self.maturityDate or asOfDate
                return (expdate-self.settleDate).days/360.*self.refYield/100.*self.amount
        return 0.

    def settle(self, trader):
        super(DepoTrade, self).settle(trader=trader)
        ct = CashTrade(self.book, trader, self.tradeDateTime, -self.amount, instCode='CASH_IB', refTrade=self.tradeID, comment=u'同存存出')
        ct.toDB()


class BondTrade(Trade):
    def __init__(self, book, trader, tradeDateTime, settleDate, instCode, amount, price, refYield, collateralized = False, refTrade = '', settledBy = '', comment = '', tradeID=None):
        super(BondTrade, self).__init__(book, trader, tradeDateTime, settleDate, instCode, amount, price, refYield=refYield, collateralized=collateralized, refTrade=refTrade, settledBy=settledBy, comment=comment, tradeID=tradeID)
        self.face = 100.

    def value(self, asOfDate):
        result = w.wss(self.instCode, ['dirty_cnbd'], 'tradeDate={0}'.format(format(asOfDate,'%Y%m%d')), 'credibility=1')
        if result.ErrorCode == 0:
            v = result.Data[0][0]
            return v
        else:
            return None

    def cashflows(self):
        cfs = {self.settleDate: -self.price*self.amount}
        # coupons
        return cfs

    def settle(self, trader):
        q = QtSql.QSqlQuery()
        try:
            query = """UPDATE TRADES SET SETTLED_BY='%s' WHERE TRADE_ID='%s'""" % (trader, self.tradeID)
            q.exec_(query)
            #print query
            QtSql.QSqlDatabase().commit()
            self.settledBy = trader

            ct = CashTrade(self.book, self.trader, datetime.datetime.fromordinal(self.settleDate.toordinal()), -self.amount*self.price, self.instCode[-2:]=='IB' and 'CASH_IB' or 'CASH_EX', refTrade=self.tradeID, comment=u'交割现金流')
            ct.toDB()
        except Exception, e:
            print e.message
            QtSql.QSqlDatabase().rollback()





