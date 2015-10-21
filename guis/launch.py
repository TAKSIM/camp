# -*- coding: utf-8 -*-
from PyQt4 import QtGui
import login
import env
import sys

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    db = env.Dbconfig('hewei','wehea1984')
    db.Connect()
    u = env.User('000705', db.conn)
    w = login.LoginPage(db.conn)
    w.show()
    sys.exit(app.exec_())