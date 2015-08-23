# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

class Desktop(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle(u'CAMP - 固定收益部交易管理平台')
        self.setWindowIcon(QtGui.QIcon(r'icons\todo.png'))
        #self.setToolTip(u'This is <b>测试</b>')
        self.statusBar().showMessage(u'准备就绪')
        self.setDockOptions(QtGui.QMainWindow.AnimatedDocks | QtGui.QMainWindow.AllowNestedDocks)
        self.setCentralWidget(None)

        self.aw = self.BuildAssetWidget()
        self.lw = self.BuildLiabilityWidget()

        self.menubar = self.BuildMenu()

    def BuildMenu(self):
        mb = self.menuBar()

        m1 = mb.addMenu(u'&系统')
        ea = QtGui.QAction(QtGui.QIcon(r'icons\exit.png'), u'&退出', self)
        ea.setShortcut('Ctrl+E')
        ea.setStatusTip(u'退出')
        ea.triggered.connect(QtGui.qApp.quit)
        m1.addAction(ea)

        m2 = mb.addMenu(u'&交易')
        m3 = mb.addMenu(u'&显示')
        showAW = QtGui.QAction(QtGui.QIcon(),u'资产表',self)
        showAW.setShortcut('Ctrl+A')
        showAW.setStatusTip(u'显示资产表')
        showAW.triggered.connect(self.aw.show)
        m3.addAction(showAW)

        showLW = QtGui.QAction(QtGui.QIcon(),u'负债表',self)
        showLW.setShortcut('Ctrl+L')
        showLW.setStatusTip(u'显示负债表')
        showLW.triggered.connect(self.lw.show)
        m3.addAction(showLW)

        return mb

    def BuildAssetWidget(self):
        w = QtGui.QDockWidget(u'资产',self)
        w.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,w)
        return w

    def BuildLiabilityWidget(self):
        w = QtGui.QDockWidget(u'负债',self)
        w.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,w)
        return w