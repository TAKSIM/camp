# -*- coding: utf-8 -*-
from PyQt4 import QtGui
import login
import frame
import env
import sys

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dt = frame.Desktop()
    sys.exit(app.exec_())