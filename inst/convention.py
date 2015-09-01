# -*- coding: utf-8 -*-

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