#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\gui\newfolderdialog.py
from PySide import QtGui
from PySide import QtCore
import studioqt
__all__ = ['NewFolderDialog']

class NewFolderDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        studioqt.loadUi(self)
        self.setWindowTitle('Create Folder')
        self._text = ''
        self.connect(self.ui.cancelButton, QtCore.SIGNAL('clicked()'), self.close)
        self.connect(self.ui.createButton, QtCore.SIGNAL('clicked()'), self.create)

    def text(self):
        return self._text

    def create(self):
        text = str(self.ui.lineEdit.text()).strip()
        if text:
            self._text = text
            self.close()
