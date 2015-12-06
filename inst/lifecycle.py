# -*- coding: utf-8 -*-
import hashlib
from env import enum
from PyQt4 import QtSql
import datetime
# LOGIC:
# deal is a set of events, type of events include trade open/close, coupon, collateral etc
# event gives delta (i.e. change) of positions, including cash. event links to instrument and has timestamp.
# deal rolls by EOD, and call next event..
# (intra-day change) schedule has hash id, confirmed schedule is saved to db.
# event needs to be confirmed by trader
# event needs to be saved in db

# how to deal with T+N trade? cash vs usable cash
# how to deal with collateral?
# how to deal with schedules from close event?

# open event->settle or cancel event->close/maturity/default event->settle/recovery event => position change
# need the concept of "roll" deal in order to drive the life cycle
# need "trade blotter" to show live position, and allow user to close/collateral trades
# instrument generates schedule, position is a list of amount and instrument pairs
# events generate position
# identify schedule by (dealID, instID, scheduleDate, amount, reason)

EVENT_TYPE = enum(OPEN=0, OPEN_SETTLE=1, CLOSE=2, CLOSE_SETTLE=3, DEFAULT=4, CASH_FLOW=5, COUPON=6)

class Book:
    def __init__(self, id, name_en, name_cn_short, name_cn_full, startDate = None):
        self.id = id
        self.name_en = name_en
        self.name_cn_full = name_cn_full
        self.name_cn_short = name_cn_short
        self.startDate = startDate

    def LoadTrades(self, dbconn):
        c = dbconn.cursor()
        c.execute('SELECT * FROM TRADES WHERE BOOK={}'.format(self.name_en))
        c.close()

