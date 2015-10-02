# -*- coding: utf-8 -*-
import datetime
from lifecycle import Deal
import WindPy
import MySQLdb

class BondDeal(Deal):
    def __init__(self, user, instID, amount, openPrice, bookDate=None, settleDate=None):
        Deal.__init__(self, user, instID, bookDate or datetime.datetime.now(), settleDate, amount, openPrice, shortable=False)

    def nextEvent(self, asOfDate):
        pass


class BondInstrument:
    _windFields=['sec_name',
                 'maturitydate',
                 'couponrate',
                 'interestfrequency',
                 'carrydate',
                 'amount',
                 'latestissurercreditrating']
    def __init__(self, instID):
        self.instID = instID
        self.maturity = None
        self.coupon = None
        self.freq = None
        self.accrualDate = None
        self.bondRating = None
        self.issuerRating = None

    def initFromWind(self, wp, asOfDate = None):
        try:
            wp.start()
            data = wp.wss([self.id], self._windFields, 'rptDate='+datetime.date.strftime(asOfDate or datetime.date.today()-1, '%Y%m%d'))
            self.name = data.Data[0][0]
            self.maturity = data.Data[1][0]
            self.coupon = data.Data[2][0]
            self.freq = data.Data[3][0]
            self.accrualDate = data.Data[4][0]
            self.bondRating = data.Data[5][0]
            self.issuerRating = data.Data[6][0]
            wp.close()
        except Exception, e:
            print 'Failed to retrieve data from wind for ' + self.id