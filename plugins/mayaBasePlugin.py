#Embedded file name: C:/Users/hovel/Dropbox/packages/studioLibrary/1.5.8/build27/studioLibrary\plugins\mayaBasePlugin.py
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
# THIS SOFTWARE IS PROVIDED BY KURT RATHJEN  ''AS IS'' AND ANY
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
from functools import partial
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

class NamespaceType:
    Pose = 'pose'
    Custom = 'custom'
    Selection = 'selection'

    def __init__(self):
        pass


class BasePluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class Plugin(studioLibrary.Plugin):

    def namespaces(self):
        """
        @rtype: list[str]
        """
        return self.settings().get('namespaces')

    def getNamespaceType(self):
        """
        @rtype: NamespaceType
        """
        return self.settings().get('namespaceType', NamespaceType.Selection)

    def mirrorTables(self, record):
        """
        """
        return self._findPaths(record.path(), '.mirror')

    def selectionSets(self):
        """
        """
        return self.findRecords('.set')

    def walkUp(self, path, separator = '/'):
        """
        :param path:
        :param separator:
        """
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if not path.endswith(separator):
            path += separator
        folders = path.split(separator)
        for i, folder in enumerate(folders):
            result = separator.join(folders[:i * -1])
            if result and os.path.exists(result):
                yield result

    def _findPaths(self, dirname, extension):
        """
        @type dirname: str
        @rtype:  dict[str]
        """
        results = []
        for path in self.walkUp(dirname):
            for s in [ s for s in os.listdir(path) if extension in s ]:
                value = path + '/' + s
                results.append(value)

        return results

    def _findRecords(self, dirname, extension):
        """
        @type dirname: str
        @rtype:  dict[str]
        """
        root = self.window().root()
        if not root.endswith('/'):
            root += '/'
        folders = dirname.replace(root, '').split('/')
        results = {}
        for folder in folders:
            root += '/' + folder
            for s in [ s for s in os.listdir(root) if extension in s ]:
                key = folder + ': ' + s.replace(extension, '')
                value = root + '/' + s
                results[key] = value

        return results

    def findRecords(self, extension):
        """
        @rtype: dict[str]
        """
        folders = self.window().selectedFolders()
        results = {}
        for folder in folders:
            results.update(self._findRecords(folder.dirname(), extension))

        return results


