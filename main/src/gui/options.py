#-*- coding: utf-8 -*-

from PySide import QtGui, QtCore
from ..util.iniManager import IniManager


class Options(QtGui.QWidget):
    
    def __init__(self, codeEdits):
        QtGui.QWidget.__init__(self)

        self.codeEdits = codeEdits
        self.iniManager = IniManager.getInstance()

        self.createComponents()
        self.createLayout()
        self.createConnects()

        self.setWindowTitle('Options')
        self.setWindowIcon(QtGui.QIcon(':icons/options.png'))
        self.setGeometry(100, 100, 300, 300)
        self.show()

    @QtCore.Slot()
    def saveEditorSettings(self):
        for key in self.editorOptions:
            self.iniManager.saveIni('Editor', key, str(self.editorOptions[key].isChecked()))
        for editor in self.codeEdits:
            editor.updateOptions()
        self.close()

    def createSaveDialog(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setIconPixmap(':icons/warning.png')
        msgBox.setWindowIcon(QtGui.QIcon(':icons/warning.png'))
        msgBox.setText('There are unsaved changes!')
        msgBox.setInformativeText('Do you want to save your changes?')
        msgBox.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard)
        msgBox.setDefaultButton(QtGui.QMessageBox.Save)
        ret = msgBox.exec_()
        return ret

    @QtCore.Slot()
    def hasSomethingChanged(self):
        for key in self.editorOptions:
            if self.editorOptions[key].isChecked() != self.iniManager.readBoolean('Editor', key):
                ret = self.createSaveDialog()
                if ret == QtGui.QMessageBox.Save:
                    self.saveEditorSettings
        self.close()

    def createComponents(self):
        self.headlineFont = QtGui.QFont('Arial', 18, QtGui.QFont.Bold)
        self.editorLabel = QtGui.QLabel('Editor', self)
        self.editorLabel.setFont(self.headlineFont)

        self.lineNumbersCB = QtGui.QCheckBox('Show line numbers', self)
        self.lineNumbersCB.setChecked(self.iniManager.readBoolean('Editor', 'showlinenumbers'))

        self.highlightLineCB = QtGui.QCheckBox('Highlight current line of the cursor', self)
        self.highlightLineCB.setChecked(self.iniManager.readBoolean('Editor', 'highlightcurrentline'))

        self.applyButton = QtGui.QPushButton('Apply', self)
        self.abortButton = QtGui.QPushButton('Abort', self)

    def createConnects(self):
        self.applyButton.clicked.connect(self.saveEditorSettings)
        self.abortButton.clicked.connect(self.hasSomethingChanged)

    def createLayout(self):
        self.editorOptions = {'showlinenumbers': self.lineNumbersCB,
                              'highlightcurrentline': self.highlightLineCB}

        grid = QtGui.QGridLayout()
        grid.addWidget(self.editorLabel, 0, 0)
        grid.addWidget(self.lineNumbersCB, 1,0)
        grid.addWidget(self.highlightLineCB, 2, 0)
        grid.addWidget(self.applyButton, 3, 1)
        grid.addWidget(self.abortButton, 3, 2)
        self.setLayout(grid)