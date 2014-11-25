#Embedded file name: C:/Users/hovel/Dropbox/packages/studioLibrary/1.5.8/build27/studioLibrary\plugins\selectionSetPlugin.py
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
        :param parent:
        """
        studioLibrary.Plugin.__init__(self, parent)
        self.setName('Selection Set')
        self.setIcon(self.dirname() + '/images/set.png')
        self.setExtension('set')
        self.setRecord(Record)
        self.setInfoWidget(SelectionSetInfoWidget)
        self.setCreateWidget(SelectionSetCreateWidget)
        self.setPreviewWidget(SelectionSetPreviewWidget)


class Record(mayaBasePlugin.Record):

    def __init__(self, *args, **kwargs):
        mayaBasePlugin.Record.__init__(self, *args, **kwargs)
        self._transferObject = None

    def selectionSet(self):
        """
        :return:
        """
        return self.transferObject()

    def transferPath(self):
        import os
        path = self.dirname() + '/set.json'
        if not os.path.exists(path):
            path = self.dirname() + '/set.list'
        return path

    def transferObject(self):
        """
        :return:
        """
        if not self._transferObject:
            self._transferObject = mutils.SelectionSet.createFromPath(self.transferPath())
        return self._transferObject

    def doubleClicked(self):
        """
        """
        self.selectSelectionSet()


class SelectionSetInfoWidget(mayaBasePlugin.InfoWidget):

    def __init__(self, parent = None, record = None):
        """
        :param parent:
        :param record:
        """
        mayaBasePlugin.InfoWidget.__init__(self, parent, record)


class SelectionSetPreviewWidget(mayaBasePlugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        """
        mayaBasePlugin.PreviewWidget.__init__(self, *args, **kwargs)
        self.ui.selectionSetButton.hide()

    @mutils.showWaitCursor
    def accept(self):
        """
        """
        self.record().selectSelectionSet()


class SelectionSetCreateWidget(mayaBasePlugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        """
        mayaBasePlugin.CreateWidget.__init__(self, *args, **kwargs)
        self.ui.selectionSetButton.hide()

    def help(self):
        analytics = studioLibrary.Analytics()
        analytics.logEvent('Help', 'Selection Set')
        import webbrowser
        webbrowser.open('https://www.youtube.com/watch?v=xejWubal_j8')

    @mutils.showWaitCursor
    def accept(self):
        """
        :raise:
        """
        mayaBasePlugin.CreateWidget.accept(self)
        msg = 'An error has occurred while saving the selection set! Please check the script editor for the traceback.'
        try:
            path = exportSelectionSetToTemp()
            self.record().save(content=[path], icon=self._thumbnail)
        except Exception:
            self.record().window().setError(msg)
            raise


def exportSelectionSet(path):
    objects = maya.cmds.ls(selection=True)
    selectionSet = mutils.SelectionSet.createFromObjects(objects)
    selectionSet.save(path)
    return path


def exportSelectionSetToTemp():
    path = studioLibrary.tempDir(make=True, clean=True, subdir='SelectionSetTemp')
    path += '/set.json'
    return exportSelectionSet(path)


if __name__ == '__main__':
    import studioLibrary
    studioLibrary.main()
