#-*- coding: utf-8 -*-

from PySide import QtGui


class NoneHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

    def highlightBlock(self, text):
        return
