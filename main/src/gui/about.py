__author__ = 'marcel'

from PySide import QtGui, QtCore


class About(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.createComponents()
        self.createConnects()
        self.createLayout()
        self.setWindowTitle('About')
        self.setWindowIcon(QtGui.QIcon(':icons/snow_logo'))
        self.show()

    def createComponents(self):
        iconPixMap = QtGui.QPixmap(':icons/snow_logo')
        self.iconLabel = QtGui.QLabel(self)
        self.iconLabel.setPixmap(iconPixMap)
        self.textLabel = QtGui.QLabel(self)
        self.textLabel.setOpenExternalLinks(True)
        self.textLabel.setTextFormat(QtCore.Qt.RichText)
        self.textLabel.setText("snowEdit Version 0.1 <br />" +
                               "(c) Copyright Marcel Patzwahl, 2013. All rights reserved.<br />" +
                               "This Software is developed by Marcel Patzwahl. <br />" +
                               "Also big thanks to <a href=\"http://www.fatcow.com\" >Fatcow</a>" +
                               " for providing such a big and nice icon pack. <br />" +
                               "This Software is based on Python 2.7.5 and Pyside 1.2.")
        self.closeButton = QtGui.QPushButton('Close', self)

    def createConnects(self):
        self.closeButton.clicked.connect(self.close)

    def createLayout(self):
        grid = QtGui.QGridLayout()

        grid.addWidget(self.iconLabel, 0, 0)
        grid.addWidget(self.textLabel, 1, 0)
        grid.addWidget(self.closeButton, 2, 1)

        self.setLayout(grid)
