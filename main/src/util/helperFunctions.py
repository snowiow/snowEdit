#-*- coding: utf-8 -*-
import sys
import os
import re

fileEndPattern = re.compile("^.*\.(\w{2,4})$")


def getApplicationPath():
    path = sys.argv[0]
    path = path.rsplit('\\', 2)[0]
    return path


def getFileName(path):
    if path.find(os.sep) != -1:
        return path.rsplit(os.sep, 1)[1]
    elif path.find('/') != -1:
        return path.rsplit('/', 1)[1]
    return path


def getPathOnly(path):
    if path.find(os.sep) != -1:
        return path.rsplit(os.sep, 1)[0] + os.sep
    elif path.find('/') != -1:
        return path.rsplit('/', 1)[0] + '/'
    return path


def fileIsEmpty(path):
    return os.stat(path).st_size == 0


def normalizeSeps(path):
    return path.replace('\\', '/')