# -*- coding: utf-8 -*-
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
            self.conn = MySQLdb.connect(host=self.host,user=self.user, passwd=self.pwd, db=self.dbname, port=self.port)

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
    c.execute("SET NAMES utf8")
    c.execute("SET CHARACTER_SET_CLIENT=utf8")
    c.execute("SET CHARACTER_SET_RESULTS=utf8")
    c.execute('SELECT * FROM BOOKS')
    bs = c.fetchall()
    c.close()
    books = [Book(b[0],b[1],b[3],b[2],b[4]) for b in bs]
    return books