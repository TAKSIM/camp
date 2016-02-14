# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore


class LogStream(QtCore.QObject):
    message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(LogStream, self).__init__(parent)

    def write(self, message):
        self.message.emit(str(message))


class LogPanel(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LogPanel, self).__init__(parent)
        self.setWindowTitle(u'系统日志')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        self.msg = QtGui.QTextEdit()
        #self.setWidget(self.msg)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.msg)
        self.setLayout(layout)

    def on_stream_update(self, stream):
        self.msg.moveCursor(QtGui.QTextCursor.End)
        self.msg.insertPlainText(stream)