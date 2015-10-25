# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from env import User

class LoginPage(QtGui.QWidget):

    loginSuccess = QtCore.pyqtSignal()

    def __init__(self, dbconn):
        QtGui.QWidget.__init__(self)
        self.dbconn = dbconn
        self.setWindowTitle(u'系统登录')
        self.setWindowIcon(QtGui.QIcon(u'icons\login.png'))
        self.setFixedSize(180,100)

        layout = QtGui.QVBoxLayout()
        inputLayout = QtGui.QHBoxLayout()

        leftLayout = QtGui.QVBoxLayout()
        leftLayout.addWidget(QtGui.QLabel(u'用户名'))
        leftLayout.addWidget(QtGui.QLabel(u'密码'))
        inputLayout.addLayout(leftLayout)

        rightLayout = QtGui.QVBoxLayout()
        self.username = QtGui.QLineEdit()
        self.pwd = QtGui.QLineEdit()
        self.pwd.setEchoMode(QtGui.QLineEdit.Password)
        self.pwd.setFont(QtGui.QFont('calibri',10))
        self.pwd.returnPressed.connect(self.login)
        rightLayout.addWidget(self.username)
        rightLayout.addWidget(self.pwd)
        inputLayout.addLayout(rightLayout)
        layout.addLayout(inputLayout)

        btLayout = QtGui.QHBoxLayout()
        self.btLogin = QtGui.QPushButton(u'登录')
        self.btReset = QtGui.QPushButton(u'重置密码')
        self.btLogin.clicked.connect(self.login)
        self.btReset.clicked.connect(self.resetPwd)
        btLayout.addWidget(self.btLogin)
        btLayout.addWidget(self.btReset)
        layout.addLayout(btLayout)

        self.setLayout(layout)

        self.resetPage = None

    def login(self):
        usr = self.username.text()
        if len(usr) == 0:
            QtGui.QMessageBox.warning(None, u'登陆错误', u'用户名不能为空')
        else:
            u = User(usr, self.dbconn)
            if u.id is None:
                QtGui.QMessageBox.warning(None, u'登录错误', u'无此用户')
            else:
                if not u.checkPwd(str(self.pwd.text())):
                    QtGui.QMessageBox.warning(None, u'登陆错误', u'密码错误')
                else:
                    self.loginSuccess.emit()
                    self.close()

    def resetPwd(self):
        usr = self.username.text()
        if len(usr) == 0:
            QtGui.QMessageBox.warning(None, u'登陆错误', u'用户名不能为空')
        else:
            u = User(usr, self.dbconn)
            if u.id is None:
                QtGui.QMessageBox.warning(None, u'登录错误', u'无此用户')
            else:
                u.initPwd(self.dbconn)
                self.resetPage = ResetPage(self.dbconn, u)
                self.resetPage.sgOK.connect(self.loginOK)
                self.resetPage.show()

    def loginOK(self):
        self.loginSuccess.emit()
        self.close()

class ResetPage(QtGui.QWidget):

    sgOK = QtCore.pyqtSignal()

    def __init__(self, dbconn, user):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle(u'重置登录密码')
        self.setWindowIcon(QtGui.QIcon(u'icons\login.png'))
        self.setFixedSize(200, 130)
        self.dbconn = dbconn
        self.user = user
        self.pwdLayout = QtGui.QGridLayout()
        self.pwdLayout.addWidget(QtGui.QLabel(u'临时密码'), 0, 0, 1, 1)
        self.pwdLayout.addWidget(QtGui.QLabel(u'重置密码'), 1, 0, 1, 1)
        self.pwdLayout.addWidget(QtGui.QLabel(u'再次确认'), 2, 0, 1, 1)
        self.tmpPwd = QtGui.QLineEdit()
        self.tmpPwd.setEchoMode(QtGui.QLineEdit.Password)
        self.pwdLayout.addWidget(self.tmpPwd, 0, 1, 1, 2)
        self.newPwd = QtGui.QLineEdit()
        self.newPwd.returnPressed.connect(self.ok_clicked)
        self.newPwd.setEchoMode(QtGui.QLineEdit.Password)
        self.pwdLayout.addWidget(self.newPwd, 1, 1, 1, 2)
        self.confPwd = QtGui.QLineEdit()
        self.confPwd.returnPressed.connect(self.ok_clicked)
        self.confPwd.setEchoMode(QtGui.QLineEdit.Password)
        self.pwdLayout.addWidget(self.confPwd, 2, 1, 1, 2)
        self.btOK = QtGui.QPushButton(u'确认')
        self.btOK.clicked.connect(self.ok_clicked)
        self.pwdLayout.addWidget(self.btOK, 3, 1, 1, 1)
        self.setLayout(self.pwdLayout)

    def ok_clicked(self):
        tmpPwd = str(self.tmpPwd.text())
        if self.user.checkPwd(tmpPwd):
            newPwd = str(self.newPwd.text())
            if len(newPwd) == 0:
                QtGui.QMessageBox.warning(None, u'错误', u'新密码不能为空')
            else:
                confPwd = self.confPwd.text()
                if newPwd == confPwd:
                    self.user.resetPwd(newPwd, self.dbconn)
                    self.sgOK.emit()
                    self.close()
                else:
                    QtGui.QMessageBox.warning(None, u'错误', u'两次输入的密码不一致')
        else:
            QtGui.QMessageBox.warning(None, u'错误', u'临时密码无效')



if __name__ == '__main__':
    import sys
    import env
    app = QtGui.QApplication(sys.argv)
    db = env.Dbconfig('hewei', 'wehea1984')
    db.Connect()
    u = User('000705', db.conn)
    w = ResetPage(db.conn, u)
    w.show()
    sys.exit(app.exec_())