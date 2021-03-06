'''
Created on 14.07.2013

@author: marcel
'''
#-*- coding: utf-8 -*-

from PySide import QtGui, QtCore


class LineNumberArea(QtGui.QWidget):

    def __init__(self, codeEdit):
        self._codeEdit = codeEdit
        QtGui.QWidget.__init__(self, codeEdit)

    def sizeHint(self):
        return QtCore.QSize(self._codeEdit.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self._codeEdit.lineNumberAreaPaintEvent(event)
