#-*- coding: utf-8 -*-
from helperFunctions import getApplicationPath
from ctypes import *


class DArray(Structure):
    _fields_ = [("length", c_uint),
                ("capacity", c_uint),
                ("elems", POINTER(c_char_p))]


class RaschLexer():

    """
    RaschLexer is a class, which is needed for the autocompletion in snowedit.
    The RaschLexer tokenizes the text within the editor and filters the
    important informations
    """

    def __init__(self):
        print getApplicationPath()
        self.lib = CDLL(getApplicationPath() +
                        "/main/src/resources/lib/linux/libSnowEdit.so")

        self.lib.tokenize.argtypes = [c_char_p]
        self.lib.tokenize.restype = POINTER(DArray)

        self.lib.dArrayFree.argtypes = [POINTER(DArray)]

    def getVariables(self, text):

        variables = set([])

        pointer = self.lib.tokenize(c_char_p(text))
        ret = pointer.contents
        for i in range(ret.length):
            variables.update([ret.elems[i]])

        #self.lib.dArrayFree(pointer)

        return variables

