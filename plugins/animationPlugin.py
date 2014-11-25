#Embedded file name: C:/Users/hovel/Dropbox/packages/studioLibrary/1.5.8/build27/studioLibrary\plugins\animationPlugin.py
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
import os
import time
import shutil
import mutils
try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore

try:
    import maya.mel
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()

import studioLibrary
import studioLibrary.plugins.mayaBasePlugin as mayaBasePlugin

class AnimationPluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class Plugin(mayaBasePlugin.Plugin):

    def __init__(self, parent):
        """
        @type parent:
        """
        studioLibrary.Plugin.__init__(self, parent)
        self.setName('Animation')
        self.setExtension('anim')
        self.setIcon(self.dirname() + '/images/animation.png')
        self.setRecord(Record)
        self.setInfoWidget(AnimationInfoWidget)
        self.setCreateWidget(AnimationCreateWidget)
        self.setPreviewWidget(AnimationPreviewWidget)
        settings = self.settings()
        settings.setdefault('byFrame', 1)
        settings.setdefault('byFrameDialog', True)
        settings.setdefault('connect', False)
        settings.setdefault('currentTime', False)
        settings.setdefault('showHelpImage', True)
        settings.setdefault('option', 'replace')


class Record(mayaBasePlugin.Record):

    def __init__(self, *args, **kwargs):
        """
        @type args: list[]
        @type kwargs: dict[]
        """
        mayaBasePlugin.Record.__init__(self, *args, **kwargs)
        self._pose = None
        self._filename = None
        self._sequenceTimer = None

    def transferPath(self):
        return self.dirname()

    def transferObject(self):
        if self._transferObject is None:
            self._transferObject = mutils.Animation.createFromPath(self.transferPath())
        return self._transferObject

    def doubleClicked(self):
        """
        """
        self.accept()

    def stop(self):
        """
        """
        self._filename = None
        self._sequenceTimer.stop()
        self.repaint()

    def rename(self, *args, **kwargs):
        """
        @type args: list[]
        @type kwargs: dict[]
        """
        self._sequenceTimer = None
        mayaBasePlugin.Record.rename(self, *args, **kwargs)

    def mouseEnterEvent(self, event):
        """
        @type event: QtGui.QEvent
        """
        studioLibrary.Record.mouseEnterEvent(self, event)
        if not self._sequenceTimer:
            dirname = self.dirname() + '/sequence'
            self._sequenceTimer = studioLibrary.SequenceTimer(self.parent())
            self._sequenceTimer.setDirname(dirname)
            self._sequenceTimer.communicate.frameChanged.connect(lambda filename, self = self: self.frameChanged(filename))
        self._sequenceTimer.start()

    def mouseLeaveEvent(self, event):
        """
        @type event: QtGui.QEvent
        """
        studioLibrary.Record.mouseLeaveEvent(self, event)
        self.stop()

    def mouseMoveEvent(self, event):
        """
        @type event: QtGui.QEvent
        """
        studioLibrary.Record.mouseMoveEvent(self, event)
        if studioLibrary.isControlModifier():
            x = event.pos().x() - self.rect().x()
            width = self.rect().width()
            percent = 1.0 - float(width - x) / float(width)
            frame = int(self._sequenceTimer.duration() * percent)
            self._sequenceTimer.setCurrentFrame(frame)
            self._filename = self._sequenceTimer.currentFilename()
            self.repaint()

    def frameChanged(self, path):
        """
        @type path: str
        """
        if not studioLibrary.isControlModifier():
            self._filename = path
            self.repaint()

    def paint(self, painter, option):
        """
        @type painter:
        @type option:
        """
        if self._filename:
            self.setPixmap(QtGui.QPixmap(self._filename))
        studioLibrary.Record.paint(self, painter, option)
        painter.save()
        if self._filename:
            r = self.rect()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 80, 80)))
            painter.drawRect(r.x(), r.y(), self._sequenceTimer.percent() * r.width() - 1, 2)
        painter.restore()

    def accept(self, sourceStart = None, sourceEnd = None):
        """
        @type sourceStart:
        @type sourceEnd:
        :raise AnimationPluginError:
        """
        msg = 'An error has occurred while loading the animation! Please check the script editor for the traceback.'
        start = None
        try:
            t = time.time()
            if not sourceEnd:
                sourceEnd = int(self.get('end'))
            if not sourceStart:
                sourceStart = int(self.get('start'))
            namespaces = []
            objects = maya.cmds.ls(selection=True) or []
            if not objects:
                namespaces = self.namespaces()
            gSelectedAnimLayers = maya.mel.eval('$a = $gSelectedAnimLayers;')
            if len(gSelectedAnimLayers) > 1:
                msg = 'More than one animation layer selected! Please select only one animation layer for import!'
                raise AnimationPluginError(msg)
            settings = self.plugin().settings()
            option = str(settings.get('option'))
            connect = int(settings.get('connect'))
            if settings.get('currentTime'):
                start = int(maya.cmds.currentTime(query=True))
            if sourceStart < self.get('start') or sourceEnd > self.get('end'):
                msg = 'The requested source time is out of range! Choose a source range between %s - %s.' % (self.get('start'), self.get('end'))
                raise AnimationPluginError(msg)
            a = mutils.Animation.createFromPath(self.dirname())
            a.load(objects, namespaces=namespaces, start=start, sourceTime=(sourceStart, sourceEnd), option=option, connect=connect)
            t = time.time() - t
            self.window().setInfo('Loaded animation in %0.3f seconds.' % t)
        except Exception:
            import traceback
            traceback.print_exc()
            self.window().setError(msg)


