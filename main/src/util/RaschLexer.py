#-*- coding: utf-8 -*-
from helperFunctions import getApplicationPath
from ctypes import *
from platform import system


class MemPool(Structure):
    _fields_ = [("curLength", c_uint),
                ("totalLength", c_uint),
                ("memory", c_char_p)]


class DArray(Structure):
    _fields_ = [("length", c_uint),
                ("capacity", c_uint),
                ("elems", POINTER(c_char_p)),
                ("m", POINTER(MemPool))]


libPath = getApplicationPath() + "/main/src/resources/lib/"

if system() == "Windows":
    print(libPath + "win/libSnowEdit.dll")
    lib = CDLL(libPath + "win/libSnowEdit.dll")
elif system() == "Linux":
    lib = CDLL(libPath + "linux/libSnowEdit.so")

lib.tokenize.argtypes = [c_char_p]
lib.tokenize.restype = POINTER(DArray)

lib.dArrayFree.argtypes = [POINTER(DArray)]
lib.dArrayFree.restype = None

lib.memPoolFree.argtypes = [POINTER(MemPool)]
lib.memPoolFree.restype = None


def getVariables(text):
    if text != "":
        variables = set([])
        pointer = lib.tokenize(c_char_p(text))
        ret = pointer.contents
        for i in range(ret.length):
            variables.update([ret.elems[i]])

        lib.memPoolFree(ret.m)
        lib.dArrayFree(pointer)
        return variables
    return set([])
