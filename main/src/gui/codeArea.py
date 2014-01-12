from PySide import QtGui
from codeEdit import CodeEdit
from seFind import SeFind


class CodeArea(QtGui.QWidget):

    def __init__(self, filePath = None):
        QtGui.QWidget.__init__(self)

        self.createComponents(filePath)
        self.createLayout()
        self.createConnects()
        self.show()

    def createComponents(self, filePath):
        self.codeEdit = CodeEdit(filePath)
        self.seFind = SeFind(self.codeEdit)

    def createLayout(self):
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.codeEdit)
        layout.addWidget(self.seFind)
        self.setLayout(layout)

    def createConnects(self):
        pass

