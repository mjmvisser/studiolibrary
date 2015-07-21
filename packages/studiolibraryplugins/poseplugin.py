#!/usr/bin/python
"""
"""
import os
import math
import maya.cmds
import mutils
import mayabaseplugin

try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore


class Plugin(mayabaseplugin.Plugin):

    def __init__(self, parent):
        """
        @type parent:
        """
        mayabaseplugin.Plugin.__init__(self, parent)

        self.setName("Pose")
        self.setIcon(self.dirname() + "/images/pose.png")

        self.setRecord(Record)
        self.setInfoWidget(PoseInfoWidget)
        self.setCreateWidget(PoseCreateWidget)
        self.setPreviewWidget(PosePreviewWidget)

    def setKeyOption(self, enable):
        """
        @type enable: bool
        """
        self.settings().set("keyOption", enable)

    def keyOption(self):
        """
        @rtype: bool
        """
        return self.settings().get("keyOption", False)

    def setMirrorOption(self, enable):
        """
        @type enable: bool
        """
        self.settings().set("mirrorOption", enable)

    def mirrorOption(self):
        """
        @rtype: bool
        """
        return self.settings().get("mirrorOption", False)


class Record(mayabaseplugin.Record):

    def __init__(self, *args, **kwargs):
        """
        @type args:
        @type kwargs:
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)

        self._selection = []
        self._namespaces = None
        self._mirror = None
        self._isLoading = False
        self._mirrorTable = None
        self._autoKeyFrame = None
        self._mousePosition = None
        self._currentBlendValue = 0.0
        self._previousBlendValue = 0.0

        self.setTransferClass(mutils.Pose)
        self.setTransferBasename("pose.dict")
        if not os.path.exists(self.transferPath()):
            self.setTransferBasename("pose.json")

    @classmethod
    def createFromPath(cls, path, plugin="studiolibraryplugins.poseplugin"):
        """
        @type path: str
        @rtype: Record
        """
        import studiolibrary

        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        folder = studiolibrary.Folder(dirname)
        plugin = studiolibrary.loadPlugin(plugin)

        r = cls(folder=folder)
        r.setName(basename)
        r.setPlugin(plugin)
        return r

    def isLoading(self):
        """
        @rtype: bool
        """
        return self._isLoading

    def mirrorTable(self):
        """
        @rtype: mutils.MirrorTable
        """
        paths = self.mirrorTables()
        if paths:
            path = paths[0] + "/mirrortable.json"
            return mutils.MirrorTable.createFromPath(path)

    def isBlending(self):
        """
        @rtype: bool
        """
        return self.mousePosition() is not None

    def currentBlendValue(self):
        """
        @rtype: float
        """
        return self._currentBlendValue

    def previousBlendValue(self):
        """
        @rtype: float
        """
        return self._previousBlendValue

    def toggleMirror(self):
        """
        """
        mirror = self.plugin().mirrorOption()
        mirror = False if mirror else True
        self.plugin().setMirrorOption(mirror)
        self.plugin().emit(QtCore.SIGNAL("updateMirror(bool)"), bool(mirror))

    def keyPressEvent(self, event):
        """
        @type event:
        """
        mayabaseplugin.Record.keyPressEvent(self, event)
        if not event.isAutoRepeat():
            if event.key() == QtCore.Qt.Key_M:
                self.toggleMirror()
                self._load(blend=self.currentBlendValue(), refresh=True, mirror=self._mirror)

    def mousePosition(self):
        """
        @rtype:
        """
        return self._mousePosition

    def mousePressEvent(self, event):
        """
        @type event:
        """
        mayabaseplugin.Record.mousePressEvent(self, event)
        if event.button() == QtCore.Qt.MidButton:
            self.beforeLoad(clear=True)
            self._mousePosition = event.pos()

    def mouseMoveEvent(self, event):
        """
        @type event:
        """
        mayabaseplugin.Record.mouseMoveEvent(self, event)
        if self.isBlending():
            value = (event.pos().x() - self.mousePosition().x()) / 1.5
            value = math.ceil(value) + self.previousBlendValue()
            self._load(blend=value, key=False)

    def mouseReleaseEvent(self, event):
        """
        @type event:
        """
        if self.isBlending():
            try:
                self._load(blend=self.currentBlendValue(), refresh=False, mirror=self._mirror)
            finally:
                self.afterLoad()
        mayabaseplugin.Record.mouseReleaseEvent(self, event)

    def selectionChanged(self, *args, **kwargs):
        """
        @type args:
        """
        self._mousePosition = None
        self._transferObject = None
        self._currentBlendValue = 0.0
        self._previousBlendValue = 0.0
        self.plugin().emit(QtCore.SIGNAL("updateBlend(int)"), int(0.0))

    def beforeLoad(self, clear=False):
        """
        @type clear: bool
        """
        if self._isLoading:
            return

        maya.cmds.undoInfo(openChunk=True)

        self._isLoading = True
        self._namespaces = self.namespaces()
        self._mirrorTable = self.mirrorTable()
        self._selection = maya.cmds.ls(selection=True) or []
        self._autoKeyFrame = maya.cmds.autoKeyframe(query=True, state=True)

        maya.cmds.autoKeyframe(edit=True, state=False)
        maya.cmds.select(clear=clear)

    def afterLoad(self):
        """
        """
        if not self._isLoading:
            return

        self._mirror = None
        self._isLoading = False
        self._mirrorTable = False
        self._mousePosition = None
        self._previousBlendValue = self._currentBlendValue

        if self._selection:
            maya.cmds.select(self._selection)
        maya.cmds.autoKeyframe(edit=True, state=self._autoKeyFrame)
        maya.cmds.undoInfo(closeChunk=True)

    def load(self, objects=None, namespaces=None, blend=100.0, key=None, refresh=False, mirror=None,
             mirrorTable=None):
        """
        @type objects: list[str]
        @type blend: float
        @type key: bool | None
        @type namespaces: str | None
        @type refresh: bool | None
        @type mirror: bool | None
        @type mirrorTable: mutils.MirrorTable
        """
        self.beforeLoad()
        try:
            self._load(objects=objects, namespaces=namespaces, blend=blend, key=key, refresh=refresh, mirror=mirror,
                       mirrorTable=mirrorTable)
        finally:
            self.afterLoad()

    def _load(self, objects=None, namespaces=None, blend=None, key=None, refresh=True, attrs=None,
              mirror=None, mirrorTable=None):
        """
        @type objects: list[str]
        @type blend: float
        @type key: bool | None
        @type namespaces: str | None
        @type refresh: bool | None
        @type mirror: bool | None
        @type mirrorTable: mutils.MirrorTable
        """
        if not self._isLoading:
            return

        self._currentBlendValue = blend

        try:
            if self.isBlending():
                self.window().showMessage("Blend: %s%%" % str(blend))

            if key is None:
                key = self.plugin().keyOption()

            if mirror is None:
                mirror = self.plugin().mirrorOption()

            if mirrorTable is None:
                mirrorTable = self.mirrorTable()
                if mirrorTable is None:
                    mirror = None

            if objects is None:
                objects = self._selection

            if namespaces is None:
                namespaces = self._namespaces

            self.plugin().emit(QtCore.SIGNAL("updateBlend(int)"), int(blend))
            self.transferObject().load(objects, namespaces=namespaces, attrs=attrs, blend=blend,
                                       mirror=mirror, key=key, refresh=refresh, mirrorTable=mirrorTable)

        except Exception, msg:
            self.afterLoad()
            if self.window():
                self.window().setError(str(msg))
            raise


class PoseInfoWidget(mayabaseplugin.InfoWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent:
        @type record:
        """
        mayabaseplugin.InfoWidget.__init__(self, *args, **kwargs)


