from PyQt4 import QtCore

class Pot(QtCore.QObject):

    temperatureRaisedSignal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)
        self.temperature = 1

    def Boil(self):
        self.temperatureRaisedSignal.emit()
        self.temperature += 1

class Thermometer():
    def __init__(self, pot):
        self.pot = pot
        self.pot.temperatureRaisedSignal.connect(self.temperatureWarning)

    def StartMeasure(self):
        self.pot.Boil()

    def temperatureWarning(self):
        print("Too high temperature!")

if __name__ == '__main__':
    pot = Pot()
    th = Thermometer(pot)
    th.StartMeasure()