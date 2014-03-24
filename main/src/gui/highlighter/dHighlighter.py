#-*- coding: utf-8 -*-

from PySide import QtGui, QtCore


class DHighlighter(QtGui.QSyntaxHighlighter):
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
            '\\babstract\\b', '\\balias\\b', '\\balign\\b', '\\basm\\b',
            '\\bassert\\b', '\\bauto\\b', '\\bbody\\b', '\\bbool\\b',
            '\\bbreak\\b', '\\bbyte\\b', '\\bcase\\b', '\\bcast\\b',
            '\\bcast\\b', '\\bcatch\\b', '\\bcdouble\\b', '\\bcent\\b',
            '\\bcfloat\\b', '\\bchar\\b', '\\bclass\\b', '\\bconst\\b',
            '\\bsignals\\b', '\\bsigned\\b', '\\bslots\\b', '\\bstatic\\b',
            '\\bcontinue\\b', '\\bcreal\\b', '\\bdchar\\b', '\\bdebug\\b',
            '\\bdefault\\b', '\\bdeprecated\\b', '\\bdo\\b', '\\bdouble\\b',
            '\\belse\\b', '\\benum\\b', '\\bexport\\b', '\\bextern\\b',
            '\\bfalse\\b', '\\bfinal\\b', '\\bfinally\\b', '\\bfloat\\b',
            '\\bfor\\b', '\\bforeach\\b', '\\bforeach_reverse\\b',
            '\\bfunction\\b', '\\bgoto\\b', '\\bidouble\\b', '\\bif\\b',
            '\\bifloat\\b', '\\bimmutable\\b', '\\bimport\\b', '\\bin\\b',
            '\\binout\\b', '\\bint\\b', '\\binterface\\b', '\\binvariant\\b',
            '\\bireal\\b', '\\bis\\b', '\\blazy\\b', '\\blong\\b',
            '\\bmacro\\b', '\\bmixin\\b', '\\bmodule\\b', '\\bnew\\b',
            '\\bnothrow\\b', '\\bnull\\b', '\\bout\\b', '\\boverride\\b',
            '\\bpackage\\b', '\\bpragma\\b', '\\bprivate\\b', '\\bpublic\\b',
            '\\bprotected\\b', '\\bpure\\b', '\\breal\\b', '\\bref\\b',
            '\\breturn\\b', '\\bscope\\b', '\\bshared\\b', '\\bshort\\b',
            '\\bstatic\\b', '\\bstruct\\b', '\\bsuper\\b', '\\bswitch\\b',
            '\\bsynchronized\\b', '\\btemplate\\b', '\\bthis\\b',
            '\\bthorw\\b', '\\btrue\\b', '\\btry\\b', '\\btypeid\\b',
            '\\btypeof\\b', '\\bubyte\\b', '\\bucent\\b', '\\buint\\b',
            '\\bulong\\b', '\\bunion\\b', '\\bunittest\\b', '\\bushort\\b',
            '\\bversion\\b', '\\bvoid\\b', '\\bwchar\\b', '\\bwhile\\b',
            '\\bwith\\b',
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
            expression = QtCore.QRegExp(pattern)
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

