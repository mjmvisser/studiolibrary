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
import shutil
import logging
import traceback

from PySide import QtGui
from PySide import QtCore

import studioqt
import studiolibrary

try:
    import mutils
    import maya.cmds
except ImportError, msg:
    print msg


__all__ = ["Plugin", "PreviewWidget", "CreateWidget"]

logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class ValidateError(PluginError):
    """"""
    pass


class NamespaceOption:
    FromFile = "pose"
    FromCustom = "custom"
    FromSelection = "selection"


class Plugin(studiolibrary.Plugin):

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        studiolibrary.Plugin.__init__(self, library)

    @staticmethod
    def settings():
        """
        :rtype: studiolibrary.Settings
        """
        return studiolibrary.Settings.instance("Plugin", "MayaBase")

    @staticmethod
    def tempIconPath(clean=False):
        """
        :rtype: str
        """
        tempDir = studiolibrary.TempDir("icon", clean=clean)
        return tempDir.path() + "/thumbnail.jpg"

    @staticmethod
    def tempIconSequencePath(clean=False):
        """
        :rtype: str
        """
        tempDir = studiolibrary.TempDir("sequence", clean=clean)
        return tempDir.path() + "/thumbnail.jpg"

    @staticmethod
    def createTempIcon():
        """
        :rtype: str
        """
        path = Plugin.tempIconPath()
        return mutils.snapshot(path=path)

    @staticmethod
    def createTempIconSequence(startFrame=None, endFrame=None, step=1):
        """
        :type startFrame: int
        :type endFrame: int
        :type step: int
        :rtype: str
        """
        path = Plugin.tempIconSequencePath(clean=True)

        sequencePath = mutils.snapshot(
            path=path,
            start=startFrame,
            end=endFrame,
            step=step,
        )

        iconPath = Plugin.tempIconPath()
        shutil.copyfile(sequencePath, iconPath)
        return iconPath, sequencePath

    @staticmethod
    def selectionModifiers():
        """
        :rtype: dict[bool]
        """
        result = {"add": False, "deselect": False}
        modifiers = QtGui.QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.ShiftModifier:
            result["deselect"] = True
        elif modifiers == QtCore.Qt.ControlModifier:
            result["add"] = True

        return result

    def setLoggerLevel(self, level):
        """
        :type level: int
        :rtype: None
        """
        logger_ = logging.getLogger("mutils")
        logger_.setLevel(level)

        logger_ = logging.getLogger("studiolibraryplugins")
        logger_.setLevel(level)

    def recordContextMenu(self, menu, records):
        """
        :type menu: QtGui.QMenu
        :type records: list[Record]
        :rtype: None
        """
        import selectionsetmenu

        if records:

            record = records[-1]

            action = selectionsetmenu.selectContentAction(record, parent=menu)
            menu.addAction(action)
            menu.addSeparator()

            subMenu = record.selectionSetsMenu(parent=menu, enableSelectContent=False)
            menu.addMenu(subMenu)
            menu.addSeparator()