class Event:
    def __init__(self, dealID, instID, timestamp=None, signedBy=None, signedAt=None, cancel=False, comment='', refDate=None, refAmt=None, refPrice=None, refYield=None):
        self.dealID = dealID
        self.instID = instID
        self.timestamp = timestamp or datetime.datetime.now()
        self.by = signedBy
        self.at = signedAt
        self.cancelled = cancel
        self.comment = comment
        self.refDate = refDate
        self.refAmount = refAmt
        self.refPrice = refPrice
        self.refYield = refYield
        m = hashlib.sha1(self.__class__.__name__+dealID+instID+str(self.timestamp)+str(refAmt)+str(refDate)+str(refPrice)+str(refYield))
        self.eventID = m.hexdigest()

    def posChange(self, asOfDate):
        return None

    def eventName(self):
        raise NotImplementedError('Should not reach this level')

    def sign(self, user, comment='', dbconn=None):
        self.by = user.name
        self.at = datetime.datetime.now()
        if comment:
            self.comment = comment + ' | ' + self.comment
        if dbconn:
            c = dbconn.cursor()
            try:
                query = """UPDATE EVENTS SET SIGNER='%s', SIGNED_AT='%s', COMMENT='%s' WHERE ID='%s'""" % (user.name, datetime.datetime.now(), self.comment, self.eventID)
                print query
                c.execute(query)
                dbconn.commit()
            finally:
                c.close()

    def cancel(self, user, comment='', dbconn=None):
        self.by = user.name
        self.at = datetime.datetime.now()
        self.comment = comment
        self.cancelled = True
        if dbconn:
            c = dbconn.cursor()
            try:
                query = """UPDATE EVENTS SET CANCEL='%s' WHERE ID=%s""" % (1,self.eventID)
                c.execute(query)
                dbconn.commit()
            finally:
                c.close()

    def confirmed(self):
        return self.by is not None

    def bookToDB(self, dbconn):
        if dbconn:
            cursor = dbconn.cursor()
            try:
                cursor.execute("""INSERT INTO EVENTS VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                               (self.eventID, self.dealID, self.instID, self.timestamp, self.typeID(), self.by, self.at, self.cancelled, self.comment, self.refDate, self.refAmount, self.refPrice, self.refYield))
                dbconn.commit()
            except Exception, e:
                print e.message
                dbconn.rollback()
            cursor.close()

    @staticmethod
    def fromDB(eventID, dealID, instID, timestamp, eventType, signer, signedAt, cancelled, comment, refDate, refAmount, refPrice, refYield):
        if eventType == EVENT_TYPE.OPEN:
            e = OpenEvent(dealID, instID, timestamp, refAmount, refPrice, refYield)
        elif eventType == EVENT_TYPE.OPEN_SETTLE:
            e = OpenSettleEvent(dealID, instID, refDate, refAmount, refPrice, refYield)
        elif eventType == EVENT_TYPE.DEFAULT:
            e = DefaultEvent(dealID, instID, refDate, refAmount, refYield)
        elif eventType == EVENT_TYPE.CLOSE:
            e = CloseEvent(dealID, instID, timestamp, refAmount, refPrice, refYield)
        elif eventType == EVENT_TYPE.CLOSE_SETTLE:
            e = CloseSettleEvent(dealID, instID, refDate, refAmount, refPrice, refYield)
        elif eventType == EVENT_TYPE.CASH_FLOW:
            e = CashFlowEvent(dealID, instID, refDate, refAmount)
        elif eventType == EVENT_TYPE.COUPON:
            e = CouponEvent(dealID, instID, refDate, refAmount)
        e.at = signedAt
        e.by = signer
        e.comment = comment
        return e

    def typeID(self):
        raise NotImplementedError()

class OpenEvent(Event):
    def __init__(self, dealID, instID, bookDate, amount, tradePrice, tradeYield=0):
        Event.__init__(self, dealID, instID, refDate=bookDate, refAmt=amount, refPrice=tradePrice, refYield=tradeYield)
        self.comment = '{0} open: {1} units @ {2} as of {3}'.format(self.instID, self.refAmount, self.refYield or self.refPrice, self.refDate)

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'usablecash':-self.refAmount*self.refPrice}

    def typeID(self):
        return EVENT_TYPE.OPEN

class OpenSettleEvent(Event):
    def __init__(self, dealID, instID, settleDate, amount, settlePrice, settleYield=0):
        Event.__init__(self, dealID, instID, refDate=settleDate, refAmt=amount, refPrice=settlePrice, refYield=settleYield)
        self.comment = '{0} open settle: {1} units @ {2} as of {3}'.format(self.instID, self.refAmount, self.refYield or self.refPrice, self.refDate)

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'cash':-self.refPrice*self.refAmount,
                    self.instID : self.refAmount}

    def typeID(self):
        return EVENT_TYPE.OPEN_SETTLE

class DefaultEvent(Event):
    def __init__(self, dealID, instID, defaultDate, amount, recovery=0):
        Event.__init__(dealID, instID, refDate=defaultDate, refAmt=amount, refYield=recovery)
        self.comment = '{0} default confirmed with recovery rate of {1} as of {2}'.format(self.instID, self.refYield, self.refDate)

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'usablecash':self.refYield,
                    'cash':self.refYield,
                    self.instID:-self.refAmount}

    def typeID(self):
        return EVENT_TYPE.DEFAULT

class CloseEvent(Event):
    def __init__(self, dealID, instID, closeDate, amount, closePrice, closeYield=0):
        Event.__init__(self, dealID, instID, refDate=closeDate, refAmt=amount, refPrice=closePrice, refYield=closeYield)
        self.comment = '{0} close: {1} units @ {2}'.format(self.instID, self.refAmount, self.refYield or self.refPrice)

    def typeID(self):
        return EVENT_TYPE.CLOSE

class CloseSettleEvent(Event):
    def __init__(self, dealID, instID, settleDate, amount, settlePrice, settleYield=0):
        Event.__init__(self, dealID, instID, refDate=settleDate, refAmt=amount, refPrice=settlePrice, refYield=settleYield)
        self.comment = '{0} close settle: {1} units @ {2}'.format(self.instID, self.refAmount, self.refYield or self.refPrice)

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'usablecash':self.refAmount*self.refPrice,
                    'cash':self.refAmount*self.refPrice,
                    self.instID:-self.refAmount}

    def typeID(self):
        return EVENT_TYPE.CLOSE_SETTLE

class CashFlowEvent(Event):
    def __init__(self, dealID, instID, cfDate, amount):
        Event.__init__(self, dealID, instID, refDate=cfDate, refAmt=amount)
        self.comment = 'cash flow: {0} as of {1}'.format(self.refAmount, self.refAmount)

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'cash':self.refAmount,
                    'usablecash':self.refAmount}

    def typeID(self):
        return EVENT_TYPE.CASH_FLOW

class CouponEvent(CashFlowEvent):
    def __init__(self, dealID, instID, cfDate, amount):
        CashFlowEvent.__init__(self, dealID, instID, cfDate, amount)
        self.comment = '{0} coupon: {1}'.format(self.instID, self.refAmount)

    def typeID(self):
        return EVENT_TYPE.COUPON

class Sync:
    def __init__(self, timestamp, user, book, positions, syncType = 'EOD'):
        self.timestamp = timestamp
        self.book = book
        self.positions = positions
        self.syncType = syncType # EOD, SOD
        self.maker = user

    def bookToDB(self, dbconn):
        pass

class Deal:
    def __init__(self, *args, **kwargs):
        if len(args) > 3:
            user, bookID, instID, bookDate, settleDate, amount, tradePrice = args
            dealID = kwargs.get('dealID', None)
            shortable = kwargs.get('shortable', False)
            dbconn = kwargs.get('dbconn', None)
            self.bookID = bookID
            if dealID:
                self.dealID = dealID
            else:
                m = hashlib.sha1(instID)
                m.update(str(bookID))
                m.update(bookDate.isoformat())
                m.update(settleDate.isoformat())
                m.update(str(amount))
                m.update(str(tradePrice))
                self.dealID = m.hexdigest()
            self.shortable = shortable
            self.settleDate = settleDate
            oe = OpenEvent(self.dealID, instID, bookDate, amount, tradePrice)
            oe.sign(user,  '{0} open: {1}'.format(instID, str(amount)))
            oe.bookToDB(dbconn)
            self.events = [oe]

            se = OpenSettleEvent(self.dealID, instID, settleDate, amount, tradePrice)
            se.bookToDB(dbconn)
            self.events.append(se)

            self.bookToDB(dbconn)
        else:
            dealID, book = args
            self.events = []
            q = QtSql.QSqlQuery()
            q.exec_("""SELECT * FROM EVENTS WHERE DEAL_ID='%s' ORDER BY TIME_STAMP""" % (dealID,))
            while q.next():
                eventID = q.value(0).toString()
                dealID = q.value(1).toString()
                instID = q.value(2).toString()
                timestamp = q.value(3).toDateTime()
                eventType = q.value(4).toInt()[0]
                signer = q.value(5).toString()
                signedAt = q.value(6).toString()
                cancelled = q.value(7).toBool()
                comment = q.value(8).toString()
                refDate = q.value(9).toDate()
                refAmount = q.value(10).toDouble()[0]
                refPrice = q.value(11).toDouble()[0]
                refYield = q.value(12).toDouble()[0]

                self.events.append(Event.fromDB(eventID, dealID, instID, timestamp, eventType, signer,
                                                signedAt, cancelled, comment, refDate, refAmount, refPrice, refYield))

    def bookToDB(self, dbconn):
        if dbconn:
            cursor = dbconn.cursor()
            try:
                cursor.execute("""INSERT INTO DEALS VALUES (%s,%s,%s,%s)""",
                               (self.dealID, self.book.id, self.events[0].timestamp, None))
                dbconn.commit()
            except Exception, e:
                print e.message
                dbconn.rollback()
            cursor.close()

    def closeOnDB(self, dbconn):
        if dbconn:
            c = dbconn.cursor()
            try:
                query = """UPDATE DEALS SET CLOSE='%s' WHERE ID='%s'""" % (self.events[-1].timestamp)
                print query
                c.execute(query)
                dbconn.commit()
            finally:
                c.close()

    def positions(self, asOfDate, sync = None):
        if sync is None:
            acc = datetime.datetime(1900,1,1)
            pos = {'cash':0,'usablecash':0}
        else:
            acc = sync.timestamp
            pos = sync.positions
        for e in self.events:
            if e.timestamp>acc and not e.cancelled and e.confirmed():
                pd = e.posChange(asOfDate)
                if pd:
                    for k in pd:
                        if k in pos:
                            pos[k] += pd[k]
                        else:
                            pos[k] = pd[k]
        return pos

    def close(self, user, instID, closePrice, amount = None, settleDate = None, sync = None, dbconn=None):
        pos = self.positions(datetime.datetime.now(), sync)
        posAmount = pos.get(instID, 0)
        closeAmount = amount or posAmount
        if closeAmount > posAmount and not self.shortable:
            raise ValueError('Oversell: {0} hold {1} units, but try to sell {2} units'.format(instID, posAmount, closeAmount))
        ce = CloseEvent(self.dealID, instID, None, closeAmount, closePrice)
        ce.sign(user)
        ce.bookToDB(dbconn)
        self.events.append(ce)
        se = CloseSettleEvent(self.dealID, instID, settleDate or datetime.datetime.now(), closeAmount, closePrice)
        se.bookToDB(dbconn)
        self.events.append(se)
        if abs(closeAmount - posAmount) < 0.0001:
            self.closeOnDB(dbconn)

if __name__ == '__main__':
    import env
    import datetime
    import time
    dbc = env.Dbconfig('hewei','wehea1984')
    dbc.Connect()

    user = env.User('000705',dbc.conn)
    bs = env.LoadBooks(dbc.conn)
    book = bs[0]
    bookDate = datetime.datetime.now()
    d = Deal(user, book, '123456', bookDate, bookDate, 100, 98, dbconn=dbc.conn)
    time.sleep(1)
    print d.positions(datetime.datetime.now())

    d.events[1].sign(user,'test',dbc.conn)
    print d.positions(datetime.datetime.now())

    d.close(user,'123456',99,50, dbconn=dbc.conn)
    d.events[-1].sign(user,'close half',dbconn=dbc.conn)

    print d.positions(datetime.datetime.now())

    d.close(user, '123456', 99, 25, dbconn=dbc.conn)
    d.events[-1].sign(user, 'close another quarter', dbconn=dbc.conn)
    time.sleep(1)
    print d.positions(datetime.datetime.now())
    for e in d.events:
        print e.eventID

    dbc.Close()





