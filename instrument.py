# -*- coding: utf-8 -*-
from PyQt4 import QtSql, QtGui
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
            result = w.wss(unicode(self.code), windFields, 'tradeDate={0}'.format(format(datetime.datetime.today(), '%Y%m%d')),  'industryType=1')
            if result:
                if result.ErrorCode == 0:
                    for i in range(len(fields)):
                        if fields[i][2]:
                            self.__setattr__(fields[i][1], fields[i][2](result.Data[i][0]))
                        else:
                            self.__setattr__(fields[i][1], result.Data[i][0])
                    self.initOK = True
        else:
            self.initOK = True

    def gui(self, readonly=True, asOfDate=None):
        return None

class Cash(InstrumentBase):
    def __init__(self, code, cashDate, ccy='CNY'):
        super(Cash, self).__init__(code)
        self.date = cashDate
        self.ccy = ccy

    def cashflows(self):
        return {self.date:1.}

    def gui(self, readonly=True, asOfDate=None):
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'账户'), 0, 0, 1, 1)
        acct = QtGui.QLineEdit(self.code=='CASH_IB' and u'银行间' or u'交易所')
        acct.setReadOnly(readonly)
        layout.addWidget(self.acct, 0, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'币种'), 1, 0, 1, 1)
        ccyline = QtGui.QLineEdit(self.ccy=='CNY' and u'人民币' or self.ccy)
        ccyline.setReadOnly(readonly)
        layout.addWidget(ccyline, 1, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'预期时间'), 2, 0, 1, 1)
        d = QtGui.QDateEdit(self.date)
        d.setCalendarPopup(True)
        d.setReadOnly(readonly)
        layout.addWidget(d, 2, 1, 1, 1)
        return layout

class CashBond(InstrumentBase):
    def __init__(self, code):
        super(CashBond, self).__init__(code)

    def windFieldRequests(self):
        return [ ('issuerupdated', 'issuer', None),            # 发行人
                 ('issueamount', 'issueAmount', None),         # 发行规模
                 ('windl1type', 'bondType', None),             # 债券类别
                 ('industry_gics', 'industry', None),          # 行业
                 ('maturitydate', 'maturityDate', lambda x:x.date()),       # 到期日
                 ('actualbenchmark', 'dcc', None),             # day count convention
                 ('term', 'issueTerm', None),                  # 发行期限
                 ('couponrate', 'coupon', None),               # 票息
                 ('coupon', 'couponType', None),               # 票息品种 (e.g. 到期一次还本付息)
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

    def gui(self, readonly=True, asOfDate=None):
        layout = QtGui.QGridLayout()
        lineNum = 0
        layout.addWidget(QtGui.QLabel(u'代码'), lineNum, 0, 1, 1)
        code = QtGui.QLineEdit(self.code)
        code.setReadOnly(readonly)
        layout.addWidget(code, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'简称'), lineNum, 2, 1, 1)
        name = QtGui.QLineEdit(self.name)
        name.setReadOnly(readonly)
        layout.addWidget(name, lineNum, 3, 1, 1)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'发行人'), lineNum, 0, 1, 1)
        issuer = QtGui.QLineEdit(self.issuer)
        issuer.setReadOnly(readonly)
        layout.addWidget(issuer, lineNum, 1, 1, 3)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'行业'), lineNum, 0, 1, 1)
        industry=QtGui.QLineEdit(self.industry)
        industry.setReadOnly(readonly)
        layout.addWidget(industry, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'发行人类型'), lineNum, 2, 1, 1)
        issuerType = QtGui.QLineEdit(self.issuerBackground)
        issuerType.setReadOnly(readonly)
        layout.addWidget(issuerType, lineNum, 3, 1, 1)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'市场'), lineNum, 0, 1, 1)
        mkt = QtGui.QLineEdit(self.exchange)
        mkt.setReadOnly(readonly)
        layout.addWidget(mkt, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'债券类别'), lineNum, 2, 1, 1)
        bondType = QtGui.QLineEdit(self.bondType)
        bondType.setReadOnly(readonly)
        layout.addWidget(bondType, lineNum, 3, 1, 1)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'到期日'), lineNum, 0, 1, 1)
        matDate = QtGui.QDateEdit(self.maturityDate)
        matDate.setCalendarPopup(True)
        matDate.setReadOnly(readonly)
        layout.addWidget(matDate, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'发行规模'), lineNum, 2, 1, 1)
        issueSize = QtGui.QLineEdit('{:,.0f}'.format(self.issueAmount))
        issueSize.setReadOnly(readonly)
        layout.addWidget(issueSize, lineNum, 3, 1, 1)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'主体评级'), lineNum, 0, 1, 1)
        issuerRating = QtGui.QLineEdit(self.issuerRating)
        issuerRating.setReadOnly(readonly)
        layout.addWidget(issuerRating, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'债项评级'), lineNum, 2, 1, 1)
        bondRating = QtGui.QLineEdit(self.bondRating)
        bondRating.setReadOnly(readonly)
        layout.addWidget(bondRating, lineNum, 3, 1, 1)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'评级机构'), lineNum, 0, 1, 1)
        ratingAgent = QtGui.QLineEdit(self.ratingAgent)
        ratingAgent.setReadOnly(readonly)
        layout.addWidget(ratingAgent, lineNum, 1, 1, 3)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'当期票息'), lineNum, 0, 1, 1)
        coupon = QtGui.QLineEdit('{:.2f}'.format(self.coupon))
        coupon.setReadOnly(readonly)
        layout.addWidget(coupon, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'票息品种'), lineNum, 2, 1, 1)
        couponType = QtGui.QLineEdit(self.couponType)
        couponType.setReadOnly(readonly)
        layout.addWidget(couponType, lineNum, 3, 1, 1)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'年付息次数'), lineNum, 0, 1, 1)
        couponFreq = QtGui.QLineEdit(self.numCpnPerYear and str(self.numCpnPerYear) or u'无')
        couponFreq.setReadOnly(readonly)
        layout.addWidget(couponFreq, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'起息日'), lineNum, 2, 1, 1)
        accrualDate = QtGui.QDateEdit(self.accrualDate)
        accrualDate.setCalendarPopup(True)
        accrualDate.setReadOnly(readonly)
        layout.addWidget(accrualDate, lineNum, 3, 1, 1)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'担保人'), lineNum, 0, 1, 1)
        guarantor = QtGui.QLineEdit(self.guarantor or u'无')
        guarantor.setReadOnly(readonly)
        layout.addWidget(guarantor, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'担保方式'), lineNum, 2, 1, 1)
        guarantType = QtGui.QLineEdit(self.guarantType or u'无')
        guarantType.setReadOnly(readonly)
        layout.addWidget(guarantType, lineNum, 3, 1, 1)

        lineNum += 1
        layout.addWidget(QtGui.QLabel(u'含权？'), lineNum, 0, 1, 1)
        hasOption = QtGui.QLineEdit(self.hasOpt and u'是' or u'否')
        hasOption.setReadOnly(readonly)
        layout.addWidget(hasOption, lineNum, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'次级债？'), lineNum, 2, 1, 1)
        isSub = QtGui.QLineEdit(self.isSub and u'是' or u'否')
        isSub.setReadOnly(readonly)
        layout.addWidget(isSub, lineNum, 3, 1, 1)

        return layout

    def cashflows(self):
        if self.numCpnPerYear is None:  # 到期一次还本付息或零息
            if self.coupon is None:
                return {self.maturityDate : 100.}
            else:
                return {self.maturityDate : YearFrraction(self.dcc, self.accrualDate, self.maturityDate)*self.coupon+100.}
        else:
            pass