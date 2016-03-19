# -*- coding: utf-8 -*-
import hashlib
from PyQt4 import QtSql, QtCore
from WindPy import *

sysIcon = 'guis/icons/tent.png'

def enum(**enums):
    return type('Enum', (), enums)


class User:
    def __init__(self, id):
        self.id = None
        q = QtSql.QSqlQuery()
        q.exec_('SELECT * FROM USERS WHERE ID={}'.format(id))
        while q.next():
            self.id = str(q.value(0).toString())
            self.name = q.value(1).toString()
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


class WindStartThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent=parent)
        self.result = None

    def run(self):
        self.result = w.start(showmenu=False)