class PoseCreateWidget(mayabaseplugin.CreateWidget):
    def __init__(self, *args, **kwargs):
        """
        @type parent:
        @type record:
        """
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)


class PosePreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent:
        @type record: Record
        """
        mayabaseplugin.PreviewWidget.__init__(self, *args, **kwargs)

        self.connect(self.ui.keyCheckBox, QtCore.SIGNAL("clicked()"), self.stateChanged)
        self.connect(self.ui.mirrorCheckBox, QtCore.SIGNAL("clicked()"), self.stateChanged)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderMoved(int)"), self.sliderMoved)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderPressed()"), self.sliderPressed)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderReleased()"), self.sliderReleased)
        self.plugin().connect(self.plugin(), QtCore.SIGNAL("updateBlend(int)"), self.updateSlider)
        self.plugin().connect(self.plugin(), QtCore.SIGNAL("updateMirror(bool)"), self.updateMirror)
        # self.updateSlider(self.record().currentBlendValue())
        # self._sliderPressed = False

        # Mirror check box
        mirrorTip = "Cannot find mirror table!"
        mirrorTable = self.record().mirrorTable()
        if mirrorTable:
            mirrorTip = "Using mirror table: %s" % mirrorTable.path()

        self.ui.mirrorCheckBox.setToolTip(mirrorTip)
        self.ui.mirrorCheckBox.setEnabled(mirrorTable is not None)

    def updateMirror(self, mirror):
        """
        @type mirror: bool
        """
        if mirror:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Unchecked)

    def loadSettings(self):
        """
        """
        mayabaseplugin.PreviewWidget.loadSettings(self)

        key = self.plugin().keyOption()
        mirror = self.plugin().mirrorOption()

        self.ui.keyCheckBox.setChecked(key)
        self.ui.mirrorCheckBox.setChecked(mirror)

    def saveSettings(self):
        """
        """
        key = bool(self.ui.keyCheckBox.isChecked())
        mirror = bool(self.ui.mirrorCheckBox.isChecked())

        self.plugin().setKeyOption(key)
        self.plugin().setMirrorOption(mirror)

        mayabaseplugin.PreviewWidget.saveSettings(self)

    def updateSlider(self, value):
        """
        @type value: int
        """
        self.ui.blendSlider.setValue(value)

    def sliderPressed(self):
        """
        """
        self.record().beforeLoad(clear=True)

    def sliderReleased(self):
        """
        """
        key = self.ui.keyCheckBox.isChecked()
        blend = self.ui.blendSlider.value()
        try:
            self.record()._load(blend=blend, refresh=False, key=key)
        finally:
            self.record().afterLoad()

    def sliderMoved(self, value):
        """
        @type value: float
        """
        self.record()._load(blend=value, key=False)
