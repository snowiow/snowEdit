#encoding: utf-8 -*-

"""
Code Conventions of this project for a better reading:
files: camelCase
classes: CamelCase
methods: camelCase
variables: camelCase
private variables: _camelCase
protected variables: _camelCase
constants: NAME
"""

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
