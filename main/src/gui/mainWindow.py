#-*- coding: utf-8 -*-

from PySide import QtGui, QtCore

from seTabWidget import SeTabWidget
from codeEdit import CodeEdit
from options import Options
from about import About
from seFileSystemModel import SeFileSystemModel


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.codeEdits = []

        self.createMenu()
        self.createComponents()
        self.createLayout()
        self.createConnects()

        self.setWindowTitle('snowEdit')
        self.setWindowIcon(QtGui.QIcon(':icons/snow_logo.png'))
        self.move(100, 100)

        self.show()

    #Slots for file operations

    @QtCore.Slot()
    def onNewFileClicked(self):
        self.codeEdits.append(CodeEdit(self.tabWidget))
        self.tabWidget.addTab(self.codeEdits[self.tabWidget.count()], 'new file')

    @QtCore.Slot()
    def onOpenFilesClicked(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, 'Open Files...',
                                                   QtGui.QDesktopServices.storageLocation(
                                                       QtGui.QDesktopServices.HomeLocation))

        for file in files[0]:
            self.codeEdits.append(CodeEdit(self.tabWidget, file))
            self.tabWidget.addTab(self.codeEdits[self.tabWidget.count()],
                                  self.codeEdits[self.tabWidget.count()].fileName)

    @QtCore.Slot()
    def openFile(self, index):
        if index.isValid():
            if self.model.fileInfo(index).isFile():
                self.codeEdits.append(CodeEdit(self.tabWidget, self.model.filePath(index)))
                self.tabWidget.addTab(self.codeEdits[self.tabWidget.count()],
                                      self.codeEdits[self.tabWidget.count()].fileName)

    @QtCore.Slot()
    def onOpenFolderClicked(self):
        folder = QtGui.QFileDialog.getExistingDirectory(self, 'Open Folder...',
                                                        QtGui.QDesktopServices.storageLocation(
                                                            QtGui.QDesktopServices.HomeLocation))
        path = self.model.setRootPath(folder)
        self.folderView.setRootIndex(path)


    @QtCore.Slot()
    def onSaveClicked(self):
        if self.codeEdits[self.tabWidget.currentIndex()].fileName == 'new file':
            self.onSaveAsClicked()
        else:
            try:
                currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
                f = open(currentEditor.filePath, 'w')
                f.write(currentEditor.toPlainText())
                f.close
                currentIndex = self.tabWidget.currentIndex()
                if self.tabWidget.tabText(currentIndex).endswith('*'):
                    self.tabWidget.setTabText(currentIndex, self.tabWidget.tabText(currentIndex).rsplit('*', 1)[0])
            except IOError as e:
                QtGui.QMessageBox.critical(self, 'Error', 'Error, while saving file', QtGui.QMessageBox.Ok)

    @QtCore.Slot()
    def onSaveAsClicked(self):
        saveLocation = QtGui.QFileDialog.getSaveFileName(self, 'Save file...',
                                                         QtGui.QDesktopServices.storageLocation(
                                                             QtGui.QDesktopServices.HomeLocation),
                                                         'Rush Files (*.rs)')
        if saveLocation[0] != '':
            try:
                currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
                f = open(saveLocation[0], 'w')
                f.write(currentEditor.toPlainText())
                f.close()
                currentEditor.filePath = saveLocation[0]
                self.tabWidget.setTabText(self.tabWidget.currentIndex(), currentEditor.fileName)
            except IOError as e:
                QtGui.QMessageBox.critical(self, 'Error', 'Error, while saving file', QtGui.QMessageBox.Ok)

    @QtCore.Slot()
    def onSaveAllClicked(self):
        for i in range(len(self.codeEdits)):
            self.onSaveClicked(i)

    @QtCore.Slot()
    def onOptionsClicked(self):
        self.options = Options(self.codeEdits)

    #Slot for editing

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
            selectionList = selection.cursor.selection().toPlainText().split('\n')
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

    #Slots for help menu
    @QtCore.Slot()
    def onAboutClicked(self):
        self.about = About()

    #Misc slots

    @QtCore.Slot()
    def deleteFromCodeEdits(self, int):
        del self.codeEdits[int]

    def createComponents(self):
        self.folderView = QtGui.QTreeView()
        self.model = SeFileSystemModel()
        self.folderView.setModel(self.model)

        self.folderView.setHeaderHidden(True)

        for i in range(1, 4):
            self.folderView.hideColumn(i)

    def createMenu(self):

        #FileMenu Actions
        self.newFileAction = QtGui.QAction(QtGui.QIcon(':icons/newfile.png'), 'New File', self)
        self.newFileAction.setShortcut('Ctrl+Alt+N')

        self.openFileAction = QtGui.QAction(QtGui.QIcon(':icons/open.png'), 'Open Files', self)
        self.openFileAction.setShortcut('Ctrl+O')

        self.openFolderAction = QtGui.QAction(QtGui.QIcon(':icons/openFolder.png'), 'Open Folder', self)
        self.openFolderAction.setShortcut('Ctrl+Alt+O')

        self.saveAction = QtGui.QAction(QtGui.QIcon(':icons/save.png'), 'Save', self)
        self.saveAction.setShortcut('Ctrl+S')

        self.saveAsAction = QtGui.QAction('&Save as...', self)

        self.saveAllAction = QtGui.QAction(QtGui.QIcon(':icons/saveall.png'), 'Save All', self)
        self.saveAllAction.setShortcut('Ctrl+Alt+S')

        self.optionsAction = QtGui.QAction(QtGui.QIcon(':icons/options.png'), 'Options', self)
        self.optionsAction.setShortcut('Ctrl+Alt+O')

        self.exitAction = QtGui.QAction(QtGui.QIcon(':icons/quit.png'), 'Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')

        #EditMenu Actions
        self.undoAction = QtGui.QAction(QtGui.QIcon(':icons/undo.png'), 'Undo', self)
        self.undoAction.setShortcut(QtGui.QKeySequence.Undo)

        self.redoAction = QtGui.QAction(QtGui.QIcon(':icons/redo.png'), 'Redo', self)
        self.redoAction.setShortcut(QtGui.QKeySequence.Redo)

        self.cutAction = QtGui.QAction(QtGui.QIcon(':icons/cut.png'), 'Cut', self)
        self.cutAction.setShortcut(QtGui.QKeySequence.Cut)

        self.copyAction = QtGui.QAction(QtGui.QIcon(':icons/copy.png'), 'Copy', self)
        self.copyAction.setShortcut(QtGui.QKeySequence.Copy)

        self.pasteAction = QtGui.QAction(QtGui.QIcon(':icons/paste.png'), 'Paste', self)
        self.pasteAction.setShortcut(QtGui.QKeySequence.Paste)

        self.duplicateLineAction = QtGui.QAction(QtGui.QIcon(':icons/duplicate-line.png'), 'Duplicate current line',
                                                 self)
        self.duplicateLineAction.setShortcut('Ctrl+D')

        self.commentLineAction = QtGui.QAction(QtGui.QIcon(':icons/comment.png'), '(De-)comment current line', self)
        self.commentLineAction.setShortcut('Ctrl+7')

        #Help Actions
        self.aboutAction = QtGui.QAction('About', self)

        #Creating file Toolbar
        fileToolBar = self.addToolBar('File')
        fileToolBar.setIconSize(QtCore.QSize(16, 16))
        fileToolBar.addAction(self.newFileAction)
        fileToolBar.addAction(self.openFileAction)
        fileToolBar.addAction(self.openFolderAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addAction(self.saveAllAction)

        #Creating Edit Toolbar
        editToolBar = self.addToolBar('Edit')
        editToolBar.setIconSize(QtCore.QSize(16, 16))
        editToolBar.addAction(self.undoAction)
        editToolBar.addAction(self.redoAction)
        editToolBar.addAction(self.cutAction)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)
        editToolBar.addAction(self.duplicateLineAction)
        editToolBar.addAction(self.commentLineAction)

        menuBar = self.menuBar()

        #Creating file menu
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

        #creating edit menu
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

        #creating help menu
        helpMenu = menuBar.addMenu('Help')
        helpMenu.addAction(self.aboutAction)

    def createConnects(self):
        #FileMenu Actions
        self.newFileAction.triggered.connect(self.onNewFileClicked)
        self.openFileAction.triggered.connect(self.onOpenFilesClicked)
        self.openFolderAction.triggered.connect(self.onOpenFolderClicked)
        self.saveAction.triggered.connect(self.onSaveClicked)
        self.saveAsAction.triggered.connect(self.onSaveAsClicked)
        self.saveAllAction.triggered.connect(self.onSaveAllClicked)
        self.optionsAction.triggered.connect(self.onOptionsClicked)
        self.exitAction.triggered.connect(self.close)

        #EditMenu Actions
        self.undoAction.triggered.connect(self.undo)
        self.redoAction.triggered.connect(self.redo)
        self.cutAction.triggered.connect(self.cut)
        self.copyAction.triggered.connect(self.copy)
        self.pasteAction.triggered.connect(self.paste)
        self.duplicateLineAction.triggered.connect(self.duplicateLine)
        self.commentLineAction.triggered.connect(self.commentLine)

        #HelpMenu Actions
        self.aboutAction.triggered.connect(self.onAboutClicked)

        #Tab driven events
        QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL('tabCloseRequested(int)'),
                               self.tabWidget, QtCore.SLOT('deleteTab(int)'))

        QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL('tabCloseRequested(int)'),
                               self, QtCore.SLOT('deleteFromCodeEdits(int)'))

        self.connect(self.folderView, QtCore.SIGNAL('doubleClicked(const QModelIndex&)'),
                     self, QtCore.SLOT('openFile(const QModelIndex&)'))

    def createLayout(self):
        layout = QtGui.QHBoxLayout()

        self.tabWidget = SeTabWidget()
        self.tabWidget.setTabsClosable(True)
        # self.tabWidget.setMovable(True)
        self.codeEdits.append(CodeEdit(self.tabWidget))
        self.tabWidget.addTab(self.codeEdits[self.tabWidget.count()], 'new file')

        layout.addWidget(self.folderView, 1)
        layout.addWidget(self.tabWidget, 5)

        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)