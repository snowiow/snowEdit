#-*- coding: utf-8 -*-

from PySide import QtCore, QtGui


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

        self.createKeywords()
        self.createOperators()
        self.createClassVariables()
        self.createStrings()
        self.createSingleLineComments()
        self.createAnnotations()

    def createKeywords(self):
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkBlue)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)

        keywords = ['\\band\\b', '\\bdel\\b', '\\bfor\\b', '\\bas\\b', '\\bassert\\b', '\\bbreak\\b',
                    '\\bclass\\b', '\\bcontinue\\b', '\\bdef\\b', '\\belif\\b', '\\belse\\b', '\\bexcept\\b',
                    '\\bexec\\b', '\\bFalse\\b', '\\bfinally\\b', '\\bfrom\\b', '\\bglobal\\b', '\\bif\\b',
                    '\\bimport\\b', '\\bin\\b', '\\bis\\b', '\\blambda\\b', '\\bNone\\b', '\\bnonlocal\\b',
                    '\\bnot\\b', '\bor\b', '\\bpass\\b', '\\bprint\\b', '\\braise\\b', '\\breturn\\b',
                    '\\bTrue\\b', '\\btry\\b', '\\bwhile\\b', '\\bwith\\b', '\\byield\\b', '\\b<\\b',
                    '\\b<=\\b', '\\b>\\b', r'\\b>=\\b', u'\\b==\\b', '\\b!=\\b']

        self.highlightingRules = [(QtCore.QRegExp(pattern), keywordFormat) for pattern in keywords]

    def createOperators(self):
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.blue)

        keywords = ['+', '-', '/', '*', '(', ')', '[', ']', '{', '}']

        self.highlightingRules.extend([(QtCore.QRegExp(pattern), keywordFormat) for pattern in keywords])

    def createClassVariables(self):
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtGui.QColor(223, 109, 209))

        keywords = ['self', '__init__']

        self.highlightingRules.extend([(QtCore.QRegExp(pattern), keywordFormat) for pattern in keywords])

    def createStrings(self):
        stringFormat = QtGui.QTextCharFormat()
        stringFormat.setForeground(QtCore.Qt.darkGreen)
        self.highlightingRules.append((QtCore.QRegExp('\'.*\''), stringFormat))
        self.highlightingRules.append((QtCore.QRegExp('\".*\"'), stringFormat))

    def createSingleLineComments(self):
        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(QtCore.Qt.gray)
        self.highlightingRules.append((QtCore.QRegExp('#[^\n]*'), singleLineCommentFormat))

    def createAnnotations(self):
        annotationFormat = QtGui.QTextCharFormat()
        annotationFormat.setForeground(QtGui.QColor(108, 204, 255))
        self.highlightingRules.append((QtCore.QRegExp('@[^\n]*'), annotationFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)