class Record(studiolibrary.Record):

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        studiolibrary.Record.__init__(self, *args, **kwargs)

        self._namespaces = []
        self._customNamespaces = ""
        self._namespaceOption = NamespaceOption.FromSelection

        self._transferClass = None
        self._transferObject = None
        self._transferBasename = None

    def prettyPrint(self):
        """
        :rtype: None
        """
        print("------ %s ------" % self.name())
        import json
        print json.dumps(self.transferObject().data(), indent=2)
        print("----------------\n")

    @staticmethod
    def createTempSnapshot():
        """
        Convenience method.

        :rtype: str
        """
        return Plugin.createTempSnapshot()

    @staticmethod
    def createTempImageSequence(startFrame, endFrame, step=1):
        """
        Convenience method.

        :type startFrame: int
        :type endFrame: int
        :type step: int
        :rtype: str
        """
        imageSequence = Plugin.createTempImageSequence(
                startFrame=startFrame,
                endFrame=endFrame,
                step=step
        )
        return imageSequence

    def showErrorDialog(self, message, title="Record Error"):
        """
        :type title: str
        :type message: str
        :rtype: int
        """
        return QtGui.QMessageBox.critical(None, title, str(message))

    def showSelectionSetsMenu(self, **kwargs):
        """
        :rtype: QtGui.QAction
        """
        menu = self.selectionSetsMenu(**kwargs)
        position = QtGui.QCursor().pos()
        action = menu.exec_(position)
        return action

    def selectionSetsMenu(self, parent=None, enableSelectContent=True):
        """
        :type parent: QtGui.QWidget
        :type enableSelectContent: bool
        :rtype: QtGui.QMenu
        """
        import selectionsetmenu

        namespaces = self.namespaces()

        menu = selectionsetmenu.SelectionSetMenu(
                record=self,
                parent=parent,
                namespaces=namespaces,
                enableSelectContent=enableSelectContent,
        )
        return menu

    def mirrorTables(self):
        """
        :rtype: str
        """
        return studiolibrary.findPaths(self.path(), ".mirror", direction=studiolibrary.Direction.Up)

    def selectContent(self, namespaces=None, **kwargs):
        """
        :type namespaces: list[str]
        """
        namespaces = namespaces or self.namespaces()
        kwargs = kwargs or Plugin.selectionModifiers()

        msg = "Select content: Record.selectContent(namespacea={0}, kwargs={1})"
        msg = msg.format(namespaces, kwargs)
        logger.debug(msg)

        try:
            self.transferObject().select(namespaces=namespaces, **kwargs)
        except Exception, msg:
            title = "Error while selecting content"
            QtGui.QMessageBox.critical(None, title, str(msg))
            raise

    def setTransferClass(self, classname):
        """
        :type classname: mutils.TransferObject
        """
        self._transferClass = classname

    def transferClass(self):
        """
        :rtype:
        """
        return self._transferClass

    def transferPath(self):
        """
        :rtype: str
        """
        if self.transferBasename():
            return "/".join([self.path(), self.transferBasename()])
        else:
            return self.path()

    def transferBasename(self):
        """
        :rtype: str
        """
        return self._transferBasename

    def setTransferBasename(self, transferBasename):
        """
        :rtype: str
        """
        self._transferBasename = transferBasename

    def transferObject(self):
        """
        :rtype: mutils.TransferObject
        """
        if not self._transferObject:
            path = self.transferPath()
            if os.path.exists(path):
                self._transferObject = self.transferClass().fromPath(path)
        return self._transferObject

    def settings(self):
        """
        :rtype: studiolibrary.Settings
        """
        return Plugin.settings()

    def namespaces(self):
        """
        :rtype: list[str]
        """
        namespaces = []
        namespaceOption = self.namespaceOption()

        # When creating a new record we can only get the namespaces from
        # selection because the file (transferObject) doesn't exist yet.
        if not self.transferObject():
            namespaces = self.namespaceFromSelection()

        # If the file (transferObject) exists then we can use the namespace
        # option to determined which namespaces to return.
        elif namespaceOption == NamespaceOption.FromFile:
            namespaces = self.namespaceFromFile()

        elif namespaceOption == NamespaceOption.FromCustom:
            namespaces = self.namespaceFromCustom()

        elif namespaceOption == NamespaceOption.FromSelection:
            namespaces = self.namespaceFromSelection()

        return namespaces

    def setNamespaceOption(self, namespaceOption):
        """
        :type namespaceOption: NamespaceOption
        :rtype: None
        """
        self.settings().set("namespaceOption", namespaceOption)

    def namespaceOption(self):
        """
        :rtype: NamespaceOption
        """
        namespaceOption = self.settings().get(
                "namespaceOption",
                NamespaceOption.FromSelection
        )
        return namespaceOption

    def setCustomNamespaces(self, namespaces):
        """
        :type namespaces: list[str]
        :rtype: None
        """
        self.settings().set("namespaces", namespaces)

    def namespaceFromFile(self):
        """
        :rtype: list[str]
        """
        return self.transferObject().namespaces()

    def namespaceFromCustom(self):
        """
        :rtype: list[str]
        """
        return self.settings().get("namespaces", "")

    @staticmethod
    def namespaceFromSelection():
        """
        :rtype: list[str]
        """
        return mutils.getNamespaceFromSelection() or [""]

    def objectCount(self):
        """
        :rtype: int
        """
        if self.transferObject():
            return self.transferObject().count()
        else:
            return 0

    def doubleClicked(self):
        """
        :rtype: None
        """
        self.load()

    def load(self, objects=None, namespaces=None, **kwargs):
        """
        :type namespaces: list[str]
        :type objects: list[str]
        :rtype: None
        """
        logger.debug("Loading: %s" % self.transferPath())

        self.transferObject().load(objects=objects, namespaces=namespaces, **kwargs)

        logger.debug("Loaded: %s" % self.transferPath())

    def save(self, objects, path=None, iconPath=None, force=False, **kwargs):
        """
        :type path: path
        :type objects: list
        :type iconPath: str
        :raise ValidateError:
        """
        logger.info("Saving: {0}".format(path))

        contents = list()
        tempDir = studiolibrary.TempDir("Transfer", clean=True)

        transferPath = tempDir.path() + "/" + self.transferBasename()
        t = self.transferClass().fromObjects(objects)
        t.save(transferPath, **kwargs)

        if iconPath:
            contents.append(iconPath)

        contents.append(transferPath)
        studiolibrary.Record.save(self, path=path, contents=contents, force=force)

        logger.info("Saved: {0}".format(path))


