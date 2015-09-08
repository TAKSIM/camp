# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from inst.base import User

class LoginPage(QtGui.QWidget):
    def __init__(self, dbconn):
        QtGui.QWidget.__init__(self)
        self.dbconn = dbconn
        self.setWindowTitle(u'CAMP系统登录')
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
        rightLayout.addWidget(self.username)
        rightLayout.addWidget(self.pwd)
        inputLayout.addLayout(rightLayout)
        layout.addLayout(inputLayout)

        btLayout = QtGui.QHBoxLayout()
        self.btLogin = QtGui.QPushButton(u'登录')
        self.btCancel = QtGui.QPushButton(u'取消')
        self.btLogin.clicked.connect(self.login)
        btLayout.addWidget(self.btLogin)
        btLayout.addWidget(self.btCancel)
        layout.addLayout(btLayout)

        self.setLayout(layout)
        self.show()

    def login(self):
        usr = self.username.text()
        if len(usr) == 0:
            QtGui.QMessageBox.about(None, u'登陆错误', u'用户名不能为空')
        else:
            u = User(usr, self.dbconn)
            if u.id is None:
                QtGui.QMessageBox.about(None, u'登录错误', u'无此用户')
            else:
                if not u.checkPwd(str(self.pwd.text())):
                    QtGui.QMessageBox.about(None, u'登陆错误', u'密码错误')
                else:
                    return True

if __name__ == '__main__':
    import sys
    import env
    app = QtGui.QApplication(sys.argv)
    db = env.Dbconfig('hewei','wehea1984')
    db.Connect()
    w = LoginPage(db.conn)
    sys.exit(app.exec_())