'''
Created on 17.07.2013

@author: marcel
'''

#-*- coding: utf-8 -*-
import sys
import os


def getApplicationPath():
    path = sys.argv[0]
    path = path.rsplit('\\', 2)[0]
    return path

def fileIsEmpty(path):
    return os.stat(path).st_size==0