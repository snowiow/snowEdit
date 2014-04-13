#-*- coding: utf-8 -*-

from PySide import QtGui, QtCore


class CsHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

        self._multiLineCommentFormat = QtGui.QTextCharFormat()
        self._multiLineCommentFormat.setForeground(QtCore.Qt.lightGray)

        self._commentStartExpression = QtCore.QRegExp("/\\*")
        self._commentEndExpression = QtCore.QRegExp("\\*/")

        self.createKeywords()
        self.createOperators()
        self.createStrings()
        self.createArrows()
        self.createComments()

    def createKeywords(self):
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtGui.QColor(64, 155, 11))

        keywords = [
            '\\babstract\\b', '\\bas\\b', '\\bbase\\b', '\\bbool\\b',
            '\\bbreak\\b', '\\bbyte\\b', '\\bcase\\b', '\\bcatch\\b',
            '\\bchar\\b', '\\bchecked\\b', '\\bclass\\b', '\\bconst\\b',
            '\\bcontinue\\b', '\\bdecimal\\b', '\\bdefault\\b',
            '\\bdelegate\\b', '\\bif\\b', '\\bimplicit\\b', '\\bin\\b',
            '\\bdo\\b', '\\bdouble\\b', '\\bint\\b', '\\binterface\\b',
            '\\belse\\b', '\\benum\\b', '\\bevent\\b', '\\bexplicit\\b',
            '\\bextern\\b', '\\bfalse\\b', '\\btrue\\b', '\\binternal\\b',
            '\\bfinally\\b', '\\bfixed\\b', '\\bfloat\\b', '\\bfor\\b',
            '\\bforeach\\b', '\\bgoto\\b', '\\bis\\b', '\\block\\b',
            '\\blong\\b', '\\bnamepsace\\b', '\\bnew\\b', '\\bnull\\b',
            '\\bobject\\b', '\\boperator\\b', '\\bout\\b', '\\boverride\\b',
            '\\bparams\\b', '\\bprivate\\b', '\\bprotected\\b', '\\bpublic\\b',
            '\\breadonly\\b', '\\bref\\b', '\\breturn\\b', '\\bsbyte\\b',
            '\\bsealed\\b', '\\bshort\\b', '\\bsizeof\\b', '\\bstackalloc\\b',
            '\\bstatic\\b', '\\bstring\\b', '\\bstruct\\b', '\\bswitch\\b',
            '\\bthis\\b', '\\bthrow\\b', '\\btry\\b', '\\btypeof\\b',
            '\\buint\\b', '\\bulong\\b', '\\bunchecked\\b', '\\bunsafe\\b',
            '\\bushort\\b', '\\busing\\b', '\\bvirtual\\b', '\\bvoid\\b',
            '\\bvolatile\\b', '\\bwhile\\b'
        ]

        self.highlightingRules = [(QtCore.QRegExp(pattern), keywordFormat)
                                  for pattern in keywords]

    def createOperators(self):
        operatorFormat = QtGui.QTextCharFormat()
        operatorFormat.setForeground(QtGui.QColor(148, 99, 233))
        operatorFormat.setFontWeight(QtGui.QFont.Bold)

        operators = ['\\+', '-', '/', '\\*',
                     '=', '==', '!=', '<=', '>=', '<', '>']

        self.highlightingRules.extend(
            [(QtCore.QRegExp(pattern), operatorFormat) for
             pattern in operators])

    def createStrings(self):
        stringFormat = QtGui.QTextCharFormat()
        stringFormat.setForeground(QtCore.Qt.lightGray)
        self.highlightingRules.append((QtCore.QRegExp('\".*\"'), stringFormat))
        self.highlightingRules.append((QtCore.QRegExp('\'.*\''), stringFormat))

    def createArrows(self):
        arrowFormat = QtGui.QTextCharFormat()
        arrowFormat.setForeground(QtCore.Qt.red)
        arrows = ['<-', '->']
        self.highlightingRules.extend(
            [(QtCore.QRegExp(pattern), arrowFormat) for pattern in arrows])

    def createComments(self):
        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(QtCore.Qt.gray)
        self.highlightingRules.append(
            (QtCore.QRegExp('//[^\n]*'), singleLineCommentFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = pattern
            index = expression.indexIn(text)

            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0

        if self.previousBlockState() != 1:
            startIndex = self._commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self._commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + \
                                self._commentEndExpression.matchedLength()

            self.setFormat(
                startIndex, commentLength, self._multiLineCommentFormat)
            startIndex = self._commentStartExpression.indexIn(
                text, startIndex + commentLength)
