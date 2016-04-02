# -*- coding: utf-8 -*-
from PyQt4 import QtSql
import datetime
from WindPy import w


class InstrumentBase(object):
    def __init__(self, code):
        self.code = code
        self.initOK = False
        typedata = InstrumentBase.getTypeData(self.code)
        if typedata:
            self.name, self.insttype, self.exchange = typedata
            self.getInstData()

    def windFieldRequests(self):
        return []

    def cashflows(self):
        return {}

    @staticmethod
    def getTypeData(code):
        q = QtSql.QSqlQuery("""SELECT SEC_NAME, SEC_TYPE, EXCHANGE FROM SECINFO WHERE SEC_CODE='%s'""" % code)
        while q.next():
            name = q.value(0).toString()
            insttype = q.value(1).toString()
            exchange = q.value(2).toString()
            return name, insttype, exchange
        infolist = ['sec_name', 'sec_type', 'exch_city']
        result = w.wss(unicode(code), infolist, 'tradeDate={0}'.format(format(datetime.datetime.today(), '%Y%m%d')))
        if result:
            if result.ErrorCode == 0:
                name = result.Data[0][0]
                insttype = result.Data[1][0]
                exchange = result.Data[2][0]
                q = QtSql.QSqlQuery()
                try:
                    q.exec_("""INSERT INTO SECINFO VALUES ('%s','%s','%s','%s')""" % (code, name, insttype, exchange))
                    QtSql.QSqlDatabase().commit()
                    return name, insttype, exchange
                except Exception, e:
                    print e.message
                    QtSql.QSqlDatabase().rollback()

    def getInstData(self):
        fields = self.windFieldRequests()
        if fields:
            windFields = [f[0] for f in fields]
            result = w.wss(unicode(self.code), windFields, 'tradeDate={0}'.format(format(datetime.datetime.today(), '%Y%m%d')))
            if result:
                if result.ErrorCode == 0:
                    for i in range(len(fields)):
                        self.__setattr__(fields[i][1], result.Data[i][0])
                    self.initOK = True
        else:
            self.initOK = True


class CashBond(InstrumentBase):
    def __init__(self, code):
        super(CashBond, self).__init__(code)

    def windFieldRequests(self):
        return [('issuerupdated', 'issuer'),            # 发行人
                 ('issueamount', 'issueAmount'),         # 发行规模
                 ('windl1type', 'bondType'),             # 债券类别
                 ('maturitydate', 'maturityDate'),       # 到期日
                 ('actualbenchmark', 'dcc'),             # day count convention
                 ('term', 'issueTerm'),                  # 发行期限
                 ('couponrate', 'coupon'),               # 票息
                 ('interesttype', 'couponType'),         # 利率类型 '固定利率' or '浮动利率'
                 ('interestfrequency', 'numCpnPerYear'), # 每年付息次数
                 ('latestissurercreditrating', 'issuerRating'),  # 主体评级
                 ('amount', 'bondRating'),               # 债项评级
                 ('agency_guarantor', 'guarantor'),      # 担保人
                 ('agency_grnttype', 'guarantType'),     # 担保方式
                 ('lastdate_cnbd', 'lastVDate'),         # 最新估值日'
                 ('subordinateornot', 'isSub'),          # 次级债？
                 ('municipalbond', 'isMuni'),            # 城投债？
                 ('embeddedopt', 'hasOpt'),              # 含权？
                ]

    def cashflows(self):
        pass