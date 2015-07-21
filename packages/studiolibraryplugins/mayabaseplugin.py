#!/usr/bin/python
"""
"""
import os
import logging
from functools import partial

try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore

try:
    import maya.cmds
except ImportError, msg:
    print msg

try:
    import mutils
except ImportError, msg:
    print msg


import studiolibrary
log = logging.getLogger("mayabaseplugin")


class PluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class ValidateError(PluginError):
    """"""
    pass


class NamespaceType:

    FromFile = "pose"
    FromCustom = "custom"
    FromSelection = "selection"

    def __init__(self):
        pass


class Plugin(studiolibrary.Plugin):

    def __init__(self, parent):
        """
        @type parent: QtGui.QWidget
        """
        studiolibrary.Plugin.__init__(self, parent)

    def namespaces(self):
        """
        @rtype: list[str]
        """
        return self.settings().get("namespaces")

    def setNamespaces(self, namespaces):
        """
        @type namespaces: list[str]
        """
        if isinstance(namespaces, basestring):
            namespaces = studiolibrary.stringToList(namespaces)
        self.settings().set("namespaces", namespaces)
        self.settings().save()

    def setNamespaceType(self, namespaceType):
        """
        @type namespaceType: NamespaceType | str
        """
        self.settings().set("namespaceType", namespaceType)
        self.settings().save()

    def namespaceType(self):
        """
        @rtype: NamespaceType
        """
        return self.settings().get("namespaceType", NamespaceType.FromSelection)

    @staticmethod
    def selectionModifiers():
        """
        @rtype: dict[bool]
        """
        result = {"add": False, "deselect": False}
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            result["deselect"] = True
        elif modifiers == QtCore.Qt.ControlModifier:
            result["add"] = True
        return result

    @mutils.unifyUndo
    def selectContent(self, records=None):
        """
        """
        records = records or self.window().selectedRecords()
        namespaces = self.namespaces()
        for record in records:
            record.transferObject().select(namespaces=namespaces, **self.selectionModifiers())


