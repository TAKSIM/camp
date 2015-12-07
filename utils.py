# -*- coding: utf-8 -*-
from smtplib import SMTP_SSL as SMTP
from email import Charset
from email.mime.text import MIMEText
from email.header import Header

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
