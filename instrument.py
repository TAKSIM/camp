# -*- coding: utf-8 -*-
from PyQt4 import QtSql
import datetime
from WindPy import w
from utils import YearFrraction


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
        # q = QtSql.QSqlQuery("""SELECT SEC_NAME, SEC_TYPE, EXCHANGE FROM SECINFO WHERE SEC_CODE='%s'""" % code)
        # while q.next():
        #     name = q.value(0).toString()
        #     insttype = q.value(1).toString()
        #     exchange = q.value(2).toString()
        #     return name, insttype, exchange
        infolist = ['sec_name', 'sec_type', 'exch_city']
        result = w.wss(unicode(code), infolist, 'tradeDate={0}'.format(format(datetime.datetime.today(), '%Y%m%d')))
        if result:
            if result.ErrorCode == 0:
                name = result.Data[0][0]
                insttype = result.Data[1][0]
                exchange = result.Data[2][0]
                # q = QtSql.QSqlQuery()
                try:
                    # q.exec_("""INSERT INTO SECINFO VALUES ('%s','%s','%s','%s')""" % (code, name, insttype, exchange))
                    # QtSql.QSqlDatabase().commit()
                    return name, insttype, exchange
                except Exception, e:
                    print e.message
                    # QtSql.QSqlDatabase().rollback()

    def getInstData(self):
        fields = self.windFieldRequests()
        if fields:
            windFields = [f[0] for f in fields]
            result = w.wss(unicode(self.code), windFields, 'tradeDate={0}'.format(format(datetime.datetime.today(), '%Y%m%d')))
            if result:
                if result.ErrorCode == 0:
                    for i in range(len(fields)):
                        self.__setattr__(fields[i][1], fields[i][2] and fields[i][2](result.Data[i][0]) or result.Data[i][0])
                    self.initOK = True
        else:
            self.initOK = True


class CashBond(InstrumentBase):
    def __init__(self, code):
        super(CashBond, self).__init__(code)
        if self.initOK:
            if self.couponType == u'固定利率':
                pass
            elif self.couponType == u'浮动利率':
                pass
            else:
                raise NotImplementedError('Unknown coupon type %s' % self.couponType)

    def windFieldRequests(self):
        return [ ('issuerupdated', 'issuer', None),            # 发行人
                 ('issueamount', 'issueAmount', None),         # 发行规模
                 ('windl1type', 'bondType', None),             # 债券类别
                 ('industry_gics', 'industry', None),          # 行业
                 ('maturitydate', 'maturityDate', lambda x:x.date()),       # 到期日
                 ('actualbenchmark', 'dcc', None),             # day count convention
                 ('term', 'issueTerm', None),                  # 发行期限
                 ('couponrate', 'coupon', None),               # 票息
                 ('carrydate', 'accrualDate', lambda x:x.date()),  # 起息日
                 ('interesttype', 'isFixedCoupon', lambda x:x==u'固定利率'),         # 利率类型 '固定利率' or '浮动利率'
                 ('interestfrequency', 'numCpnPerYear', None), # 每年付息次数
                 ('latestissurercreditrating', 'issuerRating', None),  # 主体评级
                 ('issurercreditratingcompany', 'ratingAgent', None),  # 发行人主体评级机构
                 ('amount', 'bondRating', None),               # 债项评级
                 ('agency_guarantor', 'guarantor', None),      # 担保人
                 ('agency_grnttype', 'guarantType', None),     # 担保方式
                 ('lastdate_cnbd', 'lastVDate', lambda x:x.date()),         # 最新估值日
                 ('subordinateornot', 'isSub', lambda x:x==u'是'),          # 次级债？
                 ('municipalbond', 'isMuni', lambda x:x==u'是'),            # 城投债？
                 ('embeddedopt', 'hasOpt', lambda x:x==u'是'),              # 含权？
                 ('nature', 'issuerBackground', None)                # 发行人属性：民营企业，地方国有企业，中央国有企业，公众企业
                ]

    def isPrivate(self):
        return self.issuerBackground not in [u'地方国有企业', u'中央国有企业']

    def cashflows(self):
        if self.numCpnPerYear is None:  # 到期一次还本付息或零息
            if self.coupon is None:
                return {self.maturityDate : 100.}
            else:
                return {self.maturityDate : YearFrraction(self.dcc, self.accrualDate, self.maturityDate)*self.coupon+100.}
        else:
            pass