class AnimationInfoWidget(mayaBasePlugin.InfoWidget):

    def __init__(self, parent = None, record = None):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayaBasePlugin.InfoWidget.__init__(self, parent, record)
        self._record = record
        end = str(record.get('end'))
        start = str(record.get('start'))
        self.ui.start.setText(start)
        self.ui.end.setText(end)


class AnimationPreviewWidget(mayaBasePlugin.PreviewWidget):

    def __init__(self, parent = None, record = None):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayaBasePlugin.PreviewWidget.__init__(self, parent, record)
        end = str(record.get('end'))
        start = str(record.get('start'))
        self.ui.start.setText(start)
        self.ui.end.setText(end)
        self.ui.sourceStartEdit.setText(start)
        self.ui.sourceEndEdit.setText(end)
        self.connect(self.ui.currentTime, QtCore.SIGNAL('stateChanged (int)'), self.stateChanged)
        self.connect(self.ui.helpCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.showHelpImage)
        self.connect(self.ui.connectCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.connectChanged)
        self.connect(self.ui.option, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.optionChanged)
        self.loadSettings()

    def sourceStart(self):
        return int(self.ui.sourceStartEdit.text())

    def sourceEnd(self):
        return int(self.ui.sourceEndEdit.text())

    def showHelpImage(self, value, save = True):
        if value:
            self.ui.helpImage.show()
        else:
            self.ui.helpImage.hide()
        if save:
            self.saveSettings()

    def saveSettings(self):
        """
        """
        super(AnimationPreviewWidget, self).saveSettings()
        s = self.settings()
        s.set('option', str(self.ui.option.currentText()))
        s.set('currentTime', bool(self.ui.currentTime.isChecked()))
        s.set('connect', float(self.ui.connectCheckBox.isChecked()))
        s.set('showHelpImage', bool(self.ui.helpCheckBox.isChecked()))
        s.save()

    def loadSettings(self):
        """
        """
        super(AnimationPreviewWidget, self).loadSettings()
        s = self.settings()
        self.ui.currentTime.setChecked(s.get('currentTime'))
        self.ui.connectCheckBox.setChecked(s.get('connect'))
        self.optionChanged(s.get('option'), save=False)
        self.ui.helpCheckBox.setChecked(s.get('showHelpImage'))
        self.showHelpImage(s.get('showHelpImage'), save=False)

    def connectChanged(self, value):
        """
        @type value: bool
        """
        self.optionChanged(str(self.ui.option.currentText()))

    def optionChanged(self, text, save = True):
        """
        @type text: str
        """
        imageText = text
        if text == 'replace all':
            imageText = 'replaceCompletely'
            self.ui.connectCheckBox.setEnabled(False)
        else:
            self.ui.connectCheckBox.setEnabled(True)
        connect = ''
        if self.ui.connectCheckBox.isChecked() and text != 'replace all':
            connect = 'Connect'
        option_image = os.path.join(self.record().plugin().dirname(), 'images/%s%s.png' % (imageText, connect))
        self.ui.helpImage.setPixmap(QtGui.QPixmap(option_image))
        index = self.ui.option.findText(text)
        if index:
            self.ui.option.setCurrentIndex(index)
        if save:
            self.saveSettings()

    def accept(self):
        """
        """
        self.record().accept(self.sourceStart(), self.sourceEnd())