class Record(studiolibrary.Record):

    def __init__(self, *args, **kwargs):
        """
        @type args:
        @type kwargs:
        """
        studiolibrary.Record.__init__(self, *args, **kwargs)
        self._transferClass = None
        self._transferObject = None
        self._transferBasename = None

    def addSelectContentsAction(self, menu):
        """
        @type menu: QtGui.QMenu
        """
        records = self.window().selectedRecords()
        if records:
            icon = studiolibrary.icon(self.plugin().dirname() + "/images/arrow.png")
            action = studiolibrary.Action(icon, "Select content", menu)
            trigger = partial(self.plugin().selectContent, records)
            action.setCallback(trigger)
            menu.addAction(action)

    def mirrorTables(self):
        """
        @rtype:
        """
        return studiolibrary.findPaths(self.path(), ".mirror", direction=studiolibrary.Direction.Up)

    def selectionSets(self):
        """
        @rtype:
        """
        return studiolibrary.findRecordsFromSelectedFolders(self.window(), ".set", direction=studiolibrary.Direction.Down)

    def selectionSetsMenu(self, menu, records, includeSelectContents=False, showApplyButton=True):
        """
        @type menu: QtGui.QMenu
        @type records: list[Record]
        """
        if includeSelectContents:
            self.addSelectContentsAction(menu)
            menu.addSeparator()

        sets = self.selectionSets()
        for name in sorted(sets.iterkeys()):
            record = studiolibrary.createRecordFromPath(sets[name], window=self.window())
            trigger1 = partial(self.selectSelectionSet, record)
            if showApplyButton:
                trigger2 = partial(self.selectSelectionSet, record, True)
            else:
                trigger2 = None
            action = OptionAction(menu, name, callback1=trigger1, callback2=trigger2)
            menu.addAction(action)

        if not menu.actions():
            action = QtGui.QAction("Empty", menu)
            action.setEnabled(False)
            menu.addAction(action)

        menu.addSeparator()

    def selectionModifiers(self):
        """
        @rtype: dict[bool]
        """
        add = False
        deselect = False
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            deselect = True
        elif modifiers == QtCore.Qt.ControlModifier:
            add = True
        return {"add": add, "deselect": deselect}

    def selectSelectionSet(self, record=None, load=False):
        """
        @type record: Record
        """
        namespaces = self.namespaces()

        if record is None:
            record = self

        try:
            record.transferObject().load(namespaces=namespaces, **self.selectionModifiers())
        except mutils.NoMatchFoundError, e:
            if self.window():
                self.window().setError(str(e))
            raise

        if load:
            self.load()

    def contextMenu(self, menu, records):
        """
        @type menu: QtGui.QMenu
        @type records: list[Record]
        """
        self.addSelectContentsAction(menu)
        menu.addSeparator()
        icon = studiolibrary.icon(self.plugin().dirname() + "/images/set.png")
        subMenu = studiolibrary.ContextMenu(menu)
        subMenu.setIcon(icon)
        subMenu.setTitle("Selection Sets")
        self.selectionSetsMenu(subMenu, records)
        menu.addMenu(subMenu)
        menu.addSeparator()
        studiolibrary.Record.contextMenu(self, menu, records)

    def setTransferClass(self, classname):
        """
        @type classname: mutils.TransferObject
        """
        self._transferClass = classname

    def transferClass(self):
        """
        @rtype:
        """
        return self._transferClass

    def transferPath(self):
        """
        @rtype: str
        """
        return os.path.join(self.dirname(), self.transferBasename())

    def transferBasename(self):
        """
        @rtype: str
        """
        return self._transferBasename

    def namespaces(self):
        """
        @rtype: list[str]
        """
        namespaceType = self.plugin().namespaceType()
        if namespaceType == NamespaceType.FromFile:
            return self.namespaceFromFile()
        elif namespaceType == NamespaceType.FromCustom:
            return self.namespaceFromCustom()
        elif namespaceType == NamespaceType.FromSelection:
            return self.namespaceFromSelection()

    def namespaceFromFile(self):
        """
        @rtype: list[str]
        """
        return self.transferObject().namespaces()

    def namespaceFromCustom(self):
        """
        @rtype: list[str]
        """
        return self.plugin().namespaces()

    @staticmethod
    def namespaceFromSelection():
        """
        @rtype: list[str]
        """
        return mutils.getNamespaceFromSelection() or [""]

    def objectCount(self):
        """
        @rtype: int
        """
        if self.transferObject():
            return self.transferObject().count()
        else:
            return 0

    def setTransferBasename(self, transferBasename):
        """
        @rtype: str
        """
        self._transferBasename = transferBasename

    def transferObject(self):
        """
        @rtype: mutils.TransferObject
        """
        if not self._transferObject:
            path = self.transferPath()
            if os.path.exists(path):
                self._transferObject = self.transferClass().createFromPath(path)
        return self._transferObject

    def doubleClicked(self):
        """
        """
        self.load()

    def load(self):
        """
        """
        log.info("Loading: %s" % self.transferPath())
        try:
            objects = maya.cmds.ls(selection=True) or []
            namespaces = self.namespaces()
            self.transferObject().load(objects=objects, namespaces=namespaces)
        except Exception, msg:
            if self.window():
                self.window().setError(str(msg))
            raise

    def validateSaveOptions(self, objects, icon):
        """
        @type objects: list[]
        @type name: str
        @type icon: str
        @raise ValidateError:
        """
        if not icon:
            raise ValidateError("No icon was found. Please create an icon first before saving.")

        if not self.name().strip():
            raise ValidateError("No name specified. Please set a name first before saving.")

        if not objects:
            raise ValidateError("Please select at least one object for saving")

    def save(self, icon=None, objects=None, force=False):
        """
        @raise:
        """
        log.info("Saving: %s" % self.transferPath())
        try:
            tempDir = studiolibrary.TempDir("Transfer", clean=True)

            if objects is None:
                objects = maya.cmds.ls(selection=True) or []

            if not icon:
                icon = tempDir.path() + "/thumbnail.jpg"
                icon = mutils.snapshot(path=icon)

            self.validateSaveOptions(objects=objects, icon=icon)

            transferPath = tempDir.path() + "/" + self.transferBasename()
            t = self.transferClass().createFromObjects(objects)
            t.save(transferPath)

            studiolibrary.Record.save(self, content=[transferPath], icon=icon, force=force)
        except Exception, msg:
            if self.window():
                self.window().setError(str(msg))
            raise


