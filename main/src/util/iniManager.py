'''
Created on 17.07.2013

@author: marcel
'''
#-*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser

import os.path
from PySide import QtGui
from helperFunctions import getApplicationPath, fileIsEmpty


# Ini Manager is singleton
class IniManager(SafeConfigParser):
    INSTANCE = None

    def __init__(self):
        if self.INSTANCE is not None:
            raise ValueError("An instantiation already exists!")

    @classmethod
    def getInstance(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = IniManager()
            SafeConfigParser.__init__(cls.INSTANCE)
            return cls.INSTANCE
        else:
            return cls.INSTANCE

    def checkExistingIniFile(self):
        print getApplicationPath()
        self.PATH = getApplicationPath() + '/cfg/options.ini'
        if not os.path.isfile(self.PATH):
            self.createNewIni()
        elif fileIsEmpty(self.PATH):
            self.createNewIni()

    def createNewIni(self):
        self.add_section('Editor')
        self.set('Editor', 'showLineNumbers', 'True')
        self.set('Editor', 'highlightCurrentLine', 'True')
        self.set('Editor', 'tabSize', '4')
        self.set('Editor', 'fontFamily', 'Courier')
        self.set('Editor', 'fontSize', '10')
        self.set('Editor', 'fontBold', 'False')
        self.set('Editor', 'fontItalic', 'False')
        self.set('Editor', 'fontUnderline', 'False')
        self.set('Editor', 'fontStrikeOut', 'False')

        self.add_section('Compiler')
        self.set('Compiler', 'path', '')
        self.set('Compiler', 'flags', '')

        iniFile = open(self.PATH, 'w')
        self.write(iniFile)
        iniFile.close()

    def saveIni(self, section, option, value):
        self.set(section, option, str(value))
        iniFile = open(self.PATH, 'w')
        self.write(iniFile)
        iniFile.close()

    def readBoolean(self, section, option):
        self.read(self.PATH)
        return self.getboolean(section, option)

    def readInt(self, section, option):
        self.read(self.PATH)
        return self.getint(section, option)

    def readString(self, section, option):
        self.read(self.PATH)
        return self.get(section, option)

    def getFont(self):
        font = QtGui.QFont()
        font.setFamily(self.readString('Editor', 'fontFamily'))
        font.setPointSize(self.readInt('Editor', 'fontSize'))
        font.setBold(self.readBoolean('Editor', 'fontBold'))
        font.setItalic(self.readBoolean('Editor', 'fontItalic'))
        font.setUnderline(self.readBoolean('Editor', 'fontUnderline'))
        font.setStrikeOut(self.readBoolean('Editor', 'fontStrikeOut'))
        return font

    def setFont(self, font):
        self.saveIni('Editor', 'fontFamily', font.family())
        self.saveIni('Editor', 'fontSize', str(font.pointSize()))
        self.saveIni('Editor', 'fontBold', str(font.bold()))
        self.saveIni('Editor', 'fontItalic', str(font.italic()))
        self.saveIni('Editor', 'fontUnderline', str(font.underline()))
        self.saveIni('Editor', 'fontStrikeOut', str(font.strikeOut()))