class Record(studioLibrary.Record):

    def __init__(self, *args, **kwargs):
        """
        @type args: list[object]
        @type kwargs: dict[object]
        """
        studioLibrary.Record.__init__(self, *args, **kwargs)
        self._transferObject = None

    def count(self):
        """
        @rtype: int
        """
        return self.transferObject().count()

    def transferPath(self):
        return self.dirname() + '/pose.json'

    def transferObject(self):
        if self._transferObject is None:
            self._transferObject = mutils.SelectionSet.createFromPath(self.transferPath())
        return self._transferObject

    def namespaces(self):
        """
        @rtype: list[str]
        """
        namespaceType = self.plugin().getNamespaceType()
        if namespaceType == NamespaceType.Selection:
            namespaces = mutils.getNamespaceFromSelection() or ['']
        elif namespaceType == NamespaceType.Pose:
            namespaces = self.transferObject().namespaces()
        else:
            namespaces = self.plugin().namespaces()
        return namespaces

    @mutils.unifyUndo
    def selectContent(self, records):
        """
        @type records:
        """
        msg = 'An error has occurred while selecting controls from pose!Please check the script editor for the traceback.'
        try:
            namespaces = self.namespaces()
            for record in records:
                record.transferObject().select(namespaces=namespaces, **self.selectionArgs())

        except Exception:
            import traceback
            traceback.print_exc()
            self.window().setError(msg)

    def selectionArgs(self):
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
        return {'add': add,
         'deselect': deselect}

    def selectSelectionSet(self, record = None, apply = False):
        """
        @type record: Record
        """
        namespaces = self.namespaces()
        if not namespaces:
            msg = 'Please specify a namepsace!'
            self.window().setError(msg)
            raise BasePluginError(msg)
        if record is None:
            record = self
        try:
            record.transferObject().load(namespaces=namespaces, **self.selectionArgs())
        except mutils.NoMatchFoundError as e:
            self.window().setError(str(e))
            raise

        if apply:
            self.apply()

    def addSelectContentsAction(self, menu):
        """
        @type menu: QtGui.QMenu
        """
        records = self.window().selectedRecords()
        if records:
            icon = studioLibrary.icon(self.plugin().dirname() + '/images/arrow.png')
            action = studioLibrary.Action(icon, 'Select content', menu)
            trigger = partial(self.selectContent, records)
            action.setCallback(trigger)
            menu.addAction(action)

    def setsContextMenu(self, menu, records, includeSelectContents = False, showApplyButton = True):
        """
        @type menu: QtGui.QMenu
        @type records: list[Record]
        """
        if includeSelectContents:
            self.addSelectContentsAction(menu)
            menu.addSeparator()
        sets = self.plugin().selectionSets()
        for name in sorted(sets.iterkeys()):
            record = studioLibrary.record(sets[name], window=self.window())
            trigger1 = partial(self.selectSelectionSet, record)
            if showApplyButton:
                trigger2 = partial(self.selectSelectionSet, record, True)
            else:
                trigger2 = None
            action = OptionAction(menu, name, callback1=trigger1, callback2=trigger2)
            menu.addAction(action)

        if not menu.actions():
            action = QtGui.QAction('Empty', menu)
            action.setEnabled(False)
            menu.addAction(action)
        menu.addSeparator()

    def contextMenu(self, menu, records):
        """
        @type menu: QtGui.QMenu
        @type records: list[Record]
        """
        self.addSelectContentsAction(menu)
        menu.addSeparator()
        icon = studioLibrary.icon(self.plugin().dirname() + '/images/set.png')
        subMenu = studioLibrary.ContextMenu(menu)
        subMenu.setIcon(icon)
        subMenu.setTitle('Selection Sets')
        self.setsContextMenu(subMenu, records)
        menu.addMenu(subMenu)
        menu.addSeparator()
        studioLibrary.Record.contextMenu(self, menu, records)

    def selectContents(self):
        msg = 'An error has occurred while selecting controls from pose!Please check the script editor for the traceback.'
        try:
            maya.cmds.undoInfo(openChunk=True)
            records = self.window().selectedRecords()
            namespaces = mutils.getNamespaceFromSelection()
            if not namespaces:
                msg = 'Please select at least one object!'
                raise BasePluginError(msg)
            maya.cmds.select(clear=True)
            for record in records:
                record.pose().select(namespace=namespaces, add=True)

        except Exception:
            import traceback
            traceback.print_exc()
            self.window().setError(msg)
        finally:
            maya.cmds.undoInfo(closeChunk=True)


class BaseWidget(QtGui.QWidget):

    def __init__(self, parent = None, record = None):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        QtGui.QWidget.__init__(self, parent)
        studioLibrary.loadUi(self)
        if studioLibrary.isPySide():
            self.layout().setContentsMargins(0, 0, 0, 0)
        self._record = record
        self._thumbnail = ''
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
        if hasattr(self.ui, 'snapshotButton'):
            self.setSnapshot(self.record().icon())
        ctime = self.record().ctime()
        if hasattr(self.ui, 'created') and ctime:
            self.ui.created.setText(studioLibrary.timeAgo(str(ctime)))
        self.loadSettings()
        try:
            self._scriptJob = None
            self._scriptJob = mutils.ScriptJob(e=['SelectionChanged', self.selectionChanged])
            self.selectionChanged()
        except NameError:
            import traceback
            traceback.print_exc()

    def selectionChanged(self):
        """
        """
        pass

    def accept(self):
        """
        """
        pass

    def loadSettings(self):
        """
        """
        pass

    def saveSettings(self):
        """
        """
        pass

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

    def record(self):
        """
        @rtype: Record
        """
        return self._record

    def settings(self):
        """
        @rtype: studioLibrary.Settings
        """
        return self.plugin().settings()

    def updateContains(self, nodes = None):
        """
        @type nodes: list[str]
        """
        if not hasattr(self.ui, 'contains'):
            return
        if nodes is None:
            count = self.record().count()
        else:
            count = len(nodes)
        plural = ''
        if count > 1:
            plural = 's'
        self.ui.contains.setText(str(count) + ' Object' + plural)

    def setSnapshot(self, path):
        """
        @type path: str
        """
        if os.path.exists(path):
            self.ui.snapshotButton.setIcon(QtGui.QIcon(QtGui.QPixmap(path)))
            self.ui.snapshotButton.setIconSize(QtCore.QSize(200, 200))
            self.ui.snapshotButton.setText('')

    def showContextMenu(self, position = None, showApplyButton = True):
        """
        @type position: QPoint
        """
        position = QtGui.QCursor().pos()
        position = self.mapTo(self, position)
        menu = QtGui.QMenu(self)
        self.record().setsContextMenu(menu, self.window().selectedRecords(), includeSelectContents=True, showApplyButton=showApplyButton)
        menu.exec_(position)


class InfoWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        @type args: list[object]
        @type kwargs: dict[object]
        """
        BaseWidget.__init__(self, *args, **kwargs)
        if hasattr(self.ui, 'contains'):
            self.updateContains()


class PreviewWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        @type args: list[object]
        @type kwargs: dict[object]
        """
        super(PreviewWidget, self).__init__(*args, **kwargs)
        if hasattr(self.ui, 'contains'):
            self.updateContains()
        self.connect(self.ui.acceptButton, QtCore.SIGNAL('clicked()'), self.accept)
        self.connect(self.ui.usePoseNamespace, QtCore.SIGNAL('clicked()'), self.stateChanged)
        self.connect(self.ui.useCustomNamespace, QtCore.SIGNAL('clicked()'), self.setUseCustomNamespace)
        self.connect(self.ui.selectionSetButton, QtCore.SIGNAL('clicked()'), self.showContextMenu)
        self.connect(self.ui.useSelectionNamespace, QtCore.SIGNAL('clicked()'), self.stateChanged)
        self.connect(self.ui.namespaceEdit, QtCore.SIGNAL('textEdited (const QString&)'), self.stateChanged)
        self.ui.selectionSetButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.selectionSetButton.customContextMenuRequested.connect(self.showContextMenu)

    def loadSettings(self):
        """
        """
        s = self.settings()
        useNamespace = s.get('namespaceType', NamespaceType.Selection)
        namespaces = s.get('namespaces', [])
        self.ui.namespaceEdit.setText(self.listToString(namespaces))
        if useNamespace == NamespaceType.Pose:
            self.ui.usePoseNamespace.setChecked(True)
        elif useNamespace == NamespaceType.Custom:
            self.ui.useCustomNamespace.setChecked(True)
        else:
            self.ui.useSelectionNamespace.setChecked(True)

    def saveSettings(self):
        """
        """
        s = self.settings()
        if self.ui.usePoseNamespace.isChecked():
            s.set('namespaceType', 'pose')
        elif self.ui.useCustomNamespace.isChecked():
            s.set('namespaceType', 'custom')
        else:
            s.set('namespaceType', 'selection')
        s.set('namespaces', self.stringToList(self.ui.namespaceEdit.text()))
        s.save()

    def listToString(self, data):
        """
        @type data:
        @rtype:
        """
        data = str(data).replace('[', '').replace(']', '')
        data = data.replace("'", '').replace('"', '')
        return data

    def stringToList(self, data):
        """
        @type data:
        @rtype:
        """
        data = '["' + str(data) + '"]'
        data = data.replace(' ', '')
        data = data.replace(',', '","')
        return eval(data)

    def namespaces(self):
        """
        @rtype:
        """
        return self.stringToList(str(self.ui.namespaceEdit.text()))

    def selectionChanged(self):
        """
        """
        namespaces = None
        if self.ui.useSelectionNamespace.isChecked():
            namespaces = mutils.getNamespaceFromSelection()
        elif self.ui.usePoseNamespace.isChecked():
            namespaces = self.record().namespaces()
        if not self.ui.useCustomNamespace.isChecked():
            self.ui.namespaceEdit.setEnabled(False)
            self.ui.namespaceEdit.setText(self.listToString(namespaces))
        else:
            self.ui.namespaceEdit.setEnabled(True)

    def setUseCustomNamespace(self, value = None):
        """
        @type value:
        """
        self.stateChanged(value)
        if self.ui.useCustomNamespace.isChecked():
            self.ui.namespaceEdit.setFocus()

    def stateChanged(self, value = None):
        """
        @type value:
        """
        self.saveSettings()
        self.selectionChanged()


class CreateWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        @type args:
        @type kwargs:
        """
        super(CreateWidget, self).__init__(*args, **kwargs)
        self.connect(self.ui.acceptButton, QtCore.SIGNAL('clicked()'), self.accept)
        self.connect(self.ui.snapshotButton, QtCore.SIGNAL('clicked()'), self.snapshot)
        self.connect(self.ui.selectionSetButton, QtCore.SIGNAL('clicked()'), self.showContextMenu)
        self.ui.selectionSetButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.selectionSetButton.customContextMenuRequested.connect(self.showContextMenu)
        self._thumbnail = None
        self._focusWidget = None
        if hasattr(self.ui, 'name'):
            self.ui.name.setText(self.record().name())
            self._focusWidget = self.ui.name

    def showContextMenu(self, position = None, showApplyButton = False):
        """
        @type position:
        @type showApplyButton: bool
        """
        super(CreateWidget, self).showContextMenu(position, showApplyButton)

    def snapshot(self):
        """
        """
        path = studioLibrary.tempDir(make=True, clean=True)
        self._thumbnail = path + '/thumbnail.jpg'
        try:
            self._thumbnail = mutils.snapshot(path=self._thumbnail)
            self.setSnapshot(self._thumbnail)
        except mutils.SnapshotError as e:
            self.record().window().setError(str(e))

    def showEvent(self, event):
        """
        @type event:
        """
        super(CreateWidget, self).showEvent(event)
        if self._focusWidget:
            self._focusWidget.setFocus()

    def thumbnail(self):
        """
        @rtype:
        """
        return self._thumbnail

    def record(self):
        """
        @rtype: 
        """
        record = BaseWidget.record(self)
        name = str(self.ui.name.text()).strip() or record.name()
        description = str(self.ui.comment.toPlainText())
        try:
            record.set('scene', maya.cmds.file(query=True, sceneName=True) or '')
        except Exception:
            import traceback
            traceback.print_exc()

        record.setName(name)
        record.setDescription(description)
        return record

    def selectionChanged(self):
        """
        """
        selection = maya.cmds.ls(selection=True) or []
        self.updateContains(nodes=selection)

    def accept(self):
        """
        :raise BasePluginError:
        """
        msg = 'An error has occurred while saving! Please check the script editor for the traceback.'
        try:
            if self.record().window().isLocked():
                msg = 'The current library is locked! You cannot save a record when a library has been locked!'
                raise BasePluginError(msg)
            if not str(self.ui.name.text()).strip():
                msg = 'Please specitfy a name!'
                raise BasePluginError(msg)
            if not os.path.exists(self._thumbnail or ''):
                result = self.window().questionDialog('Would you like to take a snapshot?')
                if result == QtGui.QMessageBox.Yes:
                    self.snapshot()
                else:
                    msg = 'Canceled!'
                    raise Exception(msg)
            if not maya.cmds.ls(selection=True):
                msg = 'Please select at least one object for export!'
                raise BasePluginError(msg)
        except BasePluginError:
            self.record().window().setError(msg)
            raise


class OptionAction(QtGui.QWidgetAction):

    def __init__(self, parent, label, callback1, callback2 = None):
        """
        :param parent:
        :param label:
        :param callback1:
        :param callback2:
        """
        QtGui.QWidgetAction.__init__(self, parent)
        self._label = label
        self.setText(label)
        self._callback1 = callback1
        self._callback2 = callback2

    def createWidget(self, parent):
        """
        :param parent:
        :return:
        """
        myWidget = QtGui.QFrame(parent)
        myWidget.setObjectName('mainWidget')
        myLabel = ExtendedLabel(self._label, parent)
        myLabel.setObjectName('myLabel')
        myIcon = ExtendedLabel('Apply', parent)
        myIcon.setObjectName('myOption')
        myLayout = QtGui.QHBoxLayout(myWidget)
        myLayout.setSpacing(0)
        myLayout.setContentsMargins(0, 0, 0, 0)
        myLayout.addWidget(myLabel, stretch=1)
        myLayout.addWidget(myIcon, stretch=0)
        trigger = partial(self.triggerCallback, self)
        myLabel.connect(myLabel, QtCore.SIGNAL('clicked'), trigger)
        if self._callback1:
            myLabel.connect(myLabel, QtCore.SIGNAL('clicked'), self._callback1)
        if self._callback2 is not None:
            trigger2 = partial(self.triggerCallback, self)
            myIcon.connect(myIcon, QtCore.SIGNAL('clicked'), trigger2)
            myIcon.connect(myIcon, QtCore.SIGNAL('clicked'), self._callback2)
        else:
            myIcon.hide()
        return myWidget

    @staticmethod
    def triggerCallback(action):
        """
        :param action:
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
        :param args:
        :param kwargs:
        """
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setFixedHeight(20)

    def mouseReleaseEvent(self, ev):
        """
        :param ev:
        """
        self.emit(QtCore.SIGNAL('clicked'))


if __name__ == '__main__':
    import studioLibrary
    studioLibrary.main(plugins=['examplePlugin'])
