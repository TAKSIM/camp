# -*- coding: utf-8 -*-
from PyQt4 import QtGui
import frame
import sys

if __name__ == '__main__':
    import sys
    sys.path.append(r'c:\temp\camp')
    app = QtGui.QApplication(sys.argv)
    dt = frame.Desktop()
    sys.exit(app.exec_())