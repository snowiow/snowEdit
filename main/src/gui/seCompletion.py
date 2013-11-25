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
        self._BUILTINS = {'null', 'true', 'false', 'alias', 'as',
                          'const', 'delete', 'do', 'else', 'enum', 'for',
                              'function', 'if', 'import', 'in', 'is', 'new',
                              'package', 'private', 'protected', 'public',
                              'ref', 'return', 'shared', 'static', 'template',
                              'type', 'this', 'throw', 'try', 'union',
                              'unique', 'while', 'with'}

        words = self._BUILTINS | s
        QtGui.QCompleter.__init__(self, list(words))

        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setMaxVisibleItems(10)
        self.setModel(QtGui.QStringListModel(list(words)))

        self.allWordsDict = {word: 0 for word in words}

        self.createConnects()


    @QtCore.Slot()
    def updateWordCount(self, word):
        """
        updates the count of a word if it was activated in the autocompletion
        """
        if word in self.allWordsDict:
            self.allWordsDict[word] += 1
        else:
            self.allWordsDict[word] = 1

    def updateAllWords(self, words):
        """
        adapts the allWordsDIct to the words list
        """
        for word in words:
            if word not in self.allWordsDict:
                self.allWordsDict[word] = 0

    def getCurrentWordsDict(self, words):
        """
        creates a dict version of the current words, which are in the
        autocompletion with their overall count
        """
        curDict = {}
        for word in words:
            curDict[word] = self.allWordsDict[word]
        return curDict

    def createSortedWordsList(self, dic):
        """
        Creates a sorted List from a dict, ascending by the count of the
        word
        """
        result = []
        for word in sorted(dic, key=dic.get, reverse=True):
            result.append(word)
        return result

    def updateWords(self, ws):
        """
        Adds words to the existing list, which aren't already in the list
        """
        words = self._BUILTINS | ws
        self.updateAllWords(words)
        curDict = self.getCurrentWordsDict(words)
        self.model().setStringList(self.createSortedWordsList(curDict))

    def createConnects(self):
        self.connect(self, QtCore.SIGNAL("activated(const QString&)"),
                     self.updateWordCount)

