#!/usr/bin/python
"""
"""
import os
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


logger = logging.getLogger("studiolibraryplugin.mirrortableplugin")


class Plugin(mayabaseplugin.Plugin):

    def __init__(self, parent):
        """
        @type parent:
        """
        studiolibrary.Plugin.__init__(self, parent)

        self.setName("Mirror Table")
        self.setIcon(self.dirname() + "/images/mirrortable.png")
        self.setExtension("mirror")

        self.setRecord(Record)
        self.setInfoWidget(MirrorTableInfoWidget)
        self.setCreateWidget(MirrorTableCreateWidget)
        self.setPreviewWidget(MirrorTablePreviewWidget)

    def mirrorAnimation(self):
        """
        @rtype: bool
        """
        return self.settings().get("mirrorAnimation", True)

    def mirrorOption(self):
        """
        @rtype: mutils.MirrorOption
        """
        return self.settings().get("mirrorOption", mutils.MirrorOption.Swap)


class Record(mayabaseplugin.Record):

    def __init__(self, *args, **kwargs):
        """
        @type args:
        @type kwargs:
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)
        self.setTransferBasename("mirrortable.json")
        self.setTransferClass(mutils.MirrorTable)

    def keyPressEvent(self, event):
        """
        @type event:
        """
        if event.key() == QtCore.Qt.Key_M:
            pass

    @mutils.showWaitCursor
    def load(self, option=None, animation=None, time=None):
        """
        @type option:
        @type animation:
        @type time:
        """
        if option is None:
            option = self.plugin().mirrorOption()

        if animation is None:
            animation = self.plugin().mirrorAnimation()

        try:
            objects = maya.cmds.ls(selection=True) or []
            self.transferObject().load(objects, namespaces=self.namespaces(),
                                       option=option, animation=animation, time=time)
        except Exception, msg:
            self.window().setError(str(msg))
            raise

    def save(self, left, right, icon=None):
        """
        @raise:
        """
        logger.info("Saving: %s" % self.transferPath())
        try:
            objects = maya.cmds.ls(selection=True) or []
            self.validateSaveOptions(objects, icon)

            tempDir = studiolibrary.TempDir("Transfer", makedirs=True)
            tmpPath = os.path.join(tempDir.path(), self.transferBasename())

            t = self.transferClass().createFromObjects(objects, left=left, right=right)
            t.save(tmpPath)

            studiolibrary.Record.save(self, content=[tmpPath], icon=icon)
        except Exception, msg:
            self.window().setError(str(msg))
            raise


class MirrorTableInfoWidget(mayabaseplugin.InfoWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayabaseplugin.InfoWidget.__init__(self, *args, **kwargs)


class MirrorTablePreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayabaseplugin.PreviewWidget.__init__(self, *args, **kwargs)

        self.connect(self.ui.mirrorAnimationCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.stateChanged)
        self.connect(self.ui.mirrorOptionComboBox, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.stateChanged)

        mt = self.record().transferObject()
        self.ui.left.setText(mt.left())
        self.ui.right.setText(mt.right())

    def mirrorOption(self):
        """
        @rtype: str
        """
        return self.ui.mirrorOptionComboBox.findText(self.ui.mirrorOptionComboBox.currentText(), QtCore.Qt.MatchExactly)

    def mirrorAnimation(self):
        """
        @rtype: bool
        """
        return self.ui.mirrorAnimationCheckBox.isChecked()

    def saveSettings(self):
        """
        """
        super(MirrorTablePreviewWidget, self).saveSettings()
        s = self.settings()
        s.set("mirrorOption", int(self.mirrorOption()))
        s.set("mirrorAnimation", bool(self.mirrorAnimation()))
        s.save()

    def loadSettings(self):
        """
        """
        super(MirrorTablePreviewWidget, self).loadSettings()
        s = self.settings()
        self.ui.mirrorOptionComboBox.setCurrentIndex(s.get("mirrorOption", mutils.MirrorOption.Swap))
        self.ui.mirrorAnimationCheckBox.setChecked(s.get("mirrorAnimation", True))


class MirrorTableCreateWidget(mayabaseplugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)

    def selectionChanged(self):
        """
        """
        objects = maya.cmds.ls(selection=True) or []

        if not self.ui.left.text():
            self.ui.left.setText(mutils.MirrorTable.findLeftSide(objects))

        if not self.ui.right.text():
            self.ui.right.setText(mutils.MirrorTable.findRightSide(objects))

        mt = mutils.MirrorTable.createFromObjects([], left=str(self.ui.left.text()), right=str(self.ui.right.text()))

        self.ui.leftCount.setText(str(mt.leftCount(objects)))
        self.ui.rightCount.setText(str(mt.rightCount(objects)))

        mayabaseplugin.CreateWidget.selectionChanged(self)

    def accept(self):
        """
        """
        left = str(self.ui.left.text())
        right = str(self.ui.right.text())
        self.record().setName(self.nameText())
        self.record().setDescription(self.description())
        self.record().save(left=left, right=right, icon=self.thumbnail())


if __name__ == "__main__":
    import studiolibrary
    studiolibrary.main()