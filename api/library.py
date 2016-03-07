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
from PySide import QtCore

import studioqt
import studiolibrary


__all__ = ["Library", "LibraryError"]

logger = logging.getLogger(__name__)


class LibraryError(Exception):
    """"""
    pass


class LibraryValidateError(LibraryError):
    """"""
    pass


class LibrarySignal(QtCore.QObject):
    """"""
    onAdded = QtCore.Signal(object)
    onLoaded = QtCore.Signal(object)
    onDeleted = QtCore.Signal(object)
    onPathChanged = QtCore.Signal(object)
    onSettingsSaved = QtCore.Signal(object)


class Library(object):

    _libraries = {}

    signal = LibrarySignal()
    onAdded = signal.onAdded
    onLoaded = signal.onLoaded
    onDeleted = signal.onDeleted
    onPathChanged = signal.onPathChanged
    onSettingsSaved = signal.onSettingsSaved

    DEFAULT_NAME = "Default"
    DEFAULT_PLUGINS = []
    DEFAULT_COLOR = "rgb(0, 175, 255)"
    DEFAULT_BACKGROUND_COLOR = "rgb(70, 70, 70)"
    SETTINGS_DIALOG_TEXT = "All changes will be saved to your local settings."
    WELCOME_DIALOG_TEXT = """Before you get started please choose a folder location for storing the data. \
A network folder is recommended for sharing within a studio."""

    @classmethod
    def fromName(cls, name=None):
        """
        :type name: str
        :rtype: list[Library]
        """
        if not name:
            name = Library.DEFAULT_NAME

        if name not in Library._libraries:
            library = cls()
            library.setName(name)
            Library._libraries[name] = library

        return Library._libraries[name]

    @staticmethod
    def default():
        """
        :rtype: list[Library]
        """
        for library in Library.libraries():
            if library.isDefault():
                return library

        return Library.fromName(Library.DEFAULT_NAME)

    def __init__(self):

        self._name = None
        self._debug = False
        self._theme = None
        self._settings = {}
        self._libraryWidget = None
        self._settingsDialog = None
        self._pluginManager = studiolibrary.PluginManager()

    @staticmethod
    def libraries():
        """
        :rtype: list[Library]
        """
        Library.initLibraries()
        libraries = Library._libraries.values()
        libraries.sort(key=lambda lib: lib.name())
        return libraries

    @staticmethod
    def initLibraries():
        """
        :rtype: None
        """
        path = Library.defaultSettingsPath()
        if os.path.exists(path):
            for name in os.listdir(path):
                filename, extension = os.path.splitext(name)
                library_ = Library.fromName(filename)

    @staticmethod
    def defaultSettingsPath():
        """
        :rtype: str
        """
        return os.path.join(studiolibrary.Settings.DEFAULT_PATH, "Library")

    @staticmethod
    def windows():
        """
        :rtype: list[MainWindow]
        """
        result = []
        for library in Library.libraries():
            if library.libraryWidget() is not None:
                result.append(library.libraryWidget())

        return result

    @staticmethod
    def sortRecords(records, sort=studiolibrary.SortOption.Ordered, order=None):
        """
        :type records: list[studiolibrary.Record]
        :type sort: studiolibrary.SortOption
        :type order: list[str]
        :rtype: list[studiolibrary.Record]
        """
        order = order or []
        result = []
        _records = {}

        # Index records
        for record in records:
            if sort == studiolibrary.SortOption.Ordered:
                _records.setdefault(record.name(), record)
            elif sort == studiolibrary.SortOption.Modified:
                _records.setdefault(record.mtime() + str(id(record)), record)

        # Sort records by custom order
        if sort == studiolibrary.SortOption.Ordered:
            for name in order:
                if name in _records:
                    result.append(_records[name])

            for name in _records:
                if name not in order and name in _records:
                    result.append(_records[name])

        # Sort records by modified
        elif sort == studiolibrary.SortOption.Modified:
            order = sorted(_records.keys())
            order.reverse()
            for mtime in order:
                result.append(_records[mtime])

        else:
            result = records
        return result

    def listRecords(self, path):
        """
        :type path: str
        :rtype: studiolibrary.Records
        """
        records = []
        paths = studiolibrary.listPaths(path)
        for path in paths:
            record = self.recordFromPath(path)
            if record:
                records.append(record)
        return records

    def findRecords(self, path, search=None, direction=studiolibrary.Direction.Down):
        """
        :type path: str
        :type search: str
        :type direction: studiolibrary.Direction
        :rtype: studiolibrary.Records
        """
        records = []
        paths = studiolibrary.findPaths(path, search=search, direction=direction)
        for path in paths:
            record = self.recordFromPath(path)
            if record:
                records.append(record)
        return records

    def recordFromPath(self, path):
        """
        :type path: str
        :rtype: studiolibrary.Record
        :raise: LibraryError
        """
        plugins = self.pluginManager().plugins().values()
        for plugin in plugins:
            if plugin.match(path):
                return plugin.record(path)
        logger.debug('Cannot find plugin for path extension "%s"' % path)

    def setLoggerLevel(self, level):
        """
        :type level: int
        """
        logger = logging.getLogger("studiolibrary")
        logger.setLevel(level)

        for plugin in self.pluginManager().plugins().values():
            plugin.setLoggerLevel(level)

    def isDebug(self):
        """
        :rtype: bool
        """
        return self._debug

    def showDeleteDialog(self):
        """
        :rtype: None
        """
        message = """Would you like to remove "%s" library from the manager?
This does not modify or delete the contents of the library.""" % self.name()

        result = QtGui.QMessageBox.question(None, "Remove Library", message,
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if result == QtGui.QMessageBox.Yes:
            self.delete()
        return result

    def delete(self):
        """
        :rtype: None
        """
        logger.debug("Deleting library: %s" % self.name())

        self.settings().delete()
        if self.libraryWidget():
            self.libraryWidget().close(saveSettings=False)

        if self.settingsDialog():
            self.settingsDialog().close()

        del Library._libraries[self.name()]

        Library.onDeleted.emit(self)
        logger.debug("Deleted library: %s" % self.name())

    def name(self):
        """
        :rtype: str
        """
        return self._name

    def setName(self, name):
        """
        :type name: str
        :rtype: None
        """
        if self.name() == name:
            return

        self.validateName(name)

        if self._name in self._libraries:
            self._libraries[name] = self._libraries.pop(self.name())
        self._name = name

        settingsPath = self.settingsPath()

        if not self.settings():
            s = studiolibrary.MetaFile(settingsPath)
            self.setSettings(s)
        elif not self.settings().exists():
            self.settings().setPath(settingsPath)
        else:
            self.settings().rename(name, extension=".dict")

    def readSettings(self):
        """
        :rtype: studiolibrary.MetaFile
        """
        settings = studiolibrary.MetaFile(self.settingsPath())
        return settings

    def settingsPath(self):
        """
        :rtype: str
        """
        name = self.name()
        return Library.defaultSettingsPath() + "/" + name + ".dict"

    def pluginManager(self):
        """
        :rtype: studiolibrary.PluginManager
        """
        return self._pluginManager

    def plugins(self):
        """
        :rtype: list[str]
        """
        return self.settings().get("plugins", Library.DEFAULT_PLUGINS)

    def loadPlugin(self, name):
        """
        :type name:
        :rtype: None
        """
        return self.pluginManager().loadPlugin(name, library=self)

    def loadPlugins(self):
        """
        :rtype: None
        """
        for name in self.plugins():
            self.loadPlugin(name)

    def loadedPlugins(self):
        """
        :rtype: dict[studiolibrary.Plugin]
        """
        return self.pluginManager().plugins()

    def unloadPlugins(self):
        """
        :rtype: None
        """
        self.pluginManager().unloadPlugins()

    def unloadPlugin(self, name):
        """
        :type name: str
        """
        plugin = self.pluginManager().get(name, None)
        if plugin:
            self.pluginManager().unloadPlugin(plugin)
        else:
            logger.debug("Cannot find plugin with name '%s'" % name)

    def setPlugins(self, value):
        """
        :type value:
        :rtype: None
        """
        self.settings().set("plugins", value)

    def setKwargs(self, kwargs):
        """
        :type kwargs: dict
        :rtype: None
        """
        self.settings().set("kwargs", kwargs)

    def kwargs(self):
        """
        :rtype: dict
        """
        return self.settings().get("kwargs", {})

    def theme(self):
        """
        :rtype: dict
        """
        if self._theme is None:
            c1 = self.accentColor()
            b1 = self.backgroundColor()

            textWhite = studioqt.Color(255, 255, 255, 255)
            backgroundWhite = studioqt.Color(255, 255, 255, 20)

            self._theme = {
                "PACKAGE_DIRNAME": studiolibrary.DIRNAME,
                "RESOURCE_DIRNAME": studiolibrary.RESOURCE_DIRNAME,

                "ACCENT_COLOR": c1.toString(),
                "ACCENT_COLOR_R": str(c1.red()),
                "ACCENT_COLOR_G": str(c1.green()),
                "ACCENT_COLOR_B": str(c1.blue()),

                "BACKGROUND_COLOR": b1.toString(),
                "BACKGROUND_COLOR_R": str(b1.red()),
                "BACKGROUND_COLOR_G": str(b1.green()),
                "BACKGROUND_COLOR_B": str(b1.blue()),

                "RECORD_TEXT_COLOR": textWhite.toString(),
                "RECORD_TEXT_SELECTED_COLOR": textWhite.toString(),

                "RECORD_BACKGROUND_COLOR": backgroundWhite.toString(),
                "RECORD_BACKGROUND_SELECTED_COLOR":  c1.toString(),
            }

        return self._theme

    def styleSheet(self):
        """
        :rtype: str
        """
        self._theme = None  # clear theme options
        path = studiolibrary.RESOURCE_DIRNAME + "/css/default.css"
        styleSheet = studioqt.StyleSheet.fromPath(path, options=self.theme())
        return styleSheet.data()

    def accentColor(self):
        """
        :rtype: studioqt.Color
        """
        c = self.settings().get("color", Library.DEFAULT_COLOR)  # Legacy
        c = self.settings().get("accentColor", c)
        return studioqt.Color.fromString(c)

    def setAccentColor(self, color):
        """
        :type color: studioqt.Color
        """
        c = studioqt.Color(color.red(), color.green(), color.blue(), color.alpha())
        self.settings().set("accentColor", c.toString())

    def backgroundColor(self):
        """
        :rtype: studioqt.Color
        """
        c = self.settings().get("backgroundColor", Library.DEFAULT_BACKGROUND_COLOR)
        return studioqt.Color.fromString(c)

    def setBackgroundColor(self, color):
        """
        :type color: studioqt.Color
        """
        c = studioqt.Color(color.red(), color.green(), color.blue(), color.alpha())
        self.settings().set("backgroundColor", c.toString())

    def path(self):
        """
        :rtype: str
        """
        return self.settings().get("path", "")

    def validateName(self, name, caseSensitive=True):
        """
        :type name: str
        """
        libraries = {}

        if not name or not name.strip():
            raise LibraryValidateError('Cannot use an empty name "%s"!' % name)

        try:
            name.decode('ascii')
        except UnicodeDecodeError:
            raise LibraryValidateError('The name "%s" is not an ascii-encoded string!' % name)

        studiolibrary.validateString(name)

        if name in Library._libraries:
            if self != Library._libraries[name]:
                raise LibraryValidateError('The Library "%s" already exists!' % name)

        if caseSensitive:
            for n in Library._libraries:
                libraries[n.lower()] = Library._libraries[n]

            if name.lower() in libraries:
                if self != libraries[name.lower()]:
                    raise LibraryValidateError('The Library "%s" already exists. It is case sensitive!' % name)

    @staticmethod
    def validatePath(path):
        """
        :type path: str
        """
        if "\\" in path:
            raise LibraryValidateError("Please use '/' instead of '\\'. Invalid token found for path '%s'!" % path)

        if not path or not path.strip():
            raise LibraryValidateError("Cannot set an empty path '%s'!" % path)

        if not os.path.exists(path):
            raise LibraryValidateError("Cannot find folder path '%s'!" % path)

    def setPath(self, path):
        """
        :type path: str
        """
        self.validatePath(path)
        self.settings().set("path", path)
        Library.onPathChanged.emit(self)

    def setDefault(self, value):
        """
        :type value: bool
        :rtype: None
        """
        for library in self.libraries():
            library._setDefault(False)
        self._setDefault(value)

    def _setDefault(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self.settings().set("isDefault", value)

    def isDefault(self):
        """
        :rtype: bool
        """
        return self.settings().get("isDefault", False)

    def settings(self):
        """
        :rtype: studiolibrary.MetaFile
        """
        return self._settings

    def setSettings(self, settings):
        """
        :type settings: studiolibrary.MetaFile
        """
        self._settings = settings

    def libraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget
        """
        return self._libraryWidget

    def setLibraryWidget(self, libraryWidget):
        """
        :type libraryWidget: studiolibrary.LibraryWidget
        """
        self._libraryWidget = libraryWidget

    def load(self):
        """
        :rtype: None
        """
        self.show(**self.kwargs())

    def show(self, **kwargs):
        """
        :rtype: None
        """
        if not self.path():
            result = self.execWelcomeDialog()
            if result == QtGui.QDialog.Rejected:
                logger.debug("Dialog was canceled")
                return

        elif not os.path.exists(self.path()):
            result = self.execSettingsDialog()
            if result == QtGui.QDialog.Rejected:
                logger.debug("Dialog was canceled")
                return

        logger.debug("Showing library '%s'" % self.path())
        self.setKwargs(kwargs)

        # Create a new window
        if not self.libraryWidget():
            libraryWidget = studiolibrary.LibraryWidget(library=self)
            self.setLibraryWidget(libraryWidget)
        else:
            self.libraryWidget().close()

        self.libraryWidget().show()
        self.libraryWidget().raise_()

        Library.onLoaded.emit(self)

    def settingsDialog(self):
        """
        :rtype: studiolibrary.SettingsDialog
        """
        if not self._settingsDialog:
            self._settingsDialog = studiolibrary.SettingsDialog(None, library=self)
        return self._settingsDialog

    def setSettingsDialog(self, dialog):
        """
        :type dialog: studiolibrary.SettingsDialog
        """
        self._settingsDialog = dialog

    def execSettingsDialog(self):
        """
        :rtype: bool
        """
        self.showSettingsDialog()
        return self._execSettingsDialog()

    def execWelcomeDialog(self):
        """
        :rtype: bool
        """
        self.showWelcomeDialog()
        return self._execSettingsDialog()

    def _execSettingsDialog(self):
        """
        :rtype: bool
        """
        color = self.accentColor()
        backgroundColor = self.backgroundColor()
        result = self.settingsDialog().exec_()

        if result == QtGui.QDialog.Accepted:
            self.saveSettingsDialog()
        else:
            self.setAccentColor(color)
            self.setBackgroundColor(backgroundColor)

        return result

    @staticmethod
    def showNewLibraryDialog():
        """
        :rtype: None
        """
        library = Library()
        settings = studiolibrary.MetaFile("")
        library.setSettings(settings)

        settingsDialog = studiolibrary.SettingsDialog(None, library=library)
        settingsDialog.setTitle("New Library!")
        settingsDialog.setHeader("Create a new library")
        settingsDialog.setText("Create a new library with a different folder location and switch between them. "
                               "For example; This could be useful when working on different film productions, "
                               "or for having a shared library and a local library.")

        result = settingsDialog.exec_()

        if result == QtGui.QDialog.Accepted:
            name = settingsDialog.name()
            path = settingsDialog.location()

            library.validateName(name)
            library.validatePath(path)

            library = Library.fromName(name)
            library.setPath(path)
            library.settings().data().update(settings.data())
            library.show()
            Library.onAdded.emit(library)

            return library
        else:
            logger.info("New library dialog was canceled!")

    def showWelcomeDialog(self):
        """
        :rtype: None
        """
        self.showSettingsDialog()
        self.settingsDialog().setTitle("Hello!")
        self.settingsDialog().setHeader("Welcome to the Studio Library")
        self.settingsDialog().setText(Library.WELCOME_DIALOG_TEXT)
        return self.settingsDialog()

    def showSettingsDialog(self):
        """
        :rtype: None
        """
        self.settingsDialog().close()

        self.settingsDialog().setTitle("Settings")
        self.settingsDialog().setHeader("Local Library Settings")
        self.settingsDialog().setText(Library.SETTINGS_DIALOG_TEXT)

        self.settingsDialog().setName(self.name())
        self.settingsDialog().setLocation(self.path())
        self.settingsDialog().updateStyleSheet()

        self.settingsDialog().showNormal()
        return self.settingsDialog()

    def saveSettingsDialog(self):
        """
        :rtype: None
        """
        if len(Library.libraries()) == 1:
            self.setDefault(True)

        self.setName(self.settingsDialog().name())
        self.setAccentColor(self.settingsDialog().color())
        self.setPath(self.settingsDialog().location())
        self.setBackgroundColor(self.settingsDialog().backgroundColor())
        self.settings().save()
        self.settingsDialog().close()
        Library.onSettingsSaved.emit(self)