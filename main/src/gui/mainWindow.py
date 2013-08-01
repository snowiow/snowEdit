#-*- coding: utf-8 -*-

import os
from ..resources.rc_snowedit import *
from PySide import QtGui, QtCore

from seTabWidget import SeTabWidget
from codeEdit import CodeEdit
from options import Options


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
    def on_newFile_clicked(self):
        self.codeEdits.append(CodeEdit(self.tabWidget))
        self.tabWidget.addTab(self.codeEdits[self.tabWidget.count()], 'new file')

    @QtCore.Slot()
    def on_open_clicked(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, 'Open files...',
                                                   QtGui.QDesktopServices.storageLocation(
                                                       QtGui.QDesktopServices.HomeLocation),
                                                   'Rush Files (*.rs)')
        for file in files[0]:
            self.codeEdits.append(CodeEdit(self.tabWidget, file))
            self.tabWidget.addTab(self.codeEdits[self.tabWidget.count()],
                                  self.codeEdits[self.tabWidget.count()].fileName)

    @QtCore.Slot()
    def on_save_clicked(self):
        if self.codeEdits[self.tabWidget.currentIndex()].fileName == 'new file':
            self.on_saveAs_clicked()
        else:
            try:
                currentEditor = self.codeEdits[self.tabWidget.currentIndex()]
                f = open(currentEditor.filePath, 'w')
                f.write(currentEditor.toPlainText())
                f.close
                currentIndex  = self.tabWidget.currentIndex()
                if self.tabWidget.tabText(currentIndex).endswith('*'):
                    self.tabWidget.setTabText(currentIndex, self.tabWidget.tabText(currentIndex).rsplit('*', 1)[0])
            except IOError as e:
                QtGui.QMessageBox.critical(self, 'Error', 'Error, while saving file', QtGui.QMessageBox.Ok)

    @QtCore.Slot()
    def on_saveAs_clicked(self):
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
    def on_saveAll_clicked(self):
        for i in range(len(self.codeEdits)):
            self.on_save_clicked(i)

    @QtCore.Slot()
    def on_options_clicked(self):
        self.options = Options(self.codeEdits)
        self.options.show()

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

    #Misc slots

    @QtCore.Slot()
    def deleteFromCodeEdits(self, int):
        del self.codeEdits[int]

    def createComponents(self):
        pass

    def createMenu(self):

        #FileMenu Actions
        self.newFileAction = QtGui.QAction(QtGui.QIcon(':icons/newfile.png'), 'New File', self)
        self.newFileAction.setShortcut('Ctrl+Alt+N')

        self.openFileAction = QtGui.QAction(QtGui.QIcon(':icons/open.png'), 'Open Files', self)
        self.openFileAction.setShortcut('Ctrl+Alt+O')

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

        #Creating file Toolbar
        fileToolBar = self.addToolBar('File')
        fileToolBar.setIconSize(QtCore.QSize(16, 16))
        fileToolBar.addAction(self.newFileAction)
        fileToolBar.addAction(self.openFileAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addAction(self.saveAllAction)

        #Creating Edit Toolbar
        editToolBar = self.addToolBar('Edit')
        editToolBar.setIconSize(QtCore.QSize(16, 16))
        editToolBar.addAction(self.undoAction)
        editToolBar.addAction(self.redoAction)
        editToolBar.addAction(self.cutAction)

        menuBar = self.menuBar()

        #Creating ile menu
        fileMenu = menuBar.addMenu('File')
        fileMenu.addAction(self.newFileAction)
        fileMenu.addAction(self.openFileAction)
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
        editMenu.addAction(self.cutAction)

    def createConnects(self):
        #FileMenu Actions
        self.newFileAction.triggered.connect(self.on_newFile_clicked)
        self.openFileAction.triggered.connect(self.on_open_clicked)
        self.saveAction.triggered.connect(self.on_save_clicked)
        self.saveAsAction.triggered.connect(self.on_saveAs_clicked)
        self.saveAllAction.triggered.connect(self.on_saveAll_clicked)
        self.optionsAction.triggered.connect(self.on_options_clicked)
        self.exitAction.triggered.connect(self.close)

        #EditMenu Actions
        self.undoAction.triggered.connect(self.undo)
        self.redoAction.triggered.connect(self.redo)
        self.cutAction.triggered.connect(self.cut)

        #Tab driven events
        QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL('tabCloseRequested(int)'),
                               self.tabWidget, QtCore.SLOT('deleteTab(int)'))

        QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL('tabCloseRequested(int)'),
                               self, QtCore.SLOT('deleteFromCodeEdits(int)'))

    def createLayout(self):
        layout = QtGui.QGridLayout()

        self.tabWidget = SeTabWidget()
        self.tabWidget.setTabsClosable(True)
        # self.tabWidget.setMovable(True)
        self.codeEdits.append(CodeEdit(self.tabWidget))
        self.tabWidget.addTab(self.codeEdits[self.tabWidget.count()], 'new file')

        layout.addWidget(self.tabWidget)

        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)