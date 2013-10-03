__author__ = 'marcel'

from PySide import QtGui, QtCore


class SeCompletion(QtGui.QCompleter):
    """
    SeCompletion implements the QCompleter and holds the autocompleteList.
    It is a popup completion, cas insensitive and works with a set instead of
    a list, because of avoiding duplicates
    """

    def __init__(self, s=set([])):
        self.words = set([u'null', u'true', u'false']) | s
        QtGui.QCompleter.__init__(self, list(self.words))

        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setMaxVisibleItems(10)
        self.setModel(QtGui.QStringListModel(list(self.words)))

    def addWords(self, ws):
        '''
        Adds words to the existing list, which aren't already in the list
        '''
        self.words = self.words | ws
        self.model().setStringList(list(self.words))