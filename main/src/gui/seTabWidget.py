__author__ = 'marcel'

from PySide import QtGui, QtCore


class SeTabWidget(QtGui.QTabWidget):

    def __init__(self):
        QtGui.QTabWidget.__init__(self)

    @QtCore.Slot()
    def starTab(self):
        if not self.tabText(self.currentIndex()).endswith('*'):
            self.setTabText(self.currentIndex(),
                            self.tabText(self.currentIndex()) + '*')

    @QtCore.Slot()
    def deleteTab(self, int):
        self.removeTab(int)
