# -*- coding: utf-8 -*-
import hashlib
import MySQLdb

def enum(**enums):
    return type('Enum', (), enums)

class Dbconfig:
    def __init__(self, user, pwd, host='caitcfid.mysql.rds.aliyuncs.com', port=3306, dbname='secs'):
        self.user = user
        self.pwd = pwd
        self.host = host
        self.port = port
        self.dbname = dbname
        self.conn = None

    def Connect(self):
        if self.conn is None:
            self.conn = MySQLdb.connect(host=self.host,user=self.user, passwd=self.pwd, db=self.dbname, port=self.port, charset='utf8')

    def Close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

class Book:
    def __init__(self, id, name_en, name_cn_full, name_cn_short, startDate = None):
        self.id = id
        self.name_en = name_en
        self.name_cn_full = name_cn_full
        self.name_cn_short = name_cn_short
        self.startDate = startDate

    def LoadTrades(self, dbconn):
        c = dbconn.cursor()
        c.execute('SELECT * FROM TRADES WHERE BOOK={}'.format(self.name_en))
        c.close()

def LoadBooks(dbconn):
    c = dbconn.cursor()
    c.execute('SELECT * FROM BOOKS')
    bs = c.fetchall()
    c.close()
    books = [Book(b[0],b[1],b[3],b[2],b[4]) for b in bs]
    return books

class User:
    def __init__(self, id, dbconn):
        c = dbconn.cursor()
        try:
            c.execute('SELECT * FROM USERS WHERE ID={}'.format(id))
            u = c.fetchall()
            if u:
                self.id = id
                self.name = u[0][1]
                self.email = u[0][2]
                self.role = u[0][3]
                self.pwd = u[0][4]
                self.pwdtmp = u[0][5]
            else:
                self.id = None
        finally:
            c.close()

    def needPwdReset(self):
        return self.pwdtmp != 0

    def checkPwd(self, pwd):
        return hashlib.sha1(pwd).hexdigest() == self.pwd

    def resetPwd(self, newpwd, dbconn):
        hex = hashlib.sha1(newpwd).hexdigest()
        c = dbconn.cursor()
        try:
            query = """UPDATE USERS SET PWD='%s', PWD_TEMP=0 WHERE ID=%s""" % (hex, self.id)
            print query
            c.execute(query)
            dbconn.commit()
            self.pwd = hex
        finally:
            c.close()

    def initPwd(self, dbconn):
        import random
        import string
        import utils
        initpwd = ''.join(random.choice(string.ascii_letters) for i in range(6))
        hex = hashlib.sha1(initpwd).hexdigest()
        utils.sendmail('CAITC-FID@caitc.cn',[self.email], u'重设CAMP密码', initpwd)
        c = dbconn.cursor()
        try:
            query = """UPDATE USERS SET PWD='%s', PWD_TEMP=1 WHERE ID=%s""" % (hex, self.id)
            print query
            c.execute(query)
            dbconn.commit()
            self.pwd = hex
        finally:
            c.close()
