# -*- coding: utf-8 -*-
import secs.bond
import datetime
from WindPy import w
if __name__=='__main__':
    b = secs.bond.BondBase('1080087.IB')
    b.initFromWind(w, datetime.date.today())
    pass