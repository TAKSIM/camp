# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QMainWindow()
    w.statusBar().showMessage(u'准备就绪')
    mb = w.menuBar()
    ea = QtGui.QAction(QtGui.QIcon(r'icons\exit.png'), u'&退出', w)
    ea.setShortcut('Ctrl+E')
    ea.setStatusTip(u'退出')
    ea.triggered.connect(QtGui.qApp.quit)

    fm = mb.addMenu(u'&系统')
    fm.addAction(ea)

    w.setWindowTitle(u'固定收益部交易管理平台')
    w.setWindowIcon(QtGui.QIcon(r'icons\todo.png'))
    w.setToolTip(u'This is <b>测试</b>')
    #btn = QtGui.QPushButton(u'退出', w)
    #btn.clicked.connect(QtCore.QCoreApplication.instance().quit)
    #btn.resize(btn.sizeHint())
    w.show()
    sys.exit(app.exec_())