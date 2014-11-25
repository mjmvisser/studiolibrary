#Embedded file name: C:/Users/hovel/Dropbox/packages/studioLibrary/1.5.8/build27/studioLibrary\plugins\posePlugin.py
"""
# Released subject to the BSD License
# Please visit http://www.voidspace.org.uk/python/license.shtml
#
# Copyright (c) 2014, Kurt Rathjen
# All rights reserved.
# Comments, suggestions and bug reports are welcome.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
   # * Redistributions of source code must retain the above copyright
   #   notice, this list of conditions and the following disclaimer.
   # * Redistributions in binary form must reproduce the above copyright
   # notice, this list of conditions and the following disclaimer in the
   # documentation and/or other materials provided with the distribution.
   # * Neither the name of Kurt Rathjen nor the
   # names of its contributors may be used to endorse or promote products
   # derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY KURT RATHJEN ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL KURT RATHJEN BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""
import math
try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore

try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()

import os
import mutils
import studioLibrary
import studioLibrary.plugins.mayaBasePlugin as mayaBasePlugin

class PosePluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class Plugin(mayaBasePlugin.Plugin):

    def __init__(self, parent):
        """
        :param parent:
        """
        studioLibrary.Plugin.__init__(self, parent)
        self.setName('Pose')
        self.setIcon(self.dirname() + '/images/pose.png')
        self.setRecord(Record)
        self.setInfoWidget(PoseInfoWidget)
        self.setCreateWidget(PoseCreateWidget)
        self.setPreviewWidget(PosePreviewWidget)

    def mirrorTableText(self):
        path = self.mirrorTablePath()
        mirrorTables = self.mirrorTables()
        for name in mirrorTables:
            if path == mirrorTables[name]:
                return name

    def setMirrorOption(self, enable):
        s = self.settings()
        s.set('mirrorOption', enable)
        s.save()

    def mirrorOption(self):
        return self.settings().get('mirrorOption', False)


class Record(mayaBasePlugin.Record):

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        """
        mayaBasePlugin.Record.__init__(self, *args, **kwargs)
        self._value = 0.0
        self._blend = 0.0
        self._mpos = None
        self._attrs = None
        self._settings = None
        self._selection = []
        self._namespaces = None
        self._transferObject = None
        self._mirror = None
        self._mirrorTable = None
        self._autoKeyFrame = None

    def transferPath(self):
        path = self.dirname() + '/pose.json'
        if not os.path.exists(path):
            path = self.dirname() + '/pose.dict'
        return path

    def transferObject(self):
        if self._transferObject is None:
            self._transferObject = mutils.Pose.createFromPath(self.transferPath())
        return self._transferObject

    def mirrorTable(self):
        """
        @rtype: mutils.MirrorTable
        """
        paths = self.plugin().mirrorTables(self)
        if paths:
            path = paths[0] + '/mirrortable.json'
            return mutils.MirrorTable.createFromPath(path)

    def isBlending(self):
        """
        @rtype: bool
        """
        if self._mpos:
            return True
        return False

    def value(self):
        return self._value

    def prettyPrint(self):
        """
        """
        print '# ------ %s ------' % self.name()
        print self.transferObject().dump()
        print '# ----------------\n'

    def doubleClicked(self):
        """
        """
        self.apply()

    def clearCache(self):
        """
        """
        self._blend = 0.0
        self._value = 0.0
        self._transferObject = None
        self.plugin().emit(QtCore.SIGNAL('updateBlend(int)'), int(0.0))

    def beforeLoad(self, clear = False):
        """
        @type clear: bool
        """
        maya.cmds.undoInfo(openChunk=True)
        self._namespaces = self.namespaces()
        self._attrs = None
        self._settings = self.plugin().settings()
        if self._mirror is None:
            self._mirror = self._settings.get('mirror', False)
        self._mirrorTable = self.mirrorTable()
        self._selection = maya.cmds.ls(selection=True) or []
        self._autoKeyFrame = maya.cmds.autoKeyframe(query=True, state=True)
        maya.cmds.autoKeyframe(edit=True, state=False)
        maya.cmds.select(clear=clear)

    def afterLoad(self):
        """
        """
        self._mpos = None
        self._blend = self._value
        self._mirror = None
        self._mirrorTable = False
        if self._selection:
            maya.cmds.select(self._selection)
        maya.cmds.autoKeyframe(edit=True, state=self._autoKeyFrame)
        maya.cmds.undoInfo(closeChunk=True)

    def applyBlend(self, blend, key = False, refresh = True):
        """
        @type key: bool
        @type blend: float
        @type refresh: bool
        """
        try:
            if studioLibrary.isControlModifier():
                blend = int(math.ceil(blend / 10.0)) * 10
            if self._blend != blend:
                self.window().showMessage('Blend: %s%%' % str(blend))
                self.apply(blend=blend, settings=self._settings, key=key, refresh=refresh, mirror=self._mirror)
        except Exception:
            self.afterLoad()

    def keyPressEvent(self, event):
        """
        @param event:
        """
        mayaBasePlugin.Record.keyPressEvent(self, event)
        if not event.isAutoRepeat():
            if event.key() == QtCore.Qt.Key_M:
                self.toggleMirror()

    def toggleMirror(self):
        """
        """
        self._mirror = False if self._mirror else True
        self.apply(blend=self._value, settings=self._settings, refresh=True, mirror=self._mirror)
        self.plugin().emit(QtCore.SIGNAL('updateMirror(bool)'), bool(self._mirror))

    def mousePressEvent(self, event):
        """
        @type event:
        """
        studioLibrary.Record.mousePressEvent(self, event)
        if event.button() == QtCore.Qt.MidButton:
            self.beforeLoad(clear=True)
            self._mpos = event.pos()

    def mouseMoveEvent(self, event):
        """
        @type event:
        """
        studioLibrary.Record.mouseMoveEvent(self, event)
        if self.isBlending():
            value = (event.pos().x() - self._mpos.x()) / 1.5
            value = math.ceil(value) + self._blend
            self.applyBlend(value)

    def mouseReleaseEvent(self, event):
        """
        @type event: 
        """
        if self.isBlending():
            try:
                self.apply(blend=self._value, settings=self._settings, refresh=False, mirror=self._mirror)
            finally:
                self.afterLoad()

        studioLibrary.Record.mouseReleaseEvent(self, event)

    def selectionChanged(self, *args):
        """
        @type args: 
        """
        self.clearCache()

    def apply(self, objects = None, namespaces = None, blend = None, settings = None, key = None, refresh = True, mirror = None, mirrorTable = None):
        """
        @type objects:
        @type namespaces: 
        @type blend: 
        @type settings: 
        @type key: 
        @type refresh: 
        @raise PosePluginError:
        """
        msg = 'An error has occurred while saving the pose! Please check the script editor for the traceback.'
        runAfterLoad = False
        if blend is None:
            runAfterLoad = True
            self.beforeLoad()
            blend = 100.0
        self._value = blend
        try:
            if mirrorTable is None:
                mirrorTable = self.mirrorTable()
            if settings is None:
                settings = self.plugin().settings()
            if key is None:
                key = settings.get('key', True)
            if mirror is None:
                mirror = settings.get('mirror', False)
            if objects is None:
                objects = self._selection
            if namespaces is None:
                namespaces = self._namespaces
            try:
                self.plugin().emit(QtCore.SIGNAL('updateBlend(int)'), int(blend))
                self.transferObject().load(objects, namespaces=namespaces, attrs=self._attrs, blend=blend, mirror=mirror, key=key, refresh=refresh, mirrorTable=mirrorTable)
            except mutils.NoMatchFoundError:
                msg = 'Cannot find any objects that match!'
                raise PosePluginError(msg)

        except Exception:
            import traceback
            traceback.print_exc()
            self.window().setError(msg)
            raise
        finally:
            if runAfterLoad:
                self.afterLoad()


