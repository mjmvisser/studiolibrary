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

"""
#---------------------------------------------------------------------------
# Saving a pose record
#---------------------------------------------------------------------------

from studiolibraryplugins import poseplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []

record = poseplugin.Record(path)
record.save(objects=objects)

#---------------------------------------------------------------------------
# Loading a pose record
#---------------------------------------------------------------------------

from studiolibraryplugins import poseplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

record = poseplugin.Record(path)
record.load(objects=objects, namespaces=namespaces, key=True, mirror=False)
"""

import os
import math
import logging

from PySide import QtCore

import studiolibrary
import studiolibraryplugins

from studiolibraryplugins import mayabaseplugin

try:
    import mutils
    import maya.cmds
except ImportError, msg:
    print msg


logger = logging.getLogger(__name__)


class Plugin(mayabaseplugin.Plugin):

    @staticmethod
    def settings():
        """
        :rtype: studiolibrary.Settings
        """
        return studiolibrary.Settings.instance("Plugin", "Pose")

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        mayabaseplugin.Plugin.__init__(self, library)

        iconPath = studiolibraryplugins.resource().get("icons", "pose.png")

        self.setName("Pose")
        self.setIconPath(iconPath)

    def record(self, path=None):
        """
        :type path: str or None
        :rtype: Record
        """
        return Record(path=path, plugin=self)

    def infoWidget(self, parent, record):
        """
        :type parent: QtGui.QWidget
        :type record: Record
        :rtype: PoseInfoWidget
        """
        return PoseInfoWidget(parent=parent, record=record)

    def createWidget(self, parent):
        """
        :type parent: QtGui.QWidget
        :rtype: PoseCreateWidget
        """
        record = self.record()
        return PoseCreateWidget(parent=parent, record=record)

    def previewWidget(self, parent, record):
        """
        :type parent: QtGui.QWidget
        :rtype: PosePreviewWidget
        """
        return PosePreviewWidget(parent=parent, record=record)


class PoseSignal(QtCore.QObject):
    """"""
    onBlendUpdated = QtCore.Signal(int)
    onMirrorUpdated = QtCore.Signal(bool)


