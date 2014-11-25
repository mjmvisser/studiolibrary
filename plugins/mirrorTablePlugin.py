#Embedded file name: C:/Users/hovel/Dropbox/packages/studioLibrary/1.5.8/build27/studioLibrary\plugins\mirrorTablePlugin.py
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

import mutils
import studioLibrary
import studioLibrary.plugins.mayaBasePlugin as mayaBasePlugin

class SelectionSetPluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class Plugin(mayaBasePlugin.Plugin):

    def __init__(self, parent):
        """
        @type parent:
        """
        studioLibrary.Plugin.__init__(self, parent)
        self.setName('Mirror Table')
        self.setIcon(self.dirname() + '/images/mirrortable.png')
        self.setExtension('mirror')
        self.setRecord(Record)
        self.setInfoWidget(MirrorTableInfoWidget)
        self.setCreateWidget(MirrorTableCreateWidget)
        self.setPreviewWidget(MirrorTablePreviewWidget)

    def mirrorAnimation(self):
        """
        @rtype: bool
        """
        return self.settings().get('mirrorAnimation', True)

    def mirrorOption(self):
        """
        @rtype: mutils.MirrorOption
        """
        return self.settings().get('mirrorOption', mutils.MirrorOption.Swap)


class Record(mayaBasePlugin.Record):

    def __init__(self, *args, **kwargs):
        mayaBasePlugin.Record.__init__(self, *args, **kwargs)
        self._transferObject = None

    def transferPath(self):
        return self.dirname() + '/mirrortable.json'

    def transferObject(self):
        if self._transferObject is None:
            self._transferObject = mutils.MirrorTable.createFromPath(self.transferPath())
        return self._transferObject

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_M:
            pass

    @mutils.showWaitCursor
    def load(self, option = None, animation = None, time = None):
        """
        """
        if option is None:
            option = self.plugin().mirrorOption()
        if animation is None:
            animation = self.plugin().mirrorAnimation()
        objects = maya.cmds.ls(selection=True)
        try:
            self.transferObject().load(objects, namespaces=self.namespaces(), option=option, animation=animation, time=time)
        except Exception as msg:
            self.window().setError(str(msg))
            raise

    def doubleClicked(self):
        """
        """
        self.load()


class MirrorTableInfoWidget(mayaBasePlugin.InfoWidget):

    def __init__(self, parent = None, record = None):
        """
        :param parent:
        :param record:
        """
        mayaBasePlugin.InfoWidget.__init__(self, parent, record)


class MirrorTablePreviewWidget(mayaBasePlugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        """
        mayaBasePlugin.PreviewWidget.__init__(self, *args, **kwargs)
        self.connect(self.ui.mirrorAnimationCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.stateChanged)
        self.connect(self.ui.mirrorOptionComboBox, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.stateChanged)
        mt = self.record().transferObject()
        self.ui.left.setText(mt.left())
        self.ui.right.setText(mt.right())

    def mirrorOption(self):
        return self.ui.mirrorOptionComboBox.findText(self.ui.mirrorOptionComboBox.currentText(), QtCore.Qt.MatchExactly)

    def mirrorAnimation(self):
        return self.ui.mirrorAnimationCheckBox.isChecked()

    def saveSettings(self):
        """
        """
        super(MirrorTablePreviewWidget, self).saveSettings()
        s = self.settings()
        s.set('mirrorOption', int(self.mirrorOption()))
        s.set('mirrorAnimation', bool(self.mirrorAnimation()))
        s.save()

    def loadSettings(self):
        """
        """
        super(MirrorTablePreviewWidget, self).loadSettings()
        s = self.settings()
        self.ui.mirrorOptionComboBox.setCurrentIndex(s.get('mirrorOption', mutils.MirrorOption.Swap))
        self.ui.mirrorAnimationCheckBox.setChecked(s.get('mirrorAnimation', True))

    def accept(self):
        """
        """
        self.record().load()


class MirrorTableCreateWidget(mayaBasePlugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        """
        mayaBasePlugin.CreateWidget.__init__(self, *args, **kwargs)
        self.ui.selectionSetButton.hide()

    def selectionChanged(self):
        objects = maya.cmds.ls(selection=True) or []
        if not self.ui.left.text():
            self.ui.left.setText(mutils.MirrorTable.findLeftSide(objects))
        if not self.ui.right.text():
            self.ui.right.setText(mutils.MirrorTable.findRightSide(objects))
        mt = mutils.MirrorTable.createFromObjects([], left=str(self.ui.left.text()), right=str(self.ui.right.text()))
        self.ui.leftCount.setText(str(mt.leftCount(objects)))
        self.ui.rightCount.setText(str(mt.rightCount(objects)))
        mayaBasePlugin.CreateWidget.selectionChanged(self)

    @mutils.showWaitCursor
    def accept(self):
        """
        :raise:
        """
        mayaBasePlugin.CreateWidget.accept(self)
        msg = 'An error has occurred while saving the mirror table! Please check the script editor for more details.'
        try:
            path = studioLibrary.getTempDir() + '/mirrortable.json'
            left = str(self.ui.left.text())
            right = str(self.ui.right.text())
            mt = mutils.MirrorTable.createFromObjects(maya.cmds.ls(selection=True), left=left, right=right)
            mt.save(path)
            self.record().save(content=[path], icon=self._thumbnail)
        except Exception:
            self.record().window().setError(msg)
            raise


if __name__ == '__main__':
    import studioLibrary
    studioLibrary.main()
