'''
Created on 17.07.2013

@author: marcel
'''
#-*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser

import os.path
from helperFunctions import getApplicationPath, fileIsEmpty


#Ini Manager is singleton
class IniManager(SafeConfigParser):
    INSTANCE = None
    PATH = None
    
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
        self.PATH = getApplicationPath().rsplit("/",2)[0] + '/cfg/options.ini'
        if not os.path.isfile(self.PATH):
            self.createNewIni()
        elif fileIsEmpty(self.PATH):
            self.createNewIni()
            
    def createNewIni(self):
        self.add_section('Editor')
        self.set('Editor', 'showLineNumbers', 'True')
        self.set('Editor', 'highlightCurrentLine', 'True')
          
        iniFile = open(self.PATH, 'w')
        self.write(iniFile)        
        iniFile.close()
        
    def saveIni(self, section, option, value):
        self.set(section, option, value)   
        iniFile = open(self.PATH, 'w')
        self.write(iniFile)        
        iniFile.close()
    
    def readBoolean(self, section, option):
        self.read(self.PATH)
        return self.getboolean(section, option)