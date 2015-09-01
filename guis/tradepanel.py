# -*- coding: utf-8 -*-

from PyQt4 import QtGui

class BondPanel(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle(u'债券交易')
        self.setFixedSize(300,250)
