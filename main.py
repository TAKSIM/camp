# -*- coding: utf-8 -*-
import sys, os, oss2
cp = os.getcwd()
sys.path.append(cp)
sys.path.append(os.path.join(cp, 'guis'))
from PyQt4 import QtGui
import guis.frame

# check update

app = QtGui.QApplication(sys.argv)
f = guis.frame.Desktop()
sys.exit(app.exec_())
