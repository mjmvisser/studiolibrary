#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\gui\__init__.py
from PySide import QtGui
from PySide import QtCore
import studioqt
import studiolibrary
__all__ = ['ContextMenu', 'PreviewWidget', 'CheckForUpdatesThread']

class PreviewWidget(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        studioqt.loadUi(self)

    def window(self):
        return self.parent().window()


class CheckForUpdatesThread(QtCore.QThread):

    def __init__(self, *args):
        QtCore.QThread.__init__(self, *args)

    def run(self):
        if studiolibrary.package().isUpdateAvailable():
            self.emit(QtCore.SIGNAL('updateAvailable()'))


class ContextMenu(QtGui.QMenu):

    def __init__(self, *args):
        QtGui.QMenu.__init__(self, *args)
        self._menus = []
        self._actions = []

    def actions(self):
        return self._actions

    def insertAction(self, actionBefore, action):
        if str(action.text()) not in self._actions:
            self._actions.append(str(action.text()))
            QtGui.QMenu.insertAction(self, actionBefore, action)

    def addAction(self, action):
        if str(action.text()) not in self._actions:
            self._actions.append(str(action.text()))
            QtGui.QMenu.addAction(self, action)

    def addMenu(self, menu):
        if str(menu.title()) not in self._menus:
            self._menus.append(str(menu.title()))
            QtGui.QMenu.addMenu(self, menu)