class BaseWidget(QtGui.QWidget):

    stateChanged = QtCore.Signal(object)

    def __init__(self, record, parent=None):
        """
        :type record: Record
        :type parent: studiolibrary.LibraryWidget
        """
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("studioLibraryPluginsWidget")

        studioqt.loadUi(self)

        self._record = None
        self._iconPath = ""
        self._scriptJob = None

        self.setRecord(record)
        self.loadSettings()

        try:
            self.selectionChanged()
            self.enableScriptJob()
        except NameError, msg:
            logger.exception(msg)

    def enableScriptJob(self):
        """
        :rtype: None
        """
        if not self._scriptJob:
            event = ['SelectionChanged', self.selectionChanged]
            self._scriptJob = mutils.ScriptJob(event=event)

    def setRecord(self, record):
        """
        :type record: Record
        """
        self._record = record

        if hasattr(self.ui, 'name'):
            self.ui.name.setText(record.name())

        if hasattr(self.ui, 'owner'):
            self.ui.owner.setText(str(record.owner()))

        if hasattr(self.ui, 'comment'):
            if isinstance(self.ui.comment, QtGui.QLabel):
                self.ui.comment.setText(record.description())
            else:
                self.ui.comment.setPlainText(record.description())

        if hasattr(self.ui, "contains"):
            self.updateContains()

        if hasattr(self.ui, 'snapshotButton'):
            path = record.iconPath()
            if os.path.exists(path):
                self.setIconPath(record.iconPath())

        ctime = record.ctime()
        if hasattr(self.ui, 'created') and ctime:
            self.ui.created.setText(studiolibrary.timeAgo(str(ctime)))

    def record(self):
        """
        :rtype: Record
        """
        return self._record

    def setState(self, state):
        """
        :type state: dict
        :rtype: None
        """
        self.stateChanged.emit(self)

    def updateState(self):
        """
        :rtype: None
        """
        self.stateChanged.emit(self)

    def state(self):
        """
        :rtype: dict
        """
        return {}

    def iconPath(self):
        """
        :rtype str
        """
        return self._iconPath

    def setIconPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        self._iconPath = path
        icon = QtGui.QIcon(QtGui.QPixmap(path))
        self.setIcon(icon)

    def setIcon(self, icon):
        """
        :type icon: QtGui.QIcon
        """
        self.ui.snapshotButton.setIcon(icon)
        self.ui.snapshotButton.setIconSize(QtCore.QSize(200, 200))
        self.ui.snapshotButton.setText("")

    def settings(self):
        """
        :rtype: studiolibrary.Settings
        """
        return self.record().settings()

    def libraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget
        """
        return self.record().plugin().libraryWidget()

    def showSelectionSetsMenu(self):
        """
        :rtype: None
        """
        record = self.record()
        record.showSelectionSetsMenu()

    def selectionChanged(self):
        """
        :rtype: None
        """
        pass

    def nameText(self):
        """
        :rtype: str
        """
        return str(self.ui.name.text()).strip()

    def description(self):
        """
        :rtype: str
        """
        return str(self.ui.comment.toPlainText()).strip()

    def loadSettings(self):
        """
        :rtype: None
        """
        pass

    def saveSettings(self):
        """
        :rtype: None
        """
        pass

    def scriptJob(self):
        """
        :rtype: mutils.ScriptJob
        """
        return self._scriptJob

    def close(self):
        """
        :rtype: None
        """
        sj = self.scriptJob()
        if sj:
            sj.kill()
        QtGui.QWidget.close(self)

    def objectCount(self):
        """
        :rtype: int
        """
        return 0

    def updateContains(self):
        """
        :rtype: None
        """
        if hasattr(self.ui, "contains"):
            count = self.objectCount()
            plural = "s" if count > 1 else ""
            self.ui.contains.setText(str(count) + " Object" + plural)


class InfoWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtGui.QWidget
        """
        BaseWidget.__init__(self, *args, **kwargs)

    def objectCount(self):
        """
        :rtype: int
        """
        if self.record().exists():
            return self.record().objectCount()
        return 0


class PreviewWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtGui.QWidget
        """
        BaseWidget.__init__(self, *args, **kwargs)

        self.setupConnections()

    def setupConnections(self):
        """
        :rtype: None
        """
        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

        self.ui.useFileNamespace.clicked.connect(self.updateState)
        self.ui.useCustomNamespace.clicked.connect(self.setFromCustomNamespace)
        self.ui.useSelectionNamespace.clicked.connect(self.updateState)
        self.ui.namespaceEdit.textEdited[str].connect(self.updateState)

    def objectCount(self):
        """
        :rtype: int
        """
        objectCount = 0

        if self.record().exists():
            objectCount = self.record().objectCount()

        return objectCount

    def updateState(self):
        """
        :rtype: None
        """
        logger.debug("Updating widget state")

        self.updateNamespaceEdit()
        self.saveSettings()

        BaseWidget.updateState(self)

    def namespaces(self):
        """
        :rtype: list[str]
        """
        namespaces = str(self.ui.namespaceEdit.text())
        namespaces = studiolibrary.stringToList(namespaces)
        return namespaces

    def setNamespaces(self, namespaces):
        """
        :type namespaces: list
        :rtype: None
        """
        namespaces = studiolibrary.listToString(namespaces)
        self.ui.namespaceEdit.setText(namespaces)

    def namespaceOption(self):
        """
        :rtype: NamespaceOption
        """
        if self.ui.useFileNamespace.isChecked():
            namespaceOption = NamespaceOption.FromFile
        elif self.ui.useCustomNamespace.isChecked():
            namespaceOption = NamespaceOption.FromCustom
        else:
            namespaceOption = NamespaceOption.FromSelection

        return namespaceOption

    def setNamespaceOption(self, namespaceOption):
        """
        :type namespaceOption: NamespaceOption
        """
        if namespaceOption == NamespaceOption.FromFile:
            self.ui.useFileNamespace.setChecked(True)
        elif namespaceOption == NamespaceOption.FromCustom:
            self.ui.useCustomNamespace.setChecked(True)
        else:
            self.ui.useSelectionNamespace.setChecked(True)

    def setState(self, state):
        """
        :type state: dict
        """
        namespaces = state.get("namespaces", "")
        self.setNamespaces(namespaces)

        namespaceOption = state.get("namespaceOption", "")
        self.setNamespaceOption(namespaceOption)

        super(PreviewWidget, self).setState(state)

    def state(self):
        """
        :rtype: dict
        """
        state = super(PreviewWidget, self).state()

        state["namespaces"] = self.namespaces()
        state["namespaceOption"] = self.namespaceOption()

        return state

    def loadSettings(self):
        """
        :rtype: None
        """
        settings = self.settings()
        self.setState(settings.data())

    def saveSettings(self):
        """
        :rtype: None
        """
        settings = self.settings()
        settings.data().update(self.state())
        settings.save()

    def selectionChanged(self):
        """
        :rtype: None
        """
        self.updateNamespaceEdit()

    def updateNamespaceEdit(self):
        """
        :rtype: None
        """
        logger.debug('Updating namespace edit')

        namespaces = None

        if self.ui.useSelectionNamespace.isChecked():
            namespaces = mutils.getNamespaceFromSelection()
        elif self.ui.useFileNamespace.isChecked():
            namespaces = self.record().transferObject().namespaces()

        if not self.ui.useCustomNamespace.isChecked():
            self.ui.namespaceEdit.setEnabled(False)
            self.setNamespaces(namespaces)
        else:
            self.ui.namespaceEdit.setEnabled(True)

    def setFromCustomNamespace(self, value=True):
        """
        :type value: bool
        :rtype: None
        """
        self.ui.useCustomNamespace.setChecked(value)
        self.ui.namespaceEdit.setEnabled(value)
        self.ui.namespaceEdit.setFocus()
        self.updateState()

    def accept(self):
        """
        :rtype: None
        """
        try:
            self.record().load()
        except Exception, msg:
            title = "Error while loading"
            QtGui.QMessageBox.critical(None, title, str(msg))
            raise


class CreateWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtGui.QWidget
        """
        BaseWidget.__init__(self, *args, **kwargs)

        self._iconPath = ""
        self._focusWidget = None

        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.snapshotButton.clicked.connect(self.snapshot)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

        # import mutils.modelpanelwidget
        # self._modelPanel = mutils.modelpanelwidget.ModelPanelWidget(self.ui.modelPanelFrame)
        # self.ui.modelPanelFrame.layout().insertWidget(0, self._modelPanel)
        # self.ui.snapshotButton.hide()

    def objectCount(self):
        """
        :rtype: int
        """
        selection = []
        try:
            selection = maya.cmds.ls(selection=True) or []
        except NameError, e:
            traceback.print_exc()

        return len(selection)

    def dirname(self):
        """
        :rtype: str or None
        """
        dirname = self.record().dirname()

        if not dirname:
            dirname = self.selectedFolderPath()

        return dirname

    def selectedFolderPath(self):
        """
        :rtype: str or None
        """
        dirname = None
        folder = self.libraryWidget().selectedFolder()

        if folder:
            dirname = folder.path()

        return dirname

    def showSelectionSetsMenu(self):
        """
        :rtype: None
        """
        import selectionsetmenu

        dirname = self.dirname()
        menu = selectionsetmenu.SelectionSetMenu.fromPath(dirname)
        position = QtGui.QCursor().pos()

        menu.exec_(position)

    def selectionChanged(self):
        """
        :rtype: None
        """
        self.updateContains()

    def modelPanel(self):
        """
        :rtype: mutils.ModelPanelWidget
        """
        return self._modelPanel

    def snapshot(self):
        """
        :rtype: None
        """
        try:
            path = Plugin.createTempIcon()
            self.setIconPath(path)
        except Exception, msg:
            title = "Error while taking snapshot"
            QtGui.QMessageBox.critical(None, title, str(msg))
            raise

    def snapshotQuestion(self):
        """
        :rtype: int
        """
        title = "Create a snapshot icon"
        message = "Would you like to create a snapshot icon?"
        options = QtGui.QMessageBox.Yes | QtGui.QMessageBox.Ignore | QtGui.QMessageBox.Cancel

        result = QtGui.QMessageBox.question(None, title, str(message), options)

        if result == QtGui.QMessageBox.Yes:
            self.snapshot()

        return result

    def accept(self):
        """
        :rtype: None
        """
        try:
            name = self.nameText()
            objects = maya.cmds.ls(selection=True) or []
            dirname = self.dirname()

            if not dirname:
                raise ValidateError("No folder selected. Please select a destination folder.")

            if not name:
                raise ValidateError("No name specified. Please set a name before saving.")

            if not objects:
                raise ValidateError("No objects selected. Please select at least one object.")

            if not os.path.exists(self.iconPath()):
                result = self.snapshotQuestion()
                if result == QtGui.QMessageBox.Cancel:
                    return

            path = dirname + "/" + name
            description = str(self.ui.comment.toPlainText())

            self.save(
                path=path,
                objects=objects,
                iconPath=self.iconPath(),
                description=description,
            )

        except Exception, msg:
            title = "Error while saving"
            QtGui.QMessageBox.critical(None, title, str(msg))
            raise

    def save(self, objects, path, iconPath, description):
        """
        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type description: str
        :rtype: None
        """
        r = self.record()
        r.setDescription(description)
        r.save(objects=objects, path=path, iconPath=iconPath)
