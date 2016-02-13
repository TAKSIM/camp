# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from guis.settings import ColorWhite, ColorRed

class PanelBase(QtGui.QDialog):
    def __init__(self, parent=None, viewOnly=False, **kwargs):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.viewOnly = viewOnly
        if not self.viewOnly:
            self.ok = QtGui.QPushButton(u'确定')
            self.ok.clicked.connect(self.commit)
            self.cancel = QtGui.QPushButton(u'取消')
            self.cancel.clicked.connect(self.close)

    def check_validity(self, raiseWarning=False):
        return True

    def toDB(self):
        pass

    def commit(self, *args, **kwargs):
        if self.check_validity(raiseWarning=True):
            self.toDB()
            self.accept()

    def check_updateWidgetStatus(self, widget, valid, warningMsg=''):
        p = QtGui.QPalette()
        p.setColor(p.Base, valid and ColorWhite or ColorRed)
        widget.setPalette(p)
        if warningMsg:
            widget.setToolTip(warningMsg)