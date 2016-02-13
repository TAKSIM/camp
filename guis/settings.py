# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from matplotlib.font_manager import FontProperties

# system colors
ColorBackground = QtGui.QColor(17,27,28)
ColorBackgroundLight = QtGui.QColor(28,48,49)
ColorTextGray = QtGui.QColor(138,145,138)
ColorTextWhite = QtGui.QColor(234,245,231)
ColorHighlightText = QtGui.QColor(253,180,101)
ColorRed = QtGui.QColor(166,32,39)
ColorBlueBar = QtGui.QColor(184,215,218)
ColorWhite = QtGui.QColor(248, 248, 255)

# set matplotlib font explicitly in order to display chinese properly
figFont = FontProperties(fname=r"C:/windows/fonts/simkai.ttf", size=14)