'''
Created on 14.07.2013

@author: marcel
'''
#-*- coding: utf-8 -*-

import sys

from PySide import QtGui

from src.gui.mainWindow import MainWindow
from src.util.iniManager import IniManager


# Initialising config-data
iniManager = IniManager.getInstance()
iniManager.checkExistingIniFile()

app = QtGui.QApplication(sys.argv)

# creating MainWindow and adjusting it
screen_rect = app.desktop().screenGeometry()
width, height = screen_rect.width(), screen_rect.height()
wid = MainWindow()
wid.resize(width - 150, height - 150)

sys.exit(app.exec_())

if __name__ == '__main__':
    pass
