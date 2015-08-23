# -*- coding: utf-8 -*-
from env import enum
import hashlib

InstType = enum(BOND=1, MMF=2, REPO=3, DEPOSITE=4, CASH=5)
Market = enum(IB=1, SH=2, SZ=3, OTHER=4)
Ccy = enum(CNY=1, CNH=2, USD=3)
Trader = enum(GaoGu=1,HuBeishi=2,QiangYuting=3,HeWwei=4)

class Instrument:
    def __init__(self, id, insttype, ccy = Ccy.CNY, isOTC=True, maturityDate=None):
        self.id = id
        self.insttype = insttype
        self.ccy = ccy
        self.isOTC = isOTC
        self.maturityDate = maturityDate

    def Price(self, asOfDate):
        raise NotImplementedError('Pricing method has not been implemented')

class Deal:
    def __init__(self, inst, tradeDate, amount, tradePrice, book, trader, settleDate=None, maturityDate=None):
        self.inst = inst
        self.tradeDate = tradeDate
        self.amount = amount
        self.tradePrice = tradePrice
        self.book = book
        self.trader = trader
        self.settleDate = settleDate or tradeDate
        self.maturityDate = maturityDate or self.inst.maturityDate
        m = hashlib.sha1()
        m.update(self.inst.id)
        m.update(self.tradeDate.isoformat())
        m.update(str(self.amount))
        m.update(str(self.tradePrice))
        self.id = m.hexdigest()

    def Price(self, asOfDate):
        return self.inst.Price(asOfDate) * self.amount

    def IsLive(self, asOfDate):
        if asOfDate<=self.tradeDate:
            return False
        else:
            return self.maturityDate is None or self.maturityDate <= asOfDate

    def Book(self, dbconn):
        cursor = dbconn.cursor()
        try:
            cursor.execute("""INSERT INTO TRADES VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(self.id,self.book.id,self.tradeDate.isoformat(),self.settleDate.isoformat(),self.inst.id,self.amount,self.tradePrice,self.trader))
            dbconn.commit()
        except Exception,e:
            print e.message
            dbconn.rollback()
        cursor.close()