class AnimationCreateWidget(mayaBasePlugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        @type args:
        @type kwargs:
        """
        mayaBasePlugin.CreateWidget.__init__(self, *args, **kwargs)
        self.connect(self.ui.setEndFrameButton, QtCore.SIGNAL('clicked()'), self.setEndFrame)
        self.connect(self.ui.setStartFrameButton, QtCore.SIGNAL('clicked()'), self.setStartFrame)
        self._sequence = None
        self.ui.byFrameEdit.setValidator(QtGui.QIntValidator(1, 1000, self))
        self.ui.sequenceWidget = studioLibrary.SequenceWidget(self)
        self.connect(self.ui.sequenceWidget, QtCore.SIGNAL('clicked()'), self.snapshot)
        self.ui.layout().insertWidget(1, self.ui.sequenceWidget)
        self.ui.snapshotButton.parent().hide()
        try:
            self.ui.byFrameEdit.setText(str(self.settings().get('byFrame')))
            start, end = mutils.currentRange()
            self.ui.startFrameEdit.setValidator(QtGui.QIntValidator(-50000000, 50000000, self))
            self.ui.endFrameEdit.setValidator(QtGui.QIntValidator(-50000000, 50000000, self))
            self.ui.startFrameEdit.setText(str(int(start)))
            self.ui.endFrameEdit.setText(str(int(end)))
        except ValueError:
            import traceback
            traceback.print_exc()

    def startFrame(self):
        """
        :return:
        """
        try:
            return int(float(str(self.ui.startFrameEdit.text()).strip()))
        except ValueError:
            return None

    def endFrame(self):
        """
        @rtype:
        """
        try:
            return int(float(str(self.ui.endFrameEdit.text()).strip()))
        except ValueError:
            return None

    def duration(self):
        """
        @rtype:
        """
        return self.endFrame() - self.startFrame()

    def byFrame(self):
        """
        @rtype:
        """
        return int(float(self.ui.byFrameEdit.text()))

    def close(self):
        """
        """
        self.settings().set('byFrame', self.byFrame())
        self.settings().save()
        mayaBasePlugin.CreateWidget.close(self)

    def setEndFrame(self):
        """
        """
        start, end = mutils.selectedRange()
        self.ui.endFrameEdit.setText(str(end))

    def setStartFrame(self):
        """
        """
        start, end = mutils.selectedRange()
        self.ui.startFrameEdit.setText(str(start))

    def snapshot(self):
        """
        :raise AnimationPluginError:
        """
        startFrame, endFrame = mutils.selectedRange()
        if startFrame == endFrame:
            endFrame = self.endFrame()
            startFrame = self.startFrame()
        if startFrame is None or endFrame is None:
            msg = 'Please choose a start frame and an end frame.'
            import traceback
            traceback.print_exc()
            QtGui.QMessageBox.critical(self, 'Error', msg)
            raise AnimationPluginError(msg)
        if self.settings().get('byFrameDialog') and self.duration() > 100 and self.byFrame() == 1:
            msg = 'To help speed up the playblast you can set the "by frame" to a greater number than 1.\neg: If the "by frame" is set to 2 it will playblast every second frame.\nWould you like to show this message again?'
            result = self.window().questionDialog(msg, 'Tip')
            if result == QtGui.QMessageBox.Cancel:
                raise AnimationPluginError('Playblast cancelled!')
            elif result == QtGui.QMessageBox.No:
                self.settings().set('byFrameDialog', False)
        path = studioLibrary.tempDir(make=True, clean=True)
        self._thumbnail = path + '/thumbnail.jpg'
        self._sequence = path + '/sequence/thumbnail.jpg'
        try:
            self._sequence = mutils.snapshot(path=self._sequence, start=startFrame, end=self.endFrame(), step=self.byFrame())
        except mutils.SnapshotError as e:
            self.record().window().setError(str(e))
            raise

        shutil.copyfile(self._sequence, self._thumbnail)
        self.setSnapshot(self._thumbnail)
        self.ui.sequenceWidget.setDirname(os.path.dirname(self._sequence))

    def accept(self):
        """
        :raise AnimationPluginError:
        """
        msg = 'An error has occurred while saving the animation! Please check the script editor for the traceback.'
        mayaBasePlugin.CreateWidget.accept(self)
        try:
            record = self.record()
            gSelectedAnimLayers = maya.mel.eval('$a = $gSelectedAnimLayers;')
            if len(gSelectedAnimLayers) > 1:
                msg = 'More than one animation layer selected! Please select only one animation layer for export!'
                raise AnimationPluginError(msg)
            if self.startFrame() is None or self.endFrame() is None:
                msg = 'Please specify a start and end frame!'
                raise AnimationPluginError(msg)
            if self.startFrame() >= self.endFrame():
                msg = 'The start frame cannot be greater than or equal to the end frame!'
                raise AnimationPluginError(msg)
            if mutils.getDurationFromNodes(nodes=maya.cmds.ls(selection=True) or []) <= 0:
                msg = 'No animation was found on the selected objects! Please create a pose instead!'
                raise AnimationPluginError(msg)
            path = studioLibrary.tempDir(make=True, clean=True, subdir='animation.anim')
            objects = maya.cmds.ls(selection=True)
            bakeConnected = int(self.ui.bakeCheckBox.isChecked())
            a = mutils.Animation.createFromObjects(objects)
            a.save(path, time=(self.startFrame(), self.endFrame()), bakeConnected=bakeConnected)
            content = a.paths()
            record.set('start', self.startFrame())
            record.set('end', self.endFrame())
            if self._sequence:
                sequence = os.path.dirname(self._sequence)
                if os.path.exists(sequence):
                    content.append(sequence)
            record.save(content=content, icon=self.thumbnail())
        except Exception:
            self.record().window().setError(msg)
            raise


if __name__ == '__main__':
    import studioLibrary
    studioLibrary.main()