class PoseInfoWidget(mayaBasePlugin.InfoWidget):

    def __init__(self, parent = None, record = None):
        """
        @type parent:
        @type record:
        """
        mayaBasePlugin.InfoWidget.__init__(self, parent, record)
        self.window().setFocusPolicy(QtCore.Qt.StrongFocus)


class PosePreviewWidget(mayaBasePlugin.PreviewWidget):

    def __init__(self, parent = None, record = None):
        """
        @type parent: 
        @type record: Record
        """
        mayaBasePlugin.PreviewWidget.__init__(self, parent, record)
        self.connect(self.ui.keyCheckBox, QtCore.SIGNAL('clicked()'), self.stateChanged)
        self.connect(self.ui.mirrorCheckBox, QtCore.SIGNAL('clicked()'), self.stateChanged)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL('sliderMoved(int)'), self.sliderMoved)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL('sliderPressed()'), self.sliderPressed)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL('sliderReleased()'), self.sliderReleased)
        self.record().plugin().connect(self.record().plugin(), QtCore.SIGNAL('updateBlend(int)'), self.updateSlider)
        self.record().plugin().connect(self.record().plugin(), QtCore.SIGNAL('updateMirror(bool)'), self.updateMirror)
        self.updateSlider(self.record().value())
        mirrorTip = 'Cannot find mirror table!'
        mirrorEnable = False
        mirrorTable = self.record().mirrorTable()
        if mirrorTable:
            mirrorTip = 'Using mirror table: %s' % mirrorTable.path()
            mirrorEnable = True
        self.ui.mirrorCheckBox.setToolTip(mirrorTip)
        self.ui.mirrorCheckBox.setEnabled(mirrorEnable)

    def updateMirror(self, mirror):
        """
        @type mirror:
        """
        if mirror:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Unchecked)

    def updateSlider(self, blend):
        """
        @type blend: int
        """
        self.ui.blendSlider.setValue(blend)

    def loadSettings(self):
        """
        """
        super(PosePreviewWidget, self).loadSettings()
        s = self.settings()
        key = s.get('key', True)
        mirror = s.get('mirror', False)
        self.ui.keyCheckBox.setChecked(key)
        self.ui.mirrorCheckBox.setChecked(mirror)

    def saveSettings(self):
        """
        """
        super(PosePreviewWidget, self).saveSettings()
        s = self.settings()
        s.set('key', bool(self.ui.keyCheckBox.isChecked()))
        s.set('mirror', bool(self.ui.mirrorCheckBox.isChecked()))
        s.save()

    def sliderPressed(self):
        """
        """
        self.record().beforeLoad(clear=True)

    def sliderReleased(self):
        """
        """
        key = self.ui.keyCheckBox.isChecked()
        blend = self.ui.blendSlider.value()
        self.record().apply(blend=blend, key=key)
        self.record().afterLoad()

    def sliderMoved(self, blend):
        """
        @type blend: int
        """
        self.record().applyBlend(blend=blend)

    @mutils.showWaitCursor
    def accept(self):
        """
        """
        self.record().apply()


class PoseCreateWidget(mayaBasePlugin.CreateWidget):

    def __init__(self, parent = None, record = None):
        """
        @type parent: 
        @type record: 
        """
        mayaBasePlugin.CreateWidget.__init__(self, parent, record)

    def update(self):
        """
        """
        record = self.record()
        record.edit()

    def help(self):
        """
        """
        analytics = studioLibrary.Analytics()
        analytics.logEvent('Help', 'Pose')
        import webbrowser
        webbrowser.open('https://www.youtube.com/watch?v=lpaWrT7VXfM')

    @mutils.showWaitCursor
    def accept(self):
        """
        @raise:
        """
        msg = 'An error has occurred while saving! Please check the script editor for the traceback.'
        mayaBasePlugin.CreateWidget.accept(self)
        try:
            record = self.record()
            path = studioLibrary.tempDir(make=True, clean=True, subdir='TransferPoseTemp') + '/pose.json'
            objects = maya.cmds.ls(selection=True)
            p = mutils.Pose.createFromObjects(objects)
            p.save(path)
            content = [path]
            record.save(content=content, icon=self.thumbnail())
        except Exception:
            self.record().window().setError(msg)
            raise


if __name__ == '__main__':
    import studioLibrary
    studioLibrary.main()
