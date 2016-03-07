# -*- coding: utf-8 -*-
from smtplib import SMTP_SSL as SMTP
from email import Charset
from email.mime.text import MIMEText
from email.header import Header
import datetime

encode = 'utf-8'


def sendmail(sender, to, subject, contents, texttype='plain'):
    Charset.add_charset(encode, Charset.QP, Charset.QP, encode)
    msg = MIMEText(contents, texttype, encode)
    msg['Subject'] = Header(subject.encode(encode), encode).encode()
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    s = SMTP('mail.caitc.cn')
    s.set_debuglevel(False)
    s.login('hewei','WeHeA1984')
    try:
        s.sendmail(sender, to, msg.as_string())
    finally:
        s.quit()


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