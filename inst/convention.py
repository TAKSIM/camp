# -*- coding: utf-8 -*-
import calendar
import datetime
from dateutil.relativedelta import *

oneday = datetime.timedelta(1)

class Holiday:
    def __init__(self, region=None, dbconn=None):
        if region is None:
            self.hols = []
        else:
            tableName = 'HOLIDAY_'+region
            self.hols = []

    def isHoliday(self, asOfDate):
        if self.hols:
            return asOfDate.date() in self.hols
        else:
            return asOfDate.isoweekday() in [6,7]

def nextBusDay(today, hol=Holiday()):
    nextDay = today + oneday
    while hol.isHoliday(nextDay):
        nextDay += oneday
    return nextDay

def lastBusDay(today, hol=Holiday()):
    lastDay = today - oneday
    while hol.isHoliday(lastDay):
        lastDay -= oneday
    return lastDay

def addWeeks(today, numWeeks, hol = Holiday(), busConv = None):
    d = today + datetime.timedelta(weeks=numWeeks)
    if busConv:
        return busConv.adj(d, hol)
    else:
        return d

class DateFreq:
    def __init__(self, name, hol=None, busConv=None):
        self.name = name
        self.hol = hol
        self.busConv = busConv

    def nextDay(self, today):
        d = self.nextDayNoAdj(today)
        if self.busConv:
            return self.busConv.adj(d, self.hol)
        else:
            return d

    def lastDay(self, today):
        d = self.lastDayNoAdj(today)
        if self.busConv:
            return self.busConv.adj(d, self.hol)
        else:
            return d

    def nextDayNoAdj(self, today):
        raise NotImplementedError()

    def lastDayNoAdj(self, today):
        raise NotImplementedError()

class Annual(DateFreq):
    def __init__(self, EOM=False, hol=None, busConv=None):
        DateFreq.__init__(self, u'每年'+(u'(月底)' if EOM else ''), hol, busConv)
        self.EOM = EOM

    def nextDayNoAdj(self, today):
        nextDay = today+relativedelta(years=+1)
        if self.EOM:
            _, numDays = calendar.monthrange(nextDay.year, nextDay.month)
            nextDay = datetime.date(nextDay.year, nextDay.month, numDays)
        return nextDay

    def lastDayNoAdj(self, today):
        lastDay = today+relativedelta(years=-1)
        if self.EOM:
            _, numDays = calendar.monthrange(lastDay.year, lastDay.month)
            lastDay = datetime.date(lastDay.year, lastDay.month, numDays)
        return lastDay

class BusinessConvention:
    def __init__(self, name):
        self.name = name

    def adj(self, d, hol=None):
        raise NotImplementedError('')

    def Get(self, name):
        if name == 'F':
            return Following()
        elif name == 'MF':
            return ModifiedFollowing()

class Following(BusinessConvention):
    def __init__(self):
        BusinessConvention.__init__(self, 'F')

    def adj(self, d, hol=None):
        useHol = hol or Holiday()
        if hol.isHoliday(d):
            return nextBusDay(d, useHol)
        else:
            return d

class ModifiedFollowing(BusinessConvention):
    def __init__(self):
        BusinessConvention.__init__(self, 'MF')

    def adj(self, d, hol=Holiday()):
        if hol.isHoliday(d):
            adjDate = nextBusDay(d, hol)
            if adjDate.month == d.month:
                return adjDate
            else:
                return lastBusDay(d, hol)
        else:
            return d

class NoAdjustment(BusinessConvention):
    def __init__(self):
        BusinessConvention.__init__(self, 'N')

    def adj(self, d, hol=None):
        return d

class DayCount:
    def __init__(self, dcname):
        self.name = dcname

    def YearFraction(self, startDate, endDate, inclStart=True, inclEnd=False):
        raise NotImplementedError('Day count method has not been implemented')

class Act365(DayCount):
    def __init__(self):
        DayCount.__init__(self,'Act/365')

    def YearFraction(self, startDate, endDate, inclStart=True, inclEnd=False):
        ds = (endDate-startDate).days
        if inclStart*inclEnd == 1:
            ds += 1
        elif inclStart + inclEnd == 0:
            ds -= 1
        return ds/365.0

class Act360(DayCount):
    def __init__(self):
        DayCount.__init__(self,'Act/360')

    def YearFraction(self, startDate, endDate, inclStart=True, inclEnd=False):
        ds = (endDate-startDate).days
        if inclStart*inclEnd == 1:
            ds += 1
        elif inclStart + inclEnd == 0:
            ds -= 1
        return ds/360.0