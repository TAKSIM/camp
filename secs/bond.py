# -*- coding: utf-8 -*-
import datetime
import WindPy
import MySQLdb

class BondBase:
    _windFields=['sec_name',
                 'maturitydate',
                 'couponrate',
                 'interestfrequency',
                 'carrydate',
                 'amount',
                 'latestissurercreditrating']
    def __init__(self, id, name=None):
        self.id = id
        self.name = name
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


    def initFromDB(self, conn, asOfDate = None):
        if type(conn) is not MySQLdb.connection:
            raise TypeError('Unknown type. Supposed to be initialized from MySQL DB')
        pass