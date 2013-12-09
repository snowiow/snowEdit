#-*- coding: utf-8 -*-

from PySide import QtGui, QtCore
from ..util.iniManager import IniManager
import re
import os


class OptionCategories(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.iniManager = IniManager.getInstance()


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
        self.setGeometry(100, 100, 700, 400)
        self.show()

    @QtCore.Slot()
    def onApplyButtonClicked(self):
        self.saveEditorSettings()
        self.saveCompilerSettings()
        self.close()

    @QtCore.Slot(QtCore.QModelIndex)
    def showStack(self, index):
        if index.isValid():
            self.stackedLayout.setCurrentIndex(index.row())

    def showStackInt(self, int):
        self.stackedLayout.setCurrentIndex(int)

    @QtCore.Slot()
    def saveEditorSettings(self):
        for key in self.editorOptions.editorBoolOptions:
            self.iniManager.saveIni(
                'Editor', key,
                self.editorOptions.editorBoolOptions[key].isChecked())

        self.iniManager.saveIni('Editor', 'tabsize',
                                self.editorOptions.tabSpinBox.value())

        self.iniManager.setFont(self.editorOptions.font)
        for editor in self.codeEdits:
            editor.updateOptions()

    @QtCore.Slot()
    def saveCompilerSettings(self):
        self.iniManager.saveIni('Compiler', 'path',
                                self.compilerOptions.compilerPath.text())

        flags = self.compilerOptions.compilerFlags.toPlainText()
        self.iniManager.saveIni('Compiler', 'flags', flags)

    def createSaveDialog(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Save')
        msgBox.setIconPixmap(':icons/warning.png')
        msgBox.setWindowIcon(QtGui.QIcon(':icons/warning.png'))
        msgBox.setText('There are unsaved changes!')
        msgBox.setInformativeText('Do you want to save your changes?')
        msgBox.setStandardButtons(
            QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard)
        msgBox.setDefaultButton(QtGui.QMessageBox.Save)
        ret = msgBox.exec_()
        return ret

    @QtCore.Slot()
    def hasSomethingChanged(self):
        somethingChanged = False
        # Has something in editor options changed
        for key in self.editorOptions.editorBoolOptions:
            isChecked = self.editorOptions.editorBoolOptions[key].isChecked()
            if isChecked != self.iniManager.readBoolean('Editor', key):
                somethingChanged = True
                break

        if self.editorOptions.tabSpinBox.value() != self.iniManager.readInt(
                'Editor', 'tabSize'):
            somethingChanged = True

        if self.editorOptions.font != self.iniManager.getFont():
            somethingChanged = True

        # Has something changed in compiler options
        compilerPath = self.compilerOptions.compilerPath.text()
        if self.iniManager.readString('Compiler', 'path') != compilerPath:
                somethingChanged = True

        flags = self.compilerOptions.compilerFlags.toPlainText()
        if self.iniManager.readString('Compiler', 'flags') != flags:
            somethingChanged = True

        if somethingChanged:
            ret = self.createSaveDialog()
            if ret == QtGui.QMessageBox.Save:
                self.saveEditorSettings()
                self.saveCompilerSettings()

        self.close()

    def createComponents(self):
        self.optionsTypesList = self.OptionTypesList()
        self.editorOptions = self.EditorOptions()
        self.compilerOptions = self.CompilerOptions()

        self.applyButton = QtGui.QPushButton('Apply', self)
        self.abortButton = QtGui.QPushButton('Abort', self)

    def createConnects(self):
        self.applyButton.clicked.connect(self.onApplyButtonClicked)
        self.abortButton.clicked.connect(self.hasSomethingChanged)
        self.connect(self.optionsTypesList, QtCore.SIGNAL(
            'clicked(const QModelIndex&)'),
            self, QtCore.SLOT('showStack(const QModelIndex&)'))

    def createLayout(self):
        self.stackedLayout = QtGui.QStackedLayout()
        self.stackedLayout.addWidget(self.editorOptions)
        self.stackedLayout.addWidget(self.compilerOptions)

        grid = QtGui.QGridLayout()
        grid.addLayout(self.stackedLayout, 0, 0)
        grid.addWidget(self.applyButton, 1, 1)
        grid.addWidget(self.abortButton, 1, 2)

        centralLayout = QtGui.QHBoxLayout()

        centralLayout.addWidget(self.optionsTypesList)
        centralLayout.addLayout(grid, 3)
        self.setLayout(centralLayout)

    class OptionTypesList(QtGui.QListView):

        def __init__(self):
            QtGui.QListView.__init__(self)

            self.createComponents()
            self.createLayout()

        def createComponents(self):
            self.model = QtGui.QStandardItemModel(self)
            self.editorItem = QtGui.QStandardItem(
                QtGui.QIcon(':icons/editorOptions.png'), 'Editor')

            self.editorItem.setEditable(False)
            self.compilerItem = QtGui.QStandardItem(
                QtGui.QIcon(':icons/compilerOptions.png'), 'Compiler')

            self.compilerItem.setEditable(False)

            self.model.appendRow(self.editorItem)
            self.model.appendRow(self.compilerItem)

        def createLayout(self):
            self.setModel(self.model)

        def createConnects(self):
            pass

    class EditorOptions(OptionCategories):

        def __init__(self):
            OptionCategories.__init__(self)

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
            self.lineNumbersCB.setChecked(
                self.iniManager.readBoolean('Editor', 'showlinenumbers'))

            self.highlightLineCB = QtGui.QCheckBox(
                'Highlight line of the cursor', self)
            self.highlightLineCB.setChecked(
                self.iniManager.readBoolean('Editor', 'highlightcurrentline'))

            self.autoIndentCB = QtGui.QCheckBox('Automatic indentation', self)
            self.autoIndentCB.setChecked(
                self.iniManager.readBoolean('Editor', 'autoindent'))

            self.tabLabel = QtGui.QLabel('Tab size', self)
            self.tabSpinBox = QtGui.QSpinBox(self)
            self.tabSpinBox.setMinimum(1)
            self.tabSpinBox.setMaximum(12)
            self.tabSpinBox.setValue(self.iniManager.readInt('Editor',
                                                             'tabSize'))

            self.fontButton = QtGui.QPushButton('Change font settings', self)
            self.fontButton.setStyleSheet(
                'text-align:left;' 'text-decoration:underline;')
            self.fontButton.setFlat(True)

        def createLayout(self):
            self.editorBoolOptions = {'showlinenumbers': self.lineNumbersCB,
                                      'highlightcurrentline':
                                          self.highlightLineCB,
                                      'autoindent': self.autoIndentCB}

            grid = QtGui.QGridLayout()
            grid.addWidget(self.lineNumbersCB, 0, 0)
            grid.addWidget(self.highlightLineCB, 1, 0)
            grid.addWidget(self.autoIndentCB, 2, 0)
            grid.addWidget(self.tabLabel, 3, 0)
            grid.addWidget(self.tabSpinBox, 3, 1)
            grid.addWidget(self.fontButton, 4, 0)
            self.setLayout(grid)

        def createConnects(self):
            self.fontButton.clicked.connect(self.showFontDialog)

    class CompilerOptions(OptionCategories):

        def __init__(self):
            OptionCategories.__init__(self)

            self.createComponents()
            self.createLayout()
            self.createConnects()

        @QtCore.Slot()
        def onSearchCompilerButtonClicked(self):
            location = QtGui.QDesktopServices.storageLocation(
                QtGui.QDesktopServices.HomeLocation)

            folder = QtGui.QFileDialog.getExistingDirectory(
                self, 'Folder for Rasch Compiler',
                location)

            filePattern = re.compile('rasch\.*\w{0,3}$')
            for file in os.listdir(folder):
                if re.match(filePattern, file):
                    self.compilerPath.setText(folder + os.sep + file)
                    self.errorLabel.hide()
                    break
                else:
                    self.errorLabel.show()

        def createComponents(self):

            self.compilerPath = QtGui.QLineEdit(self)
            self.compilerPath.setText(
                self.iniManager.readString('Compiler', 'path'))

            self.searchCompilerButton = QtGui.QPushButton('Search...', self)
            self.compilerFlags = QtGui.QPlainTextEdit(self)
            self.compilerFlags.insertPlainText(
                self.iniManager.readString('Compiler', 'flags'))

            self.errorLabel = QtGui.QLabel(self)
            self.errorLabel.setTextFormat(QtCore.Qt.RichText)
            self.errorLabel.setText(
                '<img src= ":icons/error.png" HEIGHT="16" WIDTH= "16">' +
                ' No rasch compiler found')

            if self.compilerPath.text() != '':
                self.errorLabel.hide()

        def createLayout(self):
            grid = QtGui.QGridLayout()
            grid.addWidget(self.errorLabel, 0, 0)
            grid.addWidget(self.compilerPath, 1, 0)
            grid.addWidget(self.searchCompilerButton, 1, 1)
            grid.addWidget(self.compilerFlags, 2, 0)

            self.setLayout(grid)

        def createConnects(self):
            self.searchCompilerButton.clicked.connect(
                self.onSearchCompilerButtonClicked)
