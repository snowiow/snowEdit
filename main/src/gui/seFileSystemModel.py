#-*- coding: utf-8 -*-

from PySide import QtGui
from ..resources.rc_snowedit import *

import re


class SeFileSystemModel(QtGui.QFileSystemModel):
    def __init__(self):
        QtGui.QFileSystemModel.__init__(self)
        self.fileEndPattern = re.compile("^.*\.(\w{2,4})$")

    def data(self, index, role):
        if index.column() == 0 and role == QtCore.Qt.DecorationRole:
            if self.fileEndPattern.match(index.data()) is not None:
                if index.data().endswith('rs'):
                    return QtGui.QIcon(':icons/rs-file.png')
                return QtGui.QIcon(':icons/newfile.png')

            return QtGui.QIcon(':icons/openFolder.png')

        return super(SeFileSystemModel, self).data(index, role)
