#!/usr/bin/python
"""
"""
import os
import shutil
import logging
import maya.cmds
import mutils
import studiolibrary
import mayabaseplugin

try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore


logger = logging.getLogger("studiolibraryplugins.animationplugin")


class AnimationPluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class ValidateAnimationError(AnimationPluginError):
    """"""
    pass


class Plugin(mayabaseplugin.Plugin):
    def __init__(self, parent):
        """
        @type parent:
        """
        mayabaseplugin.Plugin.__init__(self, parent)

        self.setName("Animation")
        self.setExtension("anim")
        self.setIcon(self.dirname() + "/images/animation.png")

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
        settings.setdefault('option', "replace")


class Record(mayabaseplugin.Record):
    def __init__(self, *args, **kwargs):
        """
        @type args: list[]
        @type kwargs: dict[]
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)
        self._filename = None
        self._sequenceTimer = None

        self.setTransferClass(mutils.Animation)
        self.setTransferBasename("")

    def sequenceTimer(self):
        """
        @rtype:
        """
        return self._sequenceTimer

    def setSequenceTimer(self, value):
        """
        @type value: studiolibrary.SequenceTimer
        """
        self._sequenceTimer = value

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
        self.setSequenceTimer(None)
        mayabaseplugin.Record.rename(self, *args, **kwargs)

    def mouseEnterEvent(self, event):
        """
        @type event: QtGui.QEvent
        """
        studiolibrary.Record.mouseEnterEvent(self, event)

        if not self.sequenceTimer():
            dirname = self.dirname() + "/sequence"
            sequenceTimer = studiolibrary.SequenceTimer(self.parent())
            sequenceTimer.setDirname(dirname)

            # This line has issues with PySide
            #sequenceTimer.communicate.frameChanged.connect(self.frameChanged)

            sequenceTimer.communicate.frameChanged.connect(
                lambda filename, self=self: self.frameChanged(filename))

            self.setSequenceTimer(sequenceTimer)
        self.sequenceTimer().start()

    def mouseLeaveEvent(self, event):
        """
        @type event: QtGui.QEvent
        """
        studiolibrary.Record.mouseLeaveEvent(self, event)
        self.stop()

    def mouseMoveEvent(self, event):
        """
        @type event: QtGui.QEvent
        """
        studiolibrary.Record.mouseMoveEvent(self, event)
        if studiolibrary.isControlModifier():
            x = event.pos().x() - self.rect().x()
            width = self.rect().width()
            percent = 1.0 - (float(width - x) / float(width))
            frame = int(self._sequenceTimer.duration() * percent)
            self.sequenceTimer().setCurrentFrame(frame)
            self._filename = self._sequenceTimer.currentFilename()
            self.repaint()

    def frameChanged(self, path):
        """
        @type path: str
        """
        if not studiolibrary.isControlModifier():
            self._filename = path
            self.repaint()

    def paint(self, painter, option):
        """
        @type painter:
        @type option:
        """
        if self._filename:
            self.setPixmap(QtGui.QPixmap(self._filename))

        studiolibrary.Record.paint(self, painter, option)
        painter.save()

        if self._filename:
            r = self.rect()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 80, 80)))
            painter.drawRect(r.x(), r.y(), (self._sequenceTimer.percent() * r.width() - 1), 2)

        painter.restore()

    def save(self, content=None, icon=None, startFrame=None, endFrame=None, bakeConnected=False):
        """
        @raise:
        """
        try:
            objects = maya.cmds.ls(selection=True) or []
            self.validateSaveOptions(objects=objects, icon=icon)

            #tmpPath = studiolibrary.tempDir("transfer") + "/transfer.anim"
            tempDir = studiolibrary.TempDir("Transfer")
            tempPath = tempDir.path() + "/transfer.anim"

            t = self.transferClass().createFromObjects(objects)
            t.save(tempPath, time=[startFrame, endFrame], bakeConnected=bakeConnected)
            content.extend(t.paths())

            self.set("start", startFrame)
            self.set("end", endFrame)

            studiolibrary.Record.save(self, content=content, icon=icon)

        except Exception, msg:
            self.window().setError(str(msg))
            raise

    def load(self, start=None, sourceStart=None, sourceEnd=None):
        """
        """
        logger.info("Loading: %s" % self.transferPath())
        try:
            objects = maya.cmds.ls(selection=True) or []
            namespaces = self.namespaces()

            if sourceEnd is None:
                sourceEnd = int(self.get("end"))

            if sourceStart is None:
                sourceStart = int(self.get("start"))

            # GET USER OPTIONS
            settings = self.plugin().settings()
            option = str(settings.get("option"))
            connect = int(settings.get("connect"))

            if self.plugin().settings().get("currentTime"):
                start = int(maya.cmds.currentTime(query=True))

            self.transferObject().load(objects=objects, namespaces=namespaces, start=start, option=option,
                                       connect=connect, sourceTime=(sourceStart, sourceEnd))

        except Exception, msg:
            self.window().setError(str(msg))
            raise


class AnimationInfoWidget(mayabaseplugin.InfoWidget):

    def __init__(self, parent=None, record=None):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayabaseplugin.InfoWidget.__init__(self, parent, record)

        self._record = record
        end = str(record.get("end"))
        start = str(record.get("start"))

        self.ui.start.setText(start)
        self.ui.end.setText(end)


class AnimationCreateWidget(mayabaseplugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        @type args:
        @type kwargs:
        """
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)

        self._sequence = None
        start, end = mutils.currentRange()

        self.ui.sequenceWidget = studiolibrary.SequenceWidget(self)
        self.connect(self.ui.sequenceWidget, QtCore.SIGNAL("clicked()"), self.snapshot)
        self.ui.layout().insertWidget(1, self.ui.sequenceWidget)
        self.ui.snapshotButton.parent().hide()

        self.ui.endFrameEdit.setValidator(QtGui.QIntValidator(-50000000, 50000000, self))
        self.ui.startFrameEdit.setValidator(QtGui.QIntValidator(-50000000, 50000000, self))

        self.ui.endFrameEdit.setText(str(int(end)))
        self.ui.startFrameEdit.setText(str(int(start)))

        self.ui.byFrameEdit.setValidator(QtGui.QIntValidator(1, 1000, self))
        self.ui.byFrameEdit.setText(str(self.settings().get("byFrame")))

        self.connect(self.ui.setEndFrameButton, QtCore.SIGNAL("clicked()"), self.setEndFrame)
        self.connect(self.ui.setStartFrameButton, QtCore.SIGNAL("clicked()"), self.setStartFrame)

    def startFrame(self):
        """
        @rtype:
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
        self.settings().set("byFrame", self.byFrame())
        self.settings().save()
        mayabaseplugin.CreateWidget.close(self)

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
        @raise AnimationPluginError:
        """
        startFrame, endFrame = mutils.selectedRange()
        if startFrame == endFrame:
            endFrame = self.endFrame()
            startFrame = self.startFrame()

        self.validateFrameRage()

        if self.settings().get("byFrameDialog") and self.duration() > 100 and self.byFrame() == 1:
            msg = '''To help speed up the playblast you can set the "by frame" to a greater number than 1.
eg: If the "by frame" is set to 2 it will playblast every second frame.
Would you like to show this message again?'''
            result = self.window().questionDialog(msg, "Tip")
            if result == QtGui.QMessageBox.Cancel:
                raise Exception("Playblast cancelled!")
            elif result == QtGui.QMessageBox.No:
                self.settings().set("byFrameDialog", False)

        # path = studiolibrary.tempDir(make=True, clean=True)
        tempDir = studiolibrary.TempDir(clean=True)

        self._thumbnail = tempDir.path() + "/thumbnail.jpg"
        self._sequence = tempDir.path() + "/sequence/thumbnail.jpg"
        try:
            self._sequence = mutils.snapshot(path=self._sequence, start=startFrame, end=endFrame,
                                             step=self.byFrame())
        except mutils.SnapshotError, e:
            self.record().window().setError(str(e))
            raise

        shutil.copyfile(self._sequence, self._thumbnail)
        self.setSnapshot(self._thumbnail)
        self.ui.sequenceWidget.setDirname(os.path.dirname(self._sequence))

    def validateFrameRage(self):
        """
        @raise Exception:
        """
        if self.startFrame() is None or self.endFrame() is None:
            msg = "Please choose a start frame and an end frame."
            self.window().setError(str(msg))
            raise ValidateAnimationError(msg)

    def validateImageSequence(self):
        """
        @raise Exception:
        """
        if not self._sequence or not self.thumbnail():
            msg = "No icon was found. Please create an icon first before saving."
            self.window().setError(msg)
            raise ValidateAnimationError(msg)

    def validateUnknownNodes(self):
        """
        @raise Exception:
        """
        unknown = maya.cmds.ls(type="unknown")
        if unknown:
            msg = """Found %s unknown node/s in the current scene.
Please fix or remove all unknown nodes before saving.
""" % len(unknown)
            self.window().setError(msg)
            print "Unknown nodes: " + str(unknown)
            raise ValidateAnimationError(msg)

    def accept(self):
        """
        @raise:
        """
        endFrame = self.endFrame()
        startFrame = self.startFrame()
        bakeConnected = int(self.ui.bakeCheckBox.isChecked())

        self.validateUnknownNodes()
        self.validateImageSequence()

        self.record().setName(self.nameText())
        self.record().setDescription(self.description())
        self.record().save(content=[os.path.dirname(self._sequence)], icon=self.thumbnail(),
                           startFrame=startFrame, endFrame=endFrame, bakeConnected=bakeConnected)


class AnimationPreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, parent=None, record=None):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayabaseplugin.PreviewWidget.__init__(self, parent, record)

        end = str(record.get("end"))
        start = str(record.get("start"))

        self.ui.start.setText(start)
        self.ui.end.setText(end)
        self.ui.sourceStartEdit.setText(start)
        self.ui.sourceEndEdit.setText(end)

        self.connect(self.ui.currentTime, QtCore.SIGNAL("stateChanged (int)"), self.stateChanged)
        self.connect(self.ui.helpCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.showHelpImage)
        self.connect(self.ui.connectCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.connectChanged)
        self.connect(self.ui.option, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.optionChanged)

        self.loadSettings()

    def sourceStart(self):
        """
        @rtype int
        """
        return int(self.ui.sourceStartEdit.text())

    def sourceEnd(self):
        """
        @rtype int
        """
        return int(self.ui.sourceEndEdit.text())

    def showHelpImage(self, value, save=True):
        """
        @type value:
        @type save:
        """
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
        s.set("option", str(self.ui.option.currentText()))
        s.set("currentTime", bool(self.ui.currentTime.isChecked()))
        s.set("connect", float(self.ui.connectCheckBox.isChecked()))
        s.set("showHelpImage", bool(self.ui.helpCheckBox.isChecked()))
        s.save()

    def loadSettings(self):
        """
        """
        super(AnimationPreviewWidget, self).loadSettings()
        s = self.settings()
        self.ui.currentTime.setChecked(s.get("currentTime"))
        self.ui.connectCheckBox.setChecked(s.get("connect"))
        self.optionChanged(s.get("option"), save=False)
        self.ui.helpCheckBox.setChecked(s.get("showHelpImage"))
        self.showHelpImage(s.get("showHelpImage"), save=False)

    def connectChanged(self, value):
        """
        @type value: bool
        """
        self.optionChanged(str(self.ui.option.currentText()))

    def optionChanged(self, text, save=True):
        """
        @type text: str
        """
        imageText = text
        if text == "replace all":
            imageText = "replaceCompletely"
            self.ui.connectCheckBox.setEnabled(False)
        else:
            self.ui.connectCheckBox.setEnabled(True)
        connect = ""
        if self.ui.connectCheckBox.isChecked() and text != "replace all":
            connect = "Connect"
        option_image = os.path.join(self.record().plugin().dirname(), "images/%s%s.png" % (imageText, connect))
        self.ui.helpImage.setPixmap(QtGui.QPixmap(option_image))
        index = self.ui.option.findText(text)
        if index:
            self.ui.option.setCurrentIndex(index)
        if save:
            self.saveSettings()


def test():
    """
    Use this code for testing inside maya. It should reload this plugin and the base plugin.
    """
    import studiolibrary

    from studiolibraryplugins import mayabaseplugin
    reload(mayabaseplugin)
    from studiolibraryplugins import animationplugin
    reload(animationplugin)

    import mutils
    import mutils.modelpanelwidget
    reload(mutils.modelpanelwidget)

    w = studiolibrary.main(name="TEMP")
    p = w.plugins()["animationplugin"]
    p.setRecord(animationplugin.Record)
    p.setInfoWidget(animationplugin.AnimationInfoWidget)
    p.setCreateWidget(animationplugin.AnimationCreateWidget)
    p.setPreviewWidget(animationplugin.AnimationPreviewWidget)



