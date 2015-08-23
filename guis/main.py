# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import frame

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = frame.Desktop()
    w.show()
    sys.exit(app.exec_())