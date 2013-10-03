#-*- coding: utf-8 -*-

import os
import subprocess

from PySide import QtGui, QtCore

from seTabWidget import SeTabWidget
from highlighter.noneHighlighter import NoneHighlighter
from highlighter.pythonHighlighter import PythonHighlighter
from highlighter.raschHighlighter import RaschHighlighter
from highlighter.cppHighlighter import CppHighlighter
from seConsole import SeConsole
from codeEdit import CodeEdit
from options import Options
from about import About
from seTreeView import SeTreeView
from ..util.helperFunctions import *
from ..util.iniManager import IniManager


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.codeEdits = []
        self.iniManager = IniManager.getInstance()
        self.createComponents()
        self.createMenu()
        self.createLayout()
        self.createConnects()

        self.setWindowTitle('snowEdit')
        self.setWindowIcon(QtGui.QIcon(':icons/snow_logo.png'))
        self.move(100, 100)
        self.show()

    # Slots for file operations

    @QtCore.Slot()
    def onNewFileClicked(self):
        self.codeEdits.append(CodeEdit(self.tabWidget))
        self.tabWidget.addTab(
            self.codeEdits[self.tabWidget.count()], 'new file')

    @QtCore.Slot()
    def onOpenFilesClicked(self):
        location = QtGui.QDesktopServices.storageLocation(
            QtGui.QDesktopServices.HomeLocation)
        files = QtGui.QFileDialog.getOpenFileNames(self, 'Open Files...',
                                                   location)

        for file in files[0]:
            self.checkIfFileOpen(file)

    @QtCore.Slot()
    def onOpenFolderClicked(self):
        location = QtGui.QDesktopServices.storageLocation(
            QtGui.QDesktopServices.HomeLocation)
        folder = QtGui.QFileDialog.getExistingDirectory(self, 'Open Folder...',
                                                        location)
        if folder != '':
            path = self.folderView.model.setRootPath(folder)
            self.folderView.setRootIndex(path)
            self.folderView.folderOpened = True

    @QtCore.Slot()
    def onSaveClicked(self):
        currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
        if getFileName(currentEditor.filePath) == 'new file':
            self.onSaveAsClicked()
        else:
            try:
                f = open(currentEditor.filePath, 'w')
                f.write(currentEditor.toPlainText())
                f.close
                currentIndex = self.tabWidget.currentIndex()
                if self.tabWidget.tabText(currentIndex).endswith('*'):
                    tabName = self.tabWidget.tabText(
                        currentIndex).rsplit('*', 1)[0]
                    self.tabWidget.setTabText(currentIndex, tabName)
            except IOError:
                QtGui.QMessageBox.critical(self, 'Error',
                                           'Error, while saving file',
                                           QtGui.QMessageBox.Ok)

    @QtCore.Slot()
    def onSaveAsClicked(self):
        location = QtGui.QDesktopServices.storageLocation(
            QtGui.QDesktopServices.HomeLocation)
        saveLocation = QtGui.QFileDialog.getSaveFileName(self, 'Save file...',
                                                         location,
                                                         'Rush Files (*.rs)')
        if saveLocation[0] != '':
            try:
                currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
                f = open(saveLocation[0], 'w')
                f.write(currentEditor.toPlainText())
                f.close()
                currentEditor.filePath = saveLocation[0]
                self.tabWidget.setTabText(
                    self.tabWidget.currentIndex(),
                    getFileName(currentEditor.filePath))
            except IOError:
                QtGui.QMessageBox.critical(
                    self, 'Error', 'Error, while saving file',
                    QtGui.QMessageBox.Ok)

    @QtCore.Slot()
    def onSaveAllClicked(self):
        for i in range(len(self.codeEdits)):
            self.onSaveClicked(i)

    @QtCore.Slot()
    def onOptionsClicked(self):
        self.options = Options(self.codeEdits)

    # Slots for editing

    @QtCore.Slot()
    def undo(self):
        self.codeEdits[self.tabWidget.currentIndex()].undo()

    @QtCore.Slot()
    def redo(self):
        self.codeEdits[self.tabWidget.currentIndex()].redo()

    @QtCore.Slot()
    def cut(self):
        self.codeEdits[self.tabWidget.currentIndex()].cut()

    @QtCore.Slot()
    def copy(self):
        self.codeEdits[self.tabWidget.currentIndex()].copy()

    @QtCore.Slot()
    def paste(self):
        self.codeEdits[self.tabWidget.currentIndex()].paste()

    @QtCore.Slot()
    def duplicateLine(self):
        currentEditor = self.codeEdits[self.tabWidget.currentIndex()]

        selection = QtGui.QTextEdit.ExtraSelection()
        selection.cursor = currentEditor.textCursor()
        selection.cursor.clearSelection()
        selection.cursor.select(QtGui.QTextCursor.LineUnderCursor)

        content = selection.cursor.selectedText()
        selection.cursor.clearSelection()
        currentEditor.insertPlainText("\n" + content)

    @QtCore.Slot()
    def commentLine(self):
        currentEditor = self.codeEdits[self.tabWidget.currentIndex()]

        selection = QtGui.QTextEdit.ExtraSelection()

        currentPosition = currentEditor.textCursor()
        selection.cursor = currentEditor.textCursor()

        if selection.cursor.selectedText() == '':
            selection.cursor.select(QtGui.QTextCursor.LineUnderCursor)
            lineText = selection.cursor.selectedText()
            selection.cursor.clearSelection()

            selection.cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            currentEditor.setTextCursor(selection.cursor)

            if lineText.startswith('//'):
                selection.cursor.deleteChar()
                selection.cursor.deleteChar()
            else:
                currentEditor.insertPlainText('//')

        else:
            selectionList = selection.cursor.selection(
            ).toPlainText().split('\n')
            selection.cursor.clearSelection()

            for line in selectionList:
                selection.cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                currentEditor.setTextCursor(selection.cursor)

                if line.startswith('//'):
                    selection.cursor.deleteChar()
                    selection.cursor.deleteChar()
                else:
                    currentEditor.insertPlainText('//')

                selection.cursor.movePosition(QtGui.QTextCursor.Down)

        currentEditor.setTextCursor(currentPosition)

    # Slots for run
    @QtCore.Slot()
    def onRunClicked(self):
        compilerPath = self.iniManager.readString('Compiler', 'path')
        output = subprocess.Popen(compilerPath, stdout=subprocess.PIPE)
        out, err = output.communicate()
        if output.returncode == 0:
            self.seConsole.writeToConsole(out)
            self.checkIfFileOpen(
                compilerPath.rsplit(os.sep, 1)[0] + os.sep + 'output.cpp')
        elif output.returncode > 0:
            self.seConsole.writeToConsole(out, error=True)
            self.codeEdits[self.tabWidget.currentIndex()].generateError(out)


    @QtCore.Slot()
    def onCompilerOptionsClicked(self):
        self.options = Options(self.codeEdits)
        self.options.showStackInt(1)

    # Slots for help menu
    @QtCore.Slot()
    def onAboutClicked(self):
        self.about = About()

    # Slots for folderView
    @QtCore.Slot(QtCore.QModelIndex)
    def openFile(self, index):
        if self.folderView.model.fileInfo(index).isFile():
            fileName = self.folderView.model.filePath(index)
            self.checkIfFileOpen(fileName)

    @QtCore.Slot(QtCore.QModelIndex)
    def rename(self, index):
        if index.isValid():
            input, ok = QtGui.QInputDialog.getText(
                self, 'rename', 'New filename:')

            if ok:
                if self.folderView.model.fileInfo(index).isFile():
                    if not input.endswith('.rs'):
                        input += ".rs"

                oldName = self.folderView.model.filePath(index)
                newName = getPathOnly(oldName) + input
                try:
                    os.rename(oldName, newName)
                except OSError:
                    QtGui.QMessageBox.critical(
                        self, 'Error', 'Error, while renaming file',
                        QtGui.QMessageBox.Ok)

                for i in range(len(self.codeEdits)):
                    if self.codeEdits[i].filePath == oldName:
                        self.codeEdits[i].filePath = newName
                        self.tabWidget.setTabText(i, getFileName(newName))

    @QtCore.Slot(QtCore.QModelIndex)
    def delete(self, index):
        ret = self.createDeleteDialog()
        if ret == QtGui.QMessageBox.Yes:
            self.folderView.model.remove(index)

    @QtCore.Slot(QtCore.QModelIndex)
    def addFile(self, index):
        input, ok = QtGui.QInputDialog.getText(
            self, 'Filename', 'Type in filename:')
        if ok:
            if not input.endswith('.rs'):
                input += '.rs'
            if self.folderView.rootFolderClicked:
                file = open(
                    self.folderView.model.rootPath() + '/' + input, 'w')
                file.close()
            else:
                file = open(
                    self.folderView.model.filePath(index) + '/' + input, 'w')
                file.close()

    @QtCore.Slot(QtCore.QModelIndex)
    def addFolder(self, index):
        input, ok = QtGui.QInputDialog.getText(
            self, 'Foldername', 'Type in foldername:')
        if ok:
            if self.folderView.rootFolderClicked:
                os.mkdir(self.folderView.model.rootPath() + '/' + input)
            else:
                os.mkdir(self.folderView.model.filePath(index) + '/' + input)

    # Highlighting Slots

    @QtCore.Slot()
    def python(self):
        currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
        currentEditor.highlighter = PythonHighlighter(currentEditor.document())

    @QtCore.Slot()
    def none(self):
        currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
        currentEditor.highlighter = NoneHighlighter(currentEditor.document())

    @QtCore.Slot()
    def rasch(self):
        currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
        currentEditor.highlighter = RaschHighlighter(currentEditor.document())

    @QtCore.Slot()
    def cpp(self):
        currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
        currentEditor.highlighter = CppHighlighter(currentEditor.document())

    # Misc slots
    @QtCore.Slot()
    def deleteFromCodeEdits(self, int):
        del self.codeEdits[int]

    def createDeleteDialog(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Delete')
        msgBox.setIconPixmap(':icons/delete.png')
        msgBox.setWindowIcon(QtGui.QIcon(':icons/delete.png'))
        msgBox.setText('Sure you want to delete the file or' +
                       'folder with all it\'s contents?')
        msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msgBox.setDefaultButton(QtGui.QMessageBox.No)
        ret = msgBox.exec_()
        return ret

    def createComponents(self):
        self.folderView = SeTreeView()
        self.tabWidget = SeTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.seConsole = SeConsole()

    def createMenu(self):

        # FileMenu Actions
        self.newFileAction = QtGui.QAction(
            QtGui.QIcon(':icons/newfile.png'), 'New File', self)
        self.newFileAction.setShortcut('Ctrl+Alt+N')

        self.openFileAction = QtGui.QAction(
            QtGui.QIcon(':icons/open.png'), 'Open Files', self)
        self.openFileAction.setShortcut('Ctrl+O')

        self.openFolderAction = QtGui.QAction(
            QtGui.QIcon(':icons/openFolder.png'), 'Open Folder', self)
        self.openFolderAction.setShortcut('Ctrl+Alt+O')

        self.saveAction = QtGui.QAction(
            QtGui.QIcon(':icons/save.png'), 'Save', self)
        self.saveAction.setShortcut('Ctrl+S')

        self.saveAsAction = QtGui.QAction('&Save as...', self)

        self.saveAllAction = QtGui.QAction(
            QtGui.QIcon(':icons/saveall.png'), 'Save All', self)
        self.saveAllAction.setShortcut('Ctrl+Alt+S')

        self.optionsAction = QtGui.QAction(
            QtGui.QIcon(':icons/options.png'), 'Options', self)
        self.optionsAction.setShortcut('Ctrl+Alt+O')

        self.exitAction = QtGui.QAction(
            QtGui.QIcon(':icons/quit.png'), 'Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')

        # EditMenu Actions
        self.undoAction = QtGui.QAction(
            QtGui.QIcon(':icons/undo.png'), 'Undo', self)
        self.undoAction.setShortcut(QtGui.QKeySequence.Undo)

        self.redoAction = QtGui.QAction(
            QtGui.QIcon(':icons/redo.png'), 'Redo', self)
        self.redoAction.setShortcut(QtGui.QKeySequence.Redo)

        self.cutAction = QtGui.QAction(
            QtGui.QIcon(':icons/cut.png'), 'Cut', self)
        self.cutAction.setShortcut(QtGui.QKeySequence.Cut)

        self.copyAction = QtGui.QAction(
            QtGui.QIcon(':icons/copy.png'), 'Copy', self)
        self.copyAction.setShortcut(QtGui.QKeySequence.Copy)

        self.pasteAction = QtGui.QAction(
            QtGui.QIcon(':icons/paste.png'), 'Paste', self)
        self.pasteAction.setShortcut(QtGui.QKeySequence.Paste)

        self.duplicateLineAction = QtGui.QAction(
            QtGui.QIcon(':icons/duplicate-line.png'), 'Duplicate current line',
            self)
        self.duplicateLineAction.setShortcut('Ctrl+D')

        self.commentLineAction = QtGui.QAction(
            QtGui.QIcon(':icons/comment.png'),
            '(De-)comment current line', self)
        self.commentLineAction.setShortcut('Ctrl+7')

        # Highlightingactions
        highlightActionGroup = QtGui.QActionGroup(self)
        highlightActionGroup.setExclusive(True)

        self.noneAction = QtGui.QAction('None', highlightActionGroup)
        self.noneAction.setCheckable(True)
        self.noneAction.setChecked(True)

        self.pythonAction = QtGui.QAction('Python', highlightActionGroup)
        self.pythonAction.setCheckable(True)

        self.raschAction = QtGui.QAction('Rasch', highlightActionGroup)
        self.raschAction.setCheckable(True)

        self.cppAction = QtGui.QAction('C++', highlightActionGroup)
        self.cppAction.setCheckable(True)

        # run actions
        self.runAction = QtGui.QAction(
            QtGui.QIcon(':icons/run.png'), 'Run', self)
        self.runAction.setShortcut('F5')
        self.compilerOptionsAction = QtGui.QAction('Configure Compiler', self)

        # Help Actions
        self.aboutAction = QtGui.QAction('About', self)

        # Creating file Toolbar
        fileToolBar = self.addToolBar('File')
        fileToolBar.setIconSize(QtCore.QSize(16, 16))
        fileToolBar.addAction(self.newFileAction)
        fileToolBar.addAction(self.openFileAction)
        fileToolBar.addAction(self.openFolderAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addAction(self.saveAllAction)

        # Creating Edit Toolbar
        editToolBar = self.addToolBar('Edit')
        editToolBar.setIconSize(QtCore.QSize(16, 16))
        editToolBar.addAction(self.undoAction)
        editToolBar.addAction(self.redoAction)
        editToolBar.addAction(self.cutAction)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)
        editToolBar.addAction(self.duplicateLineAction)
        editToolBar.addAction(self.commentLineAction)

        # Creating Run Toolbar
        runToolBar = self.addToolBar('Run')
        runToolBar.setIconSize(QtCore.QSize(16, 16))
        runToolBar.addAction(self.runAction)

        menuBar = self.menuBar()

        # Creating file menu
        fileMenu = menuBar.addMenu('File')
        fileMenu.addAction(self.newFileAction)
        fileMenu.addAction(self.openFileAction)
        fileMenu.addAction(self.openFolderAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.saveAllAction)
        fileMenu.addAction(self.optionsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        # creating edit menu
        editMenu = menuBar.addMenu('Edit')
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addSeparator()
        editMenu.addAction(self.duplicateLineAction)
        editMenu.addAction(self.commentLineAction)

        # Creating highlight menu
        highlightMenu = menuBar.addMenu('Highlighting')
        highlightMenu.addAction(self.noneAction)
        highlightMenu.addAction(self.cppAction)
        highlightMenu.addAction(self.pythonAction)
        highlightMenu.addAction(self.raschAction)

        # Creating run menu
        runMenu = menuBar.addMenu('Run')
        runMenu.addAction(self.runAction)
        runMenu.addAction(self.compilerOptionsAction)

        # creating help menu
        helpMenu = menuBar.addMenu('Help')
        helpMenu.addAction(self.aboutAction)

    def createConnects(self):
        # FileMenu Actions
        self.newFileAction.triggered.connect(self.onNewFileClicked)
        self.openFileAction.triggered.connect(self.onOpenFilesClicked)
        self.openFolderAction.triggered.connect(self.onOpenFolderClicked)
        self.saveAction.triggered.connect(self.onSaveClicked)
        self.saveAsAction.triggered.connect(self.onSaveAsClicked)
        self.saveAllAction.triggered.connect(self.onSaveAllClicked)
        self.optionsAction.triggered.connect(self.onOptionsClicked)
        self.exitAction.triggered.connect(self.close)

        # EditMenu Actions
        self.undoAction.triggered.connect(self.undo)
        self.redoAction.triggered.connect(self.redo)
        self.cutAction.triggered.connect(self.cut)
        self.copyAction.triggered.connect(self.copy)
        self.pasteAction.triggered.connect(self.paste)
        self.duplicateLineAction.triggered.connect(self.duplicateLine)
        self.commentLineAction.triggered.connect(self.commentLine)

        # HighlightingEvents
        self.pythonAction.triggered.connect(self.python)
        self.noneAction.triggered.connect(self.none)
        self.raschAction.triggered.connect(self.rasch)
        self.cppAction.triggered.connect(self.cpp)

        # Run menu actions
        self.runAction.triggered.connect(self.onRunClicked)
        self.compilerOptionsAction.triggered.connect(
            self.onCompilerOptionsClicked)

        # HelpMenu Actions
        self.aboutAction.triggered.connect(self.onAboutClicked)

        # Tab driven events
        QtCore.QObject.connect(
            self.tabWidget, QtCore.SIGNAL('tabCloseRequested(int)'),
            self.tabWidget, QtCore.SLOT('deleteTab(int)'))

        QtCore.QObject.connect(
            self.tabWidget, QtCore.SIGNAL('tabCloseRequested(int)'),
            self, QtCore.SLOT('deleteFromCodeEdits(int)'))

        self.connect(
            self.folderView, QtCore.SIGNAL(
                'doubleClicked(const QModelIndex&)'),
            self, QtCore.SLOT('openFile(const QModelIndex&)'))

        # Folder View Events

        self.folderView.openFileAction.triggered.connect(
            lambda: self.openFile(self.folderView.currentIndex()))
        self.folderView.renameAction.triggered.connect(
            lambda: self.rename(self.folderView.currentIndex()))
        self.folderView.deleteAction.triggered.connect(
            lambda: self.delete(self.folderView.currentIndex()))
        self.folderView.addFileAction.triggered.connect(
            lambda: self.addFile(self.folderView.currentIndex()))
        self.folderView.addFolderAction.triggered.connect(
            lambda: self.addFolder(self.folderView.currentIndex()))

    def createLayout(self):
        hlayout = QtGui.QHBoxLayout()
        vlayout = QtGui.QVBoxLayout()

        # self.tabWidget.setMovable(True)
        self.codeEdits.append(CodeEdit(self.tabWidget))
        self.tabWidget.addTab(
            self.codeEdits[self.tabWidget.count()], 'new file')

        vlayout.addWidget(self.tabWidget, 3)
        vlayout.addWidget(self.seConsole, 1)

        hlayout.addWidget(self.folderView, 1)
        hlayout.addLayout(vlayout, 5)

        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(hlayout)
        self.setCentralWidget(centralWidget)

    def setHighlighterMenu(self, editor):
        if editor.filePath.endswith('py'):
            self.pythonAction.setChecked(True)
        elif editor.filePath.endswith('rs'):
            self.raschAction.setChecked(True)
        elif editor.filePath.endswith('cpp') or editor.filePath.endswith('h'):
            self.cppAction.setChecked(True)
        else:
            self.noneAction.setChecked(True)

    def checkIfFileOpen(self, file):
        alreadyOpen = False
        for i in range(len(self.codeEdits)):
            if normalizeSeps(file) == self.codeEdits[i].filePath:
                self.tabWidget.setCurrentIndex(i)
                alreadyOpen = True
                return
        if not alreadyOpen:
            self.codeEdits.append(CodeEdit(self.tabWidget, file))
            currentEditor = self.codeEdits[self.tabWidget.count()]
            self.tabWidget.addTab(currentEditor,
                                  getFileName(currentEditor.filePath))

            self.tabWidget.setCurrentIndex(len(self.codeEdits) - 1)
            self.setHighlighterMenu(
                self.codeEdits[self.tabWidget.count() - 1])

            currentEditor.updateCompleter()
