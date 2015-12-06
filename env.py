# -*- coding: utf-8 -*-
import hashlib
import MySQLdb
from PyQt4 import QtSql

sysIcon = r'icons\tent.png'

def enum(**enums):
    return type('Enum', (), enums)

# class Dbconfig:
#     def __init__(self, user, pwd, host='caitcfid.mysql.rds.aliyuncs.com', port=3306, dbname='secs'):
#         self.user = user
#         self.pwd = pwd
#         self.host = host
#         self.port = port
#         self.dbname = dbname
#         self.conn = None
#
#     def Connect(self):
#         if self.conn is None:
#             self.conn = MySQLdb.connect(host=self.host,user=self.user, passwd=self.pwd, db=self.dbname, port=self.port, charset='utf8')
#
#     def Close(self):
#         if self.conn is not None:
#             self.conn.close()
#             self.conn = None

class User:
    def __init__(self, id):
        self.id = None
        q = QtSql.QSqlQuery()
        q.exec_('SELECT * FROM USERS WHERE ID={}'.format(id))
        while q.next():
            self.id = str(q.value(0).toString())
            self.name = str(q.value(1).toString())
            self.email = str(q.value(2).toString())
            self.role = q.value(3).toInt()[0]
            self.pwd = str(q.value(4).toString())
            self.pwdtmp = q.value(5).toInt()[0]

    def needPwdReset(self):
        return self.pwdtmp != 0

    def checkPwd(self, pwd):
        return hashlib.sha1(pwd).hexdigest() == self.pwd

    def resetPwd(self, newpwd):
        hex = hashlib.sha1(newpwd).hexdigest()
        q = QtSql.QSqlQuery()
        query = """UPDATE USERS SET PWD='%s', PWD_TEMP=0 WHERE ID=%s""" % (hex, self.id)
        print query
        q.exec_(query)
        QtSql.QSqlDatabase().commit()
        self.pwd = hex

    def initPwd(self):
        import random
        import string
        import utils
        initpwd = ''.join(random.choice(string.ascii_letters) for i in range(6))
        hex = hashlib.sha1(initpwd).hexdigest()
        utils.sendmail('CAITC-FID@caitc.cn', [self.email], u'重设CAMP密码', initpwd)
        q = QtSql.QSqlQuery()
        query = """UPDATE USERS SET PWD='%s', PWD_TEMP=1 WHERE ID=%s""" % (hex, self.id)
        q.exec_(query)
        QtSql.QSqlDatabase().commit()
        self.pwd = hex

