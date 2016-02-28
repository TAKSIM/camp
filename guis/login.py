# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from env import User

class LoginPage(QtGui.QDialog):

    def __init__(self):
        super(LoginPage, self).__init__()
        self.setWindowTitle(u'系统登录')
        self.setWindowIcon(QtGui.QIcon(u'icons\login.png'))
        self.setFixedSize(180,120)

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

        self.status = QtGui.QLabel()
        layout.addWidget(self.status)

        self.setLayout(layout)

    def login(self):
        usr = str(self.username.text())
        if len(usr) == 0:
            self.status.setText(u'登陆错误，用户名不能为空')
        else:
            u = User(usr)
            if u.id is None:
                self.status.setText(u'登陆错误，非注册用户')
            else:
                if not u.checkPwd(str(self.pwd.text())):
                    self.status.setText(u'登陆错误，密码错误')
                else:
                    self.accept()

    def resetPwd(self):
        usr = str(self.username.text())
        if len(usr) == 0:
            self.status.setText(u'登陆错误，用户名不能为空')
        else:
            u = User(usr)
            if u.id is None:
                self.status.setText(u'登陆错误，非注册用户')
            else:
                u.initPwd()
                resetPage = ResetPage(u)
                if resetPage.exec_():
                    self.show()

class ResetPage(QtGui.QDialog):

    def __init__(self, user):
        super(ResetPage, self).__init__()
        self.setWindowTitle(u'重置登录密码')
        self.setWindowIcon(QtGui.QIcon('icons/login.png'))
        self.setFixedSize(200, 130)
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
                    self.user.resetPwd(newPwd)
                    self.accept()
                else:
                    QtGui.QMessageBox.warning(None, u'错误', u'两次输入的密码不一致')
        else:
            QtGui.QMessageBox.warning(None, u'错误', u'临时密码无效')



if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    w = LoginPage()
    w.show()
    sys.exit(app.exec_())