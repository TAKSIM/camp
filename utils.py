# -*- coding: utf-8 -*-
from __future__ import print_function
import monthdelta
from smtplib import SMTP_SSL as SMTP
from email import Charset
from email.mime.text import MIMEText
from email.header import Header
import datetime
import oss2
import os, sys

encode = 'utf-8'


def sendmail(sender, to, subject, contents, texttype='plain'):
    Charset.add_charset(encode, Charset.QP, Charset.QP, encode)
    msg = MIMEText(contents, texttype, encode)
    msg['Subject'] = Header(subject.encode(encode), encode).encode()
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    s = SMTP('smtp.exmail.qq.com')
    s.ehlo('smtp.exmail.qq.com')
    s.set_debuglevel(False)
    s.login('hewei@caitc.cn','GMvsBWKwZty47LG2') # access code is generated from web (settings->account->wechat code)
    try:
        s.sendmail(sender, to, msg.as_string())
    finally:
        s.quit()


def YearFrraction(dcc, startDate, endDate):
    if dcc in ['A/365', 'Act/365']:
        return (endDate-startDate).days/365.
    elif dcc in ['Act/Act']:
        return (endDate-startDate).days/365.
    else:
        return None


def DateFwdAdj(dc, startDate, period, adj='F'):
    p = period[-1].upper()
    n = int(period[0:-1])
    if p=='D':
        d = startDate + datetime.timedelta(days=n)
    elif p=='W':
        d = startDate + datetime.timedelta(weeks=n)
    elif p=='M':
        d = startDate + monthdelta.MonthDelta(n)
    elif p=='Y':
        d = startDate + monthdelta.MonthDelta(12*n)
    else:
        return None
    return DateAdj(dc, d, adj)


def DateAdj(dc, d, adj):
    if adj=='N' or dc.IsBusinessDay(d):
        return d
    else:
        nd = dc.NextBusinessDay(d)
        if adj in ['F', 'Following'] or nd.month==d.month:
            return nd
        else:
            return dc.LastBusinessDay(d)


class DateCalculator(object):
    def __init__(self, workdays, holidays):
        self.workdays = workdays
        self.holidays = holidays
        self.oneday = datetime.timedelta(days=1)

    def NextBusinessDay(self, today, numDays=1):
        n = numDays
        t = today
        while n > 0:
            t += self.oneday
            if self.IsBusinessDay(t):
                n -= 1
        return t

    def LastBusinessDay(self, today):
        t = today - self.oneday
        while not self.IsBusinessDay(t):
            t = t - self.oneday
        return t

    def IsBusinessDay(self, t):
        if t.weekday() >= 5:  # sat or sun
            return t in self.workdays
        else:
            return t not in self.holidays


class OSS(object):
    def __init__(self, publicID=None, privateID=None, endPoint=None):
        self.auth = oss2.Auth(publicID or 'KQroupAjGmgioT6R', privateID or 'zapEAIJTOrJnWpW25eB6LIK6PBdOKh')
        self.service = oss2.Service(self.auth, endPoint or 'oss-cn-beijing.aliyuncs.com')
        self.rootBucket = oss2.Bucket(self.auth, 'https://oss-cn-beijing.aliyuncs.com', 'fixedincome')

    def listAllBuckets(self):
        return [b.name for b in oss2.BucketIterator(self.service)]

    def upload_trade_order(self, tradeID, localFilePath):
        fileExtension = localFilePath.split('.')[-1]
        self.rootBucket.put_object_from_file('trade/'+tradeID+'.'+str(fileExtension), localFilePath)
        return True

    # def percentage(self, consumed_bytes, total_bytes):
    #     if total_bytes:
    #         rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
    #         # print('\r{0}% '.format(rate), end='')
    #         # sys.stdout.flush()

    def download_trade_order(self, tradeID, localDir, fname=None, withProgressBar=False):
        for f in oss2.ObjectIterator(self.rootBucket, prefix='trade/'+tradeID):
            fn = f.key
            if fname:
                dfn = '.' in fname and fname or fname + '.' + fn.split('.')[-1]
            else:
                dfn = fn.replace('trade/', '')
            self.rootBucket.get_object_to_file(fn, os.path.join(localDir, dfn), progress_callback=None)
            return True
        return False