# -*- coding: utf-8 -*-
from env import enum
import hashlib

InstType = enum(BOND=1, MMF=2, REPO=3, DEPOSITE=4, CASH=5)
Market = enum(IB=1, SH=2, SZ=3, OTHER=4)
Ccy = enum(CNY=1, CNH=2, USD=3)
Role = enum(Trader=1,Sales=2,Risk=3,Research=4)
Auth = enum(READ_ONLY=1, READ_WRITE=2, NO_VIEW=3)

class User:
    def __init__(self, id, dbconn):
        c = dbconn.cursor()
        try:
            c.execute('SELECT * FROM USERS WHERE ID={}'.format(id))
            u = c.fetchall()
            if u:
                self.id = id
                self.name = u[0][1]
                self.email = u[0][2]
                self.role = u[0][3]
                self.pwd = u[0][4]
                self.pwdtmp = u[0][5]
            else:
                self.id = None
        finally:
            c.close()

    def needPwdReset(self):
        return self.pwdtmp != 0

    def checkPwd(self, pwd):
        m = hashlib.sha1()
        m.update(pwd)
        return m.hexdigest() == self.pwd

    def resetPwd(self, newpwd, dbconn):
        m = hashlib.sha1()
        m.update(newpwd)
        c = dbconn.cursor()
        try:
            query = """UPDATE USERS SET PWD='%s', PWD_TEMP=0 WHERE ID=%s""" % (m.hexdigest(),self.id)
            print query
            c.execute(query)
            dbconn.commit()
            self.pwd = newpwd
        finally:
            c.close()

    def initPwd(self, dbconn):
        import random
        import string
        import utils
        initpwd = ''.join(random.choice(string.ascii_letters) for i in range(6))
        m = hashlib.sha1()
        m.update(initpwd)
        utils.sendmail('CAITC-FID@caitc.cn',[self.email], u'重设CAMP密码', initpwd)
        c = dbconn.cursor()
        try:
            query = """UPDATE USERS SET PWD='%s', PWD_TEMP=1 WHERE ID=%s""" % (m.hexdigest(), self.id)
            print query
            c.execute(query)
            dbconn.commit()
        finally:
            c.close()

class Instrument:
    def __init__(self, id, insttype, ccy = Ccy.CNY, isOTC=True, maturityDate=None):
        self.id = id
        self.insttype = insttype
        self.ccy = ccy
        self.isOTC = isOTC
        self.maturityDate = maturityDate

    def Price(self, asOfDate):
        raise NotImplementedError('Pricing method has not been implemented')

class Deposite(Instrument):
    def __init__(self, counterparty, maturityDate, ccy = Ccy.CNY):
        Instrument.__init__(self, counterparty.id, InstType.DEPOSITE, ccy, True, maturityDate)

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

    def Cost(self):
        return self.amount * self.tradePrice

    def IsLive(self, asOfDate):
        if asOfDate<=self.tradeDate:
            return False
        else:
            return self.maturityDate is None or self.maturityDate <= asOfDate

    def OpenTrade(self, dbconn):
        cursor = dbconn.cursor()
        try:
            cursor.execute("""INSERT INTO TRADES VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(self.id,self.book.id,self.tradeDate.isoformat(),self.settleDate.isoformat(),self.inst.id,self.amount,self.tradePrice,self.trader))
            dbconn.commit()
        except Exception,e:
            print e.message
            dbconn.rollback()
        cursor.close()

class Position:
    def __init__(self, lastUpdate, pos):
        self.lastUpdate = lastUpdate
        self.pos = pos # inst id : amount
        if 'cash' not in self.pos:
            pos['cash'] = 0.0

    def loadDeals(self, ds):
        for d in ds:
            if d.inst.id in self.pos:
                self.pos[d.inst.id] += d.amount
            else:
                self.pos[d.inst.id] = d.amount
            self.pos['cash'] += d.Cost()
            if d.tradeDate > self.lastUpdate:
                self.lastUpdate = d.tradeDate