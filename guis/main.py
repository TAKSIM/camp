# -*- coding: utf-8 -*-
import env
import sys
from PyQt4 import QtGui, QtCore
import frame
from tradepanel import BondPanel

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dbconf = env.Dbconfig('hewei','wehea1984')
    dbconf.Connect()
    w = frame.Desktop(dbconf.conn)
    w.show()
    dbconf.Close()
    sys.exit(app.exec_())