from PySide import QtGui, QtCore
from seFileSystemModel import SeFileSystemModel
from ..resources.rc_snowedit import *
from ..util.helperFunctions import *


class SeTreeView(QtGui.QTreeView):
    def __init__(self):
        QtGui.QTreeView.__init__(self)
        self.folderOpened = False
        self.rootFolderClicked = False
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.createActions()
        self.createComponents()
        self.createRootContextMenu()
        self.createFolderContextMenu()
        self.createFileContextMenu()
        self.createConnects()

    @QtCore.Slot()
    def onCustomContextMenuClicked(self, pos):
        index = self.indexAt(pos)
        if self.folderOpened:
            if index.data() is not None:
                self.rootFolderClicked = False
                if fileEndPattern.match(index.data()) is not None:
                    self.fileContextMenu.exec_(self.mapToGlobal(pos))
                else:
                    self.folderContextMenu.exec_(self.mapToGlobal(pos))
            else:
                self.rootFolderClicked = True
                self.rootContextMenu.exec_(self.mapToGlobal(pos))

    def createActions(self):
        self.renameAction = QtGui.QAction(QtGui.QIcon(':icons/rename.png'),
                                          'Rename', self)
        self.addFileAction = QtGui.QAction(QtGui.QIcon(':icons/addFile.png'),
                                           'Create new file', self)
        self.addFolderAction = QtGui.QAction(QtGui.QIcon(
            ':icons/addFolder.png'),
                                             'Create new folder', self)
        self.deleteAction = QtGui.QAction(QtGui.QIcon(':icons/delete.png'),
                                          'Delete', self)
        self.openFileAction = QtGui.QAction(QtGui.QIcon(
            ':icons/newfile.png'),
                                            'Open file', self)

    def createRootContextMenu(self):
        self.rootContextMenu = QtGui.QMenu()
        self.rootContextMenu.addAction(self.addFileAction)
        self.rootContextMenu.addAction(self.addFolderAction)

    def createFolderContextMenu(self):
        self.folderContextMenu = QtGui.QMenu()
        self.folderContextMenu.addAction(self.addFileAction)
        self.folderContextMenu.addAction(self.addFolderAction)
        self.folderContextMenu.addAction(self.renameAction)
        self.folderContextMenu.addAction(self.deleteAction)

    def createFileContextMenu(self):
        self.fileContextMenu = QtGui.QMenu()
        self.fileContextMenu.addAction(self.openFileAction)
        self.fileContextMenu.addAction(self.renameAction)
        self.fileContextMenu.addAction(self.deleteAction)

    def createComponents(self):
        self.model = SeFileSystemModel()

        self.setModel(self.model)

        self.setHeaderHidden(True)

        for i in range(1, 4):
            self.hideColumn(i)

    def createConnects(self):
        self.connect(self, QtCore.SIGNAL(
            'customContextMenuRequested(const QPoint&)'),
                     self,
                     QtCore.SLOT('onCustomContextMenuClicked(const QPoint &)'))