class BaseWidget(QtGui.QWidget):

    def __init__(self, parent=None, record=None):
        """
        @param parent: QtGui.QWidget
        @param record:
        """
        QtGui.QWidget.__init__(self, parent)
        studiolibrary.loadUi(self)

        self._record = record
        self.loadSettings()

        if studiolibrary.isPySide():
            self.layout().setContentsMargins(0, 0, 0, 0)

        if hasattr(self.ui, 'title'):
            self.ui.title.setText(self.record().plugin().name())

        if hasattr(self.ui, 'name'):
            self.ui.name.setText(self.record().name())

        if hasattr(self.ui, 'owner'):
            self.ui.owner.setText(str(self.record().owner()))

        if hasattr(self.ui, 'comment'):
            if isinstance(self.ui.comment, QtGui.QLabel):
                self.ui.comment.setText(self.record().description())
            else:
                self.ui.comment.setPlainText(self.record().description())

        if hasattr(self.ui, "contains"):
            self.updateContains()

        if hasattr(self.ui, 'snapshotButton'):
            self.setSnapshot(self.record().icon())

        ctime = self.record().ctime()
        if hasattr(self.ui, 'created') and ctime:
            self.ui.created.setText(studiolibrary.timeAgo(str(ctime)))

        try:
            self._scriptJob = None
            self._scriptJob = mutils.ScriptJob(e=['SelectionChanged', self.selectionChanged])
            self.selectionChanged()
        except NameError:
            import traceback
            traceback.print_exc()

    def showContextMenu(self, position=None, showApplyButton=True):
        """
        @type position: QPoint
        """
        position = QtGui.QCursor().pos()
        position = self.mapTo(self, position)

        menu = QtGui.QMenu(self)
        self.record().selectionSetsMenu(menu, self.window().selectedRecords(),
                                        includeSelectContents=True, showApplyButton=showApplyButton)
        menu.exec_(position)

    def setSnapshot(self, path):
        """
        @type path: str
        """
        if os.path.exists(path):
            self.ui.snapshotButton.setIcon(QtGui.QIcon(QtGui.QPixmap(path)))
            self.ui.snapshotButton.setIconSize(QtCore.QSize(200, 200))
            self.ui.snapshotButton.setText("")

    def selectionChanged(self):
        """
        """
        pass

    def nameText(self):
        """
        @rtype: str
        """
        return str(self.ui.name.text()).strip()

    def description(self):
        """
        @rtype: str
        """
        return str(self.ui.comment.toPlainText()).strip()

    def record(self):
        """
        @rtype: Record
        """
        return self._record

    def loadSettings(self):
        """
        """
        pass

    def saveSettings(self):
        """
        """
        pass

    def window(self):
        """
        @rtype: QtGui.QWidget
        """
        return self.record().window()

    def plugin(self):
        """
        @rtype: Plugin
        """
        return self.record().plugin()

    def settings(self):
        """
        @rtype: studiolibrary.Settings
        """
        return self.plugin().settings()

    def scriptJob(self):
        """
        @rtype: mutils.ScriptJob
        """
        return self._scriptJob

    def close(self):
        """
        """
        sj = self.scriptJob()
        if sj:
            sj.kill()
        QtGui.QWidget.close(self)

    def updateContains(self, nodes=None):
        """
        @type nodes: list[str]
        """
        if not hasattr(self.ui, "contains"):
            return

        if nodes is None:
            count = self.record().objectCount()
        else:
            count = len(nodes)

        plural = "s" if count > 1 else ""
        self.ui.contains.setText(str(count) + " Object" + plural)


class InfoWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        @param parent: QtGui.QWidget
        @param record:
        """
        BaseWidget.__init__(self, *args, **kwargs)


class PreviewWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent: QtGui.QWidget
        @type record:
        """
        BaseWidget.__init__(self, *args, **kwargs)

        self.connect(self.ui.acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.selectionSetButton, QtCore.SIGNAL("clicked()"), self.showContextMenu)
        self.connect(self.ui.useFileNamespace, QtCore.SIGNAL("clicked()"), self.stateChanged)
        self.connect(self.ui.useCustomNamespace, QtCore.SIGNAL("clicked()"), self.setFromCustomNamespace)
        self.connect(self.ui.useSelectionNamespace, QtCore.SIGNAL("clicked()"), self.stateChanged)
        self.connect(self.ui.namespaceEdit, QtCore.SIGNAL("textEdited (const QString&)"), self.stateChanged)

        self.ui.selectionSetButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.selectionSetButton.customContextMenuRequested.connect(self.showContextMenu)

    def stateChanged(self, state=None):
        """
        @type state: bool
        """
        self.updateNamespaceEdit()
        self.saveSettings()

    def loadSettings(self):
        """
        """
        namespaces = self.plugin().namespaces()
        namespaces = studiolibrary.listToString(namespaces)
        namespaceType = self.plugin().namespaceType()

        self.ui.namespaceEdit.setText(namespaces)
        if namespaceType == NamespaceType.FromFile:
            self.ui.useFileNamespace.setChecked(True)
        elif namespaceType == NamespaceType.FromCustom:
            self.ui.useCustomNamespace.setChecked(True)
        else:
            self.ui.useSelectionNamespace.setChecked(True)

    def saveSettings(self):
        """
        """
        if self.ui.useFileNamespace.isChecked():
            self.plugin().setNamespaceType(NamespaceType.FromFile)
        elif self.ui.useCustomNamespace.isChecked():
            self.plugin().setNamespaceType(NamespaceType.FromCustom)
        else:
            self.plugin().setNamespaceType(NamespaceType.FromSelection)

        namespaces = str(self.ui.namespaceEdit.text())
        self.plugin().setNamespaces(namespaces)

    def namespaces(self):
        """
        @rtype:
        """
        return studiolibrary.stringToList(str(self.ui.namespaceEdit.text()))

    def selectionChanged(self):
        """
        """
        self.stateChanged()

    def updateNamespaceEdit(self):
        """
        """
        namespaces = None

        if self.ui.useSelectionNamespace.isChecked():
            namespaces = mutils.getNamespaceFromSelection()
        elif self.ui.useFileNamespace.isChecked():
            namespaces = self.record().transferObject().namespaces()

        if not self.ui.useCustomNamespace.isChecked():
            self.ui.namespaceEdit.setEnabled(False)
            self.ui.namespaceEdit.setText(studiolibrary.listToString(namespaces))
        else:
            self.ui.namespaceEdit.setEnabled(True)

    def setFromCustomNamespace(self, value=None):
        """
        @type value:
        """
        self.stateChanged(value)
        if self.ui.useCustomNamespace.isChecked():
            self.ui.namespaceEdit.setFocus()

    def accept(self):
        """
        """
        self.record().load()


class CreateWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        @param parent: QtGui.QWidget
        @param record:
        """
        BaseWidget.__init__(self, *args, **kwargs)

        self._thumbnail = None
        self._focusWidget = None

        self.connect(self.ui.acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.snapshotButton, QtCore.SIGNAL("clicked()"), self.snapshot)
        self.connect(self.ui.selectionSetButton, QtCore.SIGNAL("clicked()"), self.showContextMenu)

        self.ui.selectionSetButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.selectionSetButton.customContextMenuRequested.connect(self.showContextMenu)

        #modelPanelName = "modelPanelCreateWidget"
        #if maya.cmds.modelPanel(modelPanelName, exists=True, query=True):
        #    maya.cmds.deleteUI(modelPanelName, panel=True)

        #self._modelPanel = mutils.modelpanelwidget.ModelPanelWidget(self, modelPanelName)
        #self._modelPanel.setFixedWidth(160)
        #self._modelPanel.setFixedHeight(160)
        #self.ui.modelPanelLayout.insertWidget(0, self._modelPanel)
        #self.ui.snapshotButton.hide()

    def thumbnail(self):
        """
        @rtype str
        """
        return self._thumbnail

    def selectionChanged(self):
        """
        """
        selection = maya.cmds.ls(selection=True) or []
        self.updateContains(selection)

    def modelPanel(self):
        """
        @return: mutils.ModelPanelWidget
        """
        return self._modelPanel

    def snapshot(self):
        tempDir = studiolibrary.TempDir(makedirs=True)
        self._thumbnail = tempDir.path() + "/thumbnail.jpg"
        try:
            self._thumbnail = mutils.snapshot(path=self._thumbnail)
            self.setSnapshot(self._thumbnail)
        except Exception, e:
            if self.record().window():
                self.record().window().setError(str(e))
            raise

    #def playblast(self, path, start=None, end=None):
    #    """
    #    """
    #    return mutils.playblast(path, self.modelPanel().name(), start=start, end=end)
    #    #playblast(path, modelPanel, start, end, frame, width, height):

    def accept(self):
        """
        @raise:
        """
        #iconPath = self.playblast()
        self.record().setName(self.nameText())
        self.record().setDescription(self.description())
        self.record().save(icon=self._thumbnail)


class OptionAction(QtGui.QWidgetAction):

    def __init__(self, parent, label, callback1, callback2=None):
        """
        @param parent:
        @param label:
        @param callback1:
        @param callback2:
        """
        QtGui.QWidgetAction.__init__(self, parent)
        self._label = label
        self.setText(label)
        self._callback1 = callback1
        self._callback2 = callback2

    def createWidget(self, parent):
        """
        @param parent:
        @rtype
        """
        myWidget = QtGui.QFrame(parent)
        myWidget.setObjectName("mainWidget")

        myLabel = ExtendedLabel(self._label, parent)
        myLabel.setObjectName('myLabel')

        myIcon = ExtendedLabel("Apply", parent)
        myIcon.setObjectName('myOption')

        myLayout = QtGui.QHBoxLayout(myWidget)
        myLayout.setSpacing(0)
        myLayout.setContentsMargins(0, 0, 0, 0)
        myLayout.addWidget(myLabel, stretch=1)
        myLayout.addWidget(myIcon, stretch=0)

        trigger = partial(self.triggerCallback, self)
        myLabel.connect(myLabel, QtCore.SIGNAL("clicked"), trigger)
        if self._callback1:
            myLabel.connect(myLabel, QtCore.SIGNAL("clicked"), self._callback1)

        if self._callback2 is not None:
            trigger2 = partial(self.triggerCallback, self)
            myIcon.connect(myIcon, QtCore.SIGNAL("clicked"), trigger2)
            myIcon.connect(myIcon, QtCore.SIGNAL("clicked"), self._callback2)
        else:
            myIcon.hide()

        return myWidget

    @staticmethod
    def triggerCallback(action):
        """
        @param action:
        """
        action.trigger()
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Escape, QtCore.Qt.NoModifier)
        if isinstance(action.parent().parent(), QtGui.QMenu):
            QtCore.QCoreApplication.postEvent(action.parent().parent(), event)
        else:
            QtCore.QCoreApplication.postEvent(action.parent(), event)


class ExtendedLabel(QtGui.QLabel):

    def __init__(self, *args, **kwargs):
        """
        @param args:
        @param kwargs:
        """
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setFixedHeight(20)

    def mouseReleaseEvent(self, ev):
        """
        @param ev:
        """
        self.emit(QtCore.SIGNAL('clicked'))


if __name__ == "__main__":
    import studiolibrary
    studiolibrary.main()