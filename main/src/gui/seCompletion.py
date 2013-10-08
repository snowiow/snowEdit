#-*- coding: utf-8 -*-

from PySide import QtGui, QtCore


class SeCompletion(QtGui.QCompleter):

    def __init__(self, s=set([])):
        """
            SeCompletion implements the QCompleter and holds the
            autocompleteList.
            It is a popup completion, cas insensitive and works with a set
            instead of
            a list, because of avoiding duplicates
            """
        self._BUILTINS = set([u'null', u'true', u'false'])
        self.words = self._BUILTINS | s
        QtGui.QCompleter.__init__(self, list(self.words))

        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setMaxVisibleItems(10)
        self.setModel(QtGui.QStringListModel(list(self.words)))

    def updateWords(self, ws):
        """
        Adds words to the existing list, which aren't already in the list
        """
        self.words = self._BUILTINS | ws
        self.model().setStringList(list(self.words))

    def avgWordLength(self):
        """Calculates the rounded average word length"""
        totalLength = 0
        for word in self.words:
            totalLength += len(word)

        return round(totalLength / len(self.words))



