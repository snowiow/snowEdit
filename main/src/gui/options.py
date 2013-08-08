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
        for key in self.editorOptions.editorBoolOptions:
            self.iniManager.saveIni('Editor', key, str(self.editorOptions.editorBoolOptions[key].isChecked()))
        self.iniManager.setFont(self.editorOptions.font)
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
        somethingChanged = False
        for key in self.editorOptions.editorBoolOptions:
            if self.editorOptions.editorBoolOptions[key].isChecked() != self.iniManager.readBoolean('Editor', key):
                somethingChanged = True
                break

        if self.editorOptions.font != self.iniManager.getFont():
            somethingChanged = True

        if somethingChanged:
            ret = self.createSaveDialog()
            if ret == QtGui.QMessageBox.Save:
                self.saveEditorSettings()

        self.close()

    def createComponents(self):
        self.optionsTypesList = self.OptionTypesList()
        self.editorOptions = self.EditorOptions()

        self.applyButton = QtGui.QPushButton('Apply', self)
        self.abortButton = QtGui.QPushButton('Abort', self)

    def createConnects(self):
        self.applyButton.clicked.connect(self.saveEditorSettings)
        self.abortButton.clicked.connect(self.hasSomethingChanged)

    def createLayout(self):

        stackedLayout = QtGui.QStackedLayout()
        stackedLayout.addWidget(self.editorOptions)

        grid = QtGui.QGridLayout()
        grid.addLayout(stackedLayout, 0, 0)
        grid.addWidget(self.applyButton, 1, 1)
        grid.addWidget(self.abortButton, 1, 2)

        centralLayout = QtGui.QHBoxLayout()

        centralLayout.addWidget(self.optionsTypesList)
        centralLayout.addLayout(grid)
        self.setLayout(centralLayout)

    class OptionTypesList(QtGui.QListView):

        def __init__(self):
            QtGui.QListView.__init__(self)

            self.createComponents()
            self.createLayout()

        def createComponents(self):
            self.model = QtGui.QStandardItemModel(self)

            editorItem = QtGui.QStandardItem(QtGui.QIcon(':icons/editorOptions.png'), 'Editor')
            editorItem.setEditable(False)

            self.model.appendRow(editorItem)

        def createLayout(self):
            self.setModel(self.model)

    class EditorOptions(QtGui.QWidget):

        def __init__(self):
            QtGui.QWidget.__init__(self)

            self.iniManager = IniManager.getInstance()
            self.font = self.iniManager.getFont()
            self.createComponents()
            self.createLayout()
            self.createConnects()

        @QtCore.Slot()
        def showFontDialog(self):
            font, ok = QtGui.QFontDialog.getFont(self.font)
            if ok:
                self.font = font

        def createComponents(self):
            self.lineNumbersCB = QtGui.QCheckBox('Show line numbers', self)
            self.lineNumbersCB.setChecked(self.iniManager.readBoolean('Editor', 'showlinenumbers'))

            self.highlightLineCB = QtGui.QCheckBox('Highlight current line of the cursor', self)
            self.highlightLineCB.setChecked(self.iniManager.readBoolean('Editor', 'highlightcurrentline'))

            #self.highlightLineColorButton = QtGui.QPushButton(self)
            # qss = QtCore.QString("background-color: %1").arg(self.iniManager.read('Editor', 'highlightcurrentlinecolor'))
            # self.highlightLineColorButton.setStyleSheet()

            self.fontButton = QtGui.QPushButton('Change font settings', self)
            self.fontButton.setStyleSheet('text-align:left;'
                                          'text-decoration:underline;')
            self.fontButton.setFlat(True)

        def createLayout(self):
            self.editorBoolOptions = {'showlinenumbers': self.lineNumbersCB,
                                      'highlightcurrentline': self.highlightLineCB}

            grid = QtGui.QGridLayout()
            grid.addWidget(self.lineNumbersCB, 0, 0)
            grid.addWidget(self.highlightLineCB, 1, 0)
            grid.addWidget(self.fontButton, 2, 0)
            self.setLayout(grid)

        def createConnects(self):
            self.fontButton.clicked.connect(self.showFontDialog)