class Record(mayabaseplugin.Record):

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)

        self.poseSignals = PoseSignal()
        self.onBlendUpdated = self.poseSignals.onBlendUpdated
        self.onMirrorUpdated = self.poseSignals.onMirrorUpdated

        self._options = None
        self._isLoading = False
        self._autoKeyFrame = None
        self._mousePosition = None
        self._currentBlendValue = 0.0
        self._previousBlendValue = 0.0

        self.setTransferClass(mutils.Pose)
        self.setTransferBasename("pose.dict")
        if not os.path.exists(self.transferPath()):
            self.setTransferBasename("pose.json")

    def settings(self):
        """
        :rtype: studiolibrary.Settings
        """
        return Plugin.settings()

    def isLoading(self):
        """
        :rtype: bool
        """
        return self._isLoading

    def mirrorTable(self):
        """
        :rtype: mutils.MirrorTable
        """
        paths = self.mirrorTables()
        if paths:
            path = paths[0] + "/mirrortable.json"
            return mutils.MirrorTable.fromPath(path)

    def isBlending(self):
        """
        :rtype: bool | None
        """
        return self.mousePosition() is not None

    def currentBlendValue(self):
        """
        :rtype: float
        """
        return self._currentBlendValue

    def previousBlendValue(self):
        """
        :rtype: float
        """
        return self._previousBlendValue

    def mirrorEnabled(self):
        """
        :rtype: bool
        """
        return self.settings().get("mirrorEnabled", False)

    def setMirrorEnabled(self, value):
        """
        :type value: bool
        """
        self.settings().set("mirrorEnabled", value)
        self.onMirrorUpdated.emit(bool(value))

    def keyEnabled(self):
        """
        :rtype: bool
        """
        return self.settings().get("keyEnabled", False)

    def setKeyEnabled(self, value):
        """
        :type value: bool
        """
        self.settings().set("keyEnabled", value)

    def toggleMirror(self):
        """
        :rtype: None
        """
        mirror = self.mirrorEnabled()
        mirror = False if mirror else True
        self.setMirrorEnabled(mirror)

    def keyPressEvent(self, event):
        """
        :type event: QtGui.QEvent
        """
        mayabaseplugin.Record.keyPressEvent(self, event)

        if not event.isAutoRepeat():
            if event.key() == QtCore.Qt.Key_M:

                self.toggleMirror()
                blend = self.currentBlendValue()
                mirror = self.mirrorEnabled()

                if self.isBlending():
                    self.loadFromSettings(
                        blend=blend,
                        mirror=mirror,
                        batchMode=True,
                        showBlendMessage=True
                    )
                else:
                    self.loadFromSettings(
                        blend=blend,
                        refresh=True,
                        mirror=mirror
                    )

    def mousePosition(self):
        """
        :rtype: QtGui.QPoint
        """
        return self._mousePosition

    def mousePressEvent(self, event):
        """
        :type event: QtCore.QEvent
        """
        mayabaseplugin.Record.mousePressEvent(self, event)
        if event.button() == QtCore.Qt.MidButton:
            self._mousePosition = event.pos()
            blend = self.previousBlendValue()
            self.loadFromSettings(
                blend=blend,
                batchMode=True,
                showBlendMessage=True
            )

    def mouseMoveEvent(self, event):
        """
        :type event: QtCore.QEvent
        """
        mayabaseplugin.Record.mouseMoveEvent(self, event)
        if self.isBlending():
            value = (event.pos().x() - self.mousePosition().x()) / 1.5
            value = math.ceil(value) + self.previousBlendValue()
            self.loadFromSettings(blend=value, batchMode=True,
                                  showBlendMessage=True)

    def mouseReleaseEvent(self, event):
        """
        :type event: QtCore.QEvent
        """
        if self.isBlending():
            blend = self.currentBlendValue()
            self.loadFromSettings(blend=blend, refresh=False)
        mayabaseplugin.Record.mouseReleaseEvent(self, event)

    def itemSelectionChanged(self, *args, **kwargs):
        """
        :rtype: None
        """
        self._mousePosition = None
        self._transferObject = None
        self._previousBlendValue = 0.0
        self.onBlendUpdated.emit(int(0.0))

    def beforeLoad(self):
        """
        :rtype: None
        """
        if self._isLoading:
            return

        logger.info('Loading Record "{0}"'.format(self.path()))

        self._isLoading = True

    def afterLoad(self):
        """
        :rtype: None
        """
        if not self._isLoading:
            return

        self._isLoading = False
        self._options = None
        self._mousePosition = None
        self._previousBlendValue = self._currentBlendValue

        logger.info('Loaded Record "{0}"'.format(self.path()))

    def doubleClicked(self):
        """
        :return: None
        """
        self.loadFromSettings(clearSelection=False)

    def loadFromSettings(self, blend=100.0, refresh=True, showBlendMessage=False,
                         batchMode=False, clearSelection=True, mirror=None):
        """
        :type blend: float
        :type refresh: bool
        :type batchMode: bool
        :type clearSelection: bool
        :type showBlendMessage: bool
        """
        if self._options is None:
            self._options = dict()
            self._options["key"] = self.keyEnabled()
            self._options['mirror'] = self.mirrorEnabled()
            self._options['namespaces'] = self.namespaces()
            self._options['mirrorTable'] = self.mirrorTable()
            self._options['objects'] = maya.cmds.ls(selection=True) or []

        if mirror is not None:
            self._options['mirror'] = mirror

        self.onBlendUpdated.emit(int(blend))

        try:
            self.load(
                blend=blend,
                refresh=refresh,
                batchMode=batchMode,
                clearSelection=clearSelection,
                showBlendMessage=showBlendMessage,
                **self._options
            )
        except Exception, msg:
            self.showErrorDialog(msg)
            raise

    def load(self, objects=None, namespaces=None, blend=100.0, key=None,
             refresh=True, attrs=None, mirror=None, mirrorTable=None,
             showBlendMessage=False, clearSelection=False, batchMode=False):
        """
        :type objects: list[str]
        :type blend: float
        :type key: bool | None
        :type namespaces: list[str] | None
        :type refresh: bool | None
        :type mirror: bool | None
        :type batchMode: bool
        :type showBlendMessage: bool
        :type mirrorTable: mutils.MirrorTable
        """
        logger.debug("Loading pose '%s'" % self.path())

        self._currentBlendValue = blend

        if showBlendMessage and self.listWidget():
            self.listWidget().showMessage("Blend: %s%%" % str(blend))

        self.beforeLoad()
        try:
            mayabaseplugin.Record.load(self, objects=objects, namespaces=namespaces, blend=blend,
                                       mirror=mirror, key=key, refresh=refresh, attrs=attrs,
                                       mirrorTable=mirrorTable, clearSelection=clearSelection,
                                       batchMode=batchMode)
        except Exception:
            self.afterLoad()
            raise

        finally:
            if not batchMode:
                self.afterLoad()

        logger.debug("Loaded pose '%s'" % self.path())


