#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/studioqt\contextmenu.py
from studioqt import QtWidgets
__all__ = ['ContextMenu']

class ContextMenu(QtWidgets.QMenu):

    def __init__(self, *args):
        QtWidgets.QMenu.__init__(self, *args)
        self._menus = []
        self._actions = []

    def actions(self):
        return self._actions

    def insertAction(self, actionBefore, action):
        if str(action.text()) not in self._actions:
            self._actions.append(str(action.text()))
            QtWidgets.QMenu.insertAction(self, actionBefore, action)

    def addAction(self, action):
        if str(action.text()) not in self._actions:
            self._actions.append(str(action.text()))
            QtWidgets.QMenu.addAction(self, action)

    def addMenu(self, menu):
        if str(menu.title()) not in self._menus:
            self._menus.append(str(menu.title()))
            QtWidgets.QMenu.addMenu(self, menu)
