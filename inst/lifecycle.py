# -*- coding: utf-8 -*-
import datetime
import hashlib

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

class Event:
    def __init__(self, dealID, instID, timestamp, signedBy=None, signedAt=None, cancel=False):
        self.dealID = dealID
        self.instID = instID
        self.timestamp = timestamp
        self.by = signedBy
        self.at = signedAt
        self.cancelled = cancel
        self.comment = ''

    def posChange(self, asOfDate):
        return None

    def eventName(self):
        raise NotImplementedError('Should not reach this level')

    def sign(self, user, comment=''):
        self.by = user.name
        self.at = datetime.datetime.now()
        self.comment = comment

    def cancel(self, user, comment=''):
        self.by = user.name
        self.at = datetime.datetime.now()
        self.comment = comment
        self.cancelled = True

    def confirmed(self):
        return self.by is not None

    def bookToDB(self, dbconn):
        raise NotImplementedError('Should not reach this level')

class OpenEvent(Event):
    def __init__(self, dealID, instID, bookDate, amount, tradePrice):
        Event.__init__(self, dealID, instID, bookDate)
        self.amount = amount
        self.tradePrice = tradePrice

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'usablecash':-self.amount*self.tradePrice}

class OpenSettleEvent(Event):
    def __init__(self, dealID, instID, settleDate, amount, settlePrice):
        Event.__init__(self, dealID, instID, settleDate)
        self.amount = amount
        self.settlePrice = settlePrice

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'cash':-self.settlePrice*self.amount,
                    self.instID : self.amount}

class DefaultEvent(Event):
    def __init__(self, dealID, instID, defaultDate, amount, recovery=0):
        Event.__init__(dealID, instID, defaultDate)
        self.amount = amount
        self.recovery = recovery

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'usablecash':self.recovery,
                    'cash':self.recovery,
                    self.instID:-self.amount}

class CloseEvent(Event):
    def __init__(self, dealID, instID, closeDate, amount, closePrice):
        Event.__init__(self, dealID, instID, closeDate)
        self.amount = amount
        self.closePrice = closePrice

class CloseSettleEvent(Event):
    def __init__(self, dealID, instID, settleDate, amount, settlePrice):
        Event.__init__(self, dealID, instID, settleDate)
        self.amount = amount
        self.settlePrice = settlePrice

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'usablecash':self.amount*self.settlePrice,
                    'cash':self.amount*self.settlePrice,
                    self.instID:-self.amount}

class CashFlowEvent(Event):
    def __init__(self, dealID, instID, cfDate, amount):
        Event.__init__(self, dealID, instID, cfDate)
        self.amount = amount

    def posChange(self, asOfDate):
        if asOfDate > self.timestamp:
            return {'cash':self.amount,
                    'usablecash':self.amount}

class CouponEvent(CashFlowEvent):
    def __init__(self, dealID, instID, cfDate, amount):
        CashFlowEvent.__init__(self, dealID, instID, cfDate, amount)
        self.comment = self.instID + u' 付息：'+str(self.amount)

class Sync:
    def __init__(self, timestamp, positions, syncType = 'EOD'):
        self.timestamp = timestamp
        self.positions = positions
        self.syncType = syncType # EOD, SOD, Intraday

    def bookToDB(self, dbconn):
        raise NotImplementedError()

class Deal:
    def __init__(self, user, instID, bookDate, settleDate, amount, tradePrice, shortable=False):
        m = hashlib.sha1(instID)
        m.update(bookDate.isoformat())
        m.update(settleDate.isoformat())
        m.update(str(amount))
        m.update(str(tradePrice))
        self.dealID = m.hexdigest()
        self.shortable = shortable
        self.settleDate = settleDate
        oe = OpenEvent(self.dealID, instID, bookDate, amount, tradePrice)
        oe.sign(user, instID + u'开仓：' + amount)
        self.events = [oe]

        se = OpenSettleEvent(self.dealID, instID, settleDate, amount, tradePrice)
        self.events.append(se)

    def nextEvent(self, asOfDate):
        return None

    def positions(self, asOfDate, sync = None):
        if sync is None:
            acc = datetime.date(1900,1,1)
            pos = {}
        else:
            acc = sync.timestamp
            pos = sync.positions
        for e in self.events:
            if e.timestamp>acc and not e.cancelled and e.confirmed():
                pd = e.posChange(asOfDate)
                for k, v in pd:
                    if k in pos:
                        pos[k] += v
                    else:
                        pos[k] = v
        return pos

    def close(self, user, instID, closePrice, amount = None, settleDate = None, sync = None):
        pos = self.positions(datetime.datetime.now(), sync)
        posAmount = pos.get(instID, 0)
        closeAmount = amount or posAmount
        if closeAmount > posAmount and not self.shortable:
            raise ValueError(u'超卖：{0}持仓{1}，计划卖出{2}'.format(instID, posAmount, closeAmount))
        ce = CloseEvent(self.dealID, instID, datetime.datetime.now(), amount, closePrice)
        ce.sign(user, instID+u' 平仓：'+str(closeAmount))
        self.events.append(ce)
        se = CloseSettleEvent(self.dealID, instID, settleDate or datetime.datetime.now(), closeAmount, closePrice)
        self.events.append(se)








