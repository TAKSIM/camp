# -*- coding: utf-8 -*-
import env
from inst import base
import datetime
from WindPy import w
if __name__=='__main__':
    #b = inst.bond.BondBase('1080087.IB')
    #b.initFromWind(w, datetime.date.today())
    dbconf = env.Dbconfig('hewei','wehea1984')
    dbconf.Connect()
    bs = env.LoadBooks(dbconf.conn)
    i = base.Instrument('ibdepo',base.InstType.DEPOSITE)
    d = base.Deal(i,datetime.datetime.now(),10,102.5,bs[0],base.Trader.GaoGu)

    d.Book(dbconf.conn)
    dbconf.Close()
    pass