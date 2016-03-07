# Copyright 2016 by Kurt Rathjen. All Rights Reserved.
#
# Permission to use, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Kurt Rathjen
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# KURT RATHJEN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# KURT RATHJEN BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import logging

from PySide import QtGui

import studiolibrary
import studiolibrary.gui


__all__ = ["Plugin"]

logger = logging.getLogger(__name__)


class Plugin(studiolibrary.BasePlugin):

    def __init__(self, library):
        studiolibrary.BasePlugin.__init__(self)
        self._library = library

        self._iconPath = ""
        self._action = None
        self._pixmap = None
        self._settings = None
        self._extension = None
        self._loggerLevel = logging.NOTSET

    @staticmethod
    def defaultSettingsPath():
        """
        :rtype: str
        """
        return os.path.join(studiolibrary.Settings.DEFAULT_PATH, "Plugin")

    def createWidget(self, parent=None):
        """
        :type parent: QtGui.QWidget or None
        :rtype: QtGui.QWidget or None
        """
        pass

    def infoWidget(self, parent, record):
        """
        :type parent: QtGui.QWidget or None
        :type record: studiolibrary.Record
        :rtype: QtGui.QWidget or None
        """
        pass

    def previewWidget(self, parent, record):
        """
        :type parent: QtGui.QWidget or None
        :type record: studiolibrary.Record
        :rtype: QtGui.QWidget or None
        """
        pass

    def newAction(self, parent=None):
        """
        :type parent: QtGui.QWidget or None
        :rtype: QtCore.QAction
        """
        icon = QtGui.QIcon(self.iconPath())
        action = QtGui.QAction(icon, self.name(), parent)
        return action

    def recordContextMenu(self, menu, records):
        """
        :type menu: QtGui.QMenu
        :type records: list[studiolibrary.Record]
        :rtype: None
        """
        pass

    def settingsPath(self):
        """
        :rtype: str
        """
        return os.path.join(self.defaultSettingsPath(), self.name() + ".dict")

    def setLoggerLevel(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self._loggerLevel = value

    def loggerLevel(self):
        """
        :rtype: bool
        """
        return self._loggerLevel

    def library(self):
        """
        :rtype: studiolibrary.Library
        """
        return self._library

    def libraryWidget(self):
        """
        :rtype: studiolibrary.gui.LibraryWidget
        """
        return self.library().libraryWidget()

    def match(self, path):
        """
        :type path: str
        :rtype: bool
        """
        if path.endswith(self.extension()):
            return True
        return False

    def pixmap(self):
        """
        :rtype: QtGui.QPixmap
        """
        if not self._pixmap:
            iconPath = self.iconPath()
            if os.path.exists(str(iconPath)):
                self._pixmap = QtGui.QPixmap(iconPath)
        return self._pixmap

    def setExtension(self, extension):
        """
        :type extension: str
        """
        if not extension.startswith("."):
            extension = "." + extension
        self._extension = extension

    def extension(self):
        """
        :rtype : str
        """
        if not self._extension:
            return "." + self.name().lower()
        return self._extension

    def settings(self):
        """
        :rtype: studiolibrary.Settings
        """
        if not self._settings:
            self._settings = studiolibrary.MetaFile(self.settingsPath())
        return self._settings

    def setIconPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        self._iconPath = path

    def iconPath(self):
        """
        :rtype: str
        """
        return self._iconPath

    def folderSelectionChanged(self, selected, deselected):
        """
        :type selected: list[studiolibrary.Folder]
        :type deselected: list[studiolibrary.Folder]
        :rtype: None
        """
        pass