class PoseInfoWidget(mayabaseplugin.InfoWidget):

    def __init__(self, *args, **kwargs):
        """"""
        mayabaseplugin.InfoWidget.__init__(self, *args, **kwargs)


class PoseCreateWidget(mayabaseplugin.CreateWidget):
    def __init__(self, *args, **kwargs):
        """"""
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)


class PosePreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :rtype: None
        """
        mayabaseplugin.PreviewWidget.__init__(self, *args, **kwargs)

        self.connect(self.ui.keyCheckBox, QtCore.SIGNAL("clicked()"), self.updateState)
        self.connect(self.ui.mirrorCheckBox, QtCore.SIGNAL("clicked()"), self.updateState)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderMoved(int)"), self.sliderMoved)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderReleased()"), self.sliderReleased)

        self.record().onBlendUpdated.connect(self.updateSlider)
        self.record().onMirrorUpdated.connect(self.updateMirror)

    def setRecord(self, record):
        """
        :type record: Record
        :rtype: None
        """
        mayabaseplugin.PreviewWidget.setRecord(self, record)

        # Mirror check box
        mirrorTip = "Cannot find mirror table!"
        mirrorTable = record.mirrorTable()
        if mirrorTable:
            mirrorTip = "Using mirror table: %s" % mirrorTable.path()

        self.ui.mirrorCheckBox.setToolTip(mirrorTip)
        self.ui.mirrorCheckBox.setEnabled(mirrorTable is not None)

    def updateMirror(self, mirror):
        """
        :type mirror: bool
        """
        if mirror:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Unchecked)

    def setState(self, state):
        """
        :rtype: None
        """
        key = state.get("keyEnabled", False)
        mirror = state.get("mirrorEnabled", False)

        self.ui.keyCheckBox.setChecked(key)
        self.ui.mirrorCheckBox.setChecked(mirror)

        super(PosePreviewWidget, self).setState(state)

    def state(self):
        """
        :rtype: None
        """
        state = super(PosePreviewWidget, self).state()

        key = bool(self.ui.keyCheckBox.isChecked())
        mirror = bool(self.ui.mirrorCheckBox.isChecked())

        state["keyEnabled"] = key
        state["mirrorEnabled"] = mirror

        return state

    def updateSlider(self, value):
        """
        :type value: int
        """
        self.ui.blendSlider.setValue(value)

    def sliderReleased(self):
        """
        :rtype: None
        """
        blend = self.ui.blendSlider.value()
        self.record().loadFromSettings(blend=blend, refresh=False,
                                       showBlendMessage=True)

    def sliderMoved(self, value):
        """
        :type value: float
        """
        self.record().loadFromSettings(blend=value, batchMode=True,
                                       showBlendMessage=True)

    def accept(self):
        """
        :rtype: None
        """
        self.record().loadFromSettings(clearSelection=False)
