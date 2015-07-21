#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary\gui.py
"""
Released subject to the BSD License
Please visit http://www.voidspace.org.uk/python/license.shtml

Contact: kurt.rathjen@gmail.com
Comments, suggestions and bug reports are welcome.
Copyright (c) 2014, Kurt Rathjen, All rights reserved.

It is a very non-restrictive license but it comes with the usual disclaimer.
This is free software: test it, break it, just don't blame me if it eats your
data! Of course if it does, let me know and I'll fix the problem so that it
doesn't happen to anyone else.

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
import re
import os
import random
import time
try:
    import mutils
except ImportError as msg:
    print msg

import studiolibrary
try:
    from PySide import QtGui
    from PySide import QtCore
    from PySide import QtUiTools
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore

__all__ = ['SequenceTimer',
 'SequenceWidget',
 'MainWindow',
 'WelcomeDialog',
 'LibrarySettings',
 'isControlModifier',
 'ContextMenu',
 'FoldersWidget',
 'RecordsWidget',
 'Action',
 'loadUi']

def loadUi(widget, path = None):
    import inspect
    if not path:
        dirname = os.path.dirname(os.path.abspath(inspect.getfile(widget.__class__)))
        basename = widget.__class__.__name__
        path = dirname + '/ui/' + basename + '.ui'
    if studiolibrary.isPySide():
        loadUiPySide(widget, path)
    else:
        loadUiPyQt4(widget, path)


def loadUiPySide(widget, path = None):
    if os.path.exists(path):
        loader = QtUiTools.QUiLoader()
        loader.setWorkingDirectory(os.path.dirname(path))
        f = QtCore.QFile(path)
        f.open(QtCore.QFile.ReadOnly)
        widget.ui = loader.load(path, widget)
        f.close()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(widget.ui)
        widget.setLayout(layout)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setMinimumWidth(widget.ui.minimumWidth())
        widget.setMinimumHeight(widget.ui.minimumHeight())


def loadUiPyQt4(widget, path = None):
    import PyQt4.uic
    if os.path.exists(path):
        widget.ui = PyQt4.uic.loadUi(path, widget)


def isControlModifier():
    modifiers = QtGui.QApplication.keyboardModifiers()
    return modifiers == QtCore.Qt.ControlModifier


class Action(QtGui.QAction):

    def __init__(self, *args):
        QtGui.QAction.__init__(self, *args)
        self.callback = None
        self.args = []

    def setCallback(self, callback, *args):
        self.callback = callback
        self.args = args
        self.connect(self, QtCore.SIGNAL('triggered(bool)'), self.call)

    def call(self, boolean):
        self.callback(*self.args)


class LibrarySettings(studiolibrary.Settings):

    def __init__(self, name):
        studiolibrary.Settings.__init__(self, 'Library', name)
        self.setdefault('sort', studiolibrary.SortOption.Ordered)
        self.setdefault('showMenu', True)
        self.setdefault('showFolders', True)
        self.setdefault('showPreview', True)
        self.setdefault('showStatus', True)
        self.setdefault('showDeleted', False)
        self.setdefault('showStatus', True)
        self.setdefault('showLabels', True)
        self.setdefault('showStatusDialog', True)
        self.setdefault('tabletMode', False)
        self.setdefault('dockArea', None)
        self.setdefault('foldersState', {})
        self.setdefault('selectedRecords', [])
        self.setdefault('filter', '')
        self.setdefault('sizes', [120, 280, 160])
        self.setdefault('iconSize', 100)
        self.setdefault('geometry', [100,
         100,
         640,
         560])
        self.setdefault('focusBackgroundColor', 'rgb(0, 160, 200, 255)')
        self.setdefault('spacing', 1)
        self.setdefault('kwargs', {})
        defaultBackground = 'DIRNAME/ui/images/background.png'
        self.setdefault('background', defaultBackground)
        background = self.get('background', '')
        if not os.path.exists(background):
            self['background'] = defaultBackground


class PreviewFrame(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)


class DialogFrame(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        studiolibrary.loadUi(self)

    def window(self):
        return self.parent().window()

    def mousePressEvent(self, event):
        self.close()


class PreviewWidget(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        studiolibrary.loadUi(self)

    def window(self):
        return self.parent().window()


class FoldersFrame(QtGui.QFrame):

    def __init__(self, *args):
        QtGui.QFrame.__init__(self, *args)
        studiolibrary.loadUi(self)

    def window(self):
        return self.parent().window()


class InfoFrame(QtGui.QMainWindow):

    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self, parent, QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        studiolibrary.loadUi(self)

    def _show(self, rect):
        QtGui.QMainWindow.show(self)


class AboutDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        studiolibrary.loadUi(self)


class WelcomeDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        studiolibrary.loadUi(self)
        self.ui.cancelButton.clicked.connect(self.close)
        self.ui.browseButton.clicked.connect(self.browse)
        self.setWindowTitle('Studio Library - %s' % studiolibrary.version())
        self._path = ''
        self._directory = ''

    def path(self):
        return self._path

    def setDirectory(self, path):
        self._directory = path

    def browse(self):
        if not self._directory:
            from os.path import expanduser
            self._directory = expanduser('~')
        path = str(QtGui.QFileDialog.getExistingDirectory(None, 'Select a root library', self._directory))
        path = path.replace('\\', '/')
        if path:
            self._path = path
            self.close()


class CheckForUpdatesThread(QtCore.QThread):

    def __init__(self, *args):
        QtCore.QThread.__init__(self, *args)

    def run(self):
        if studiolibrary.isUpdateAvailable():
            self.emit(QtCore.SIGNAL('updateAvailable()'))


class SearchButton(QtGui.QPushButton):

    def __init__(self, *args):
        QtGui.QPushButton.__init__(self, *args)

    def mouseReleaseEvent(self, event):
        self.parent().setFocus()


class SearchWidget(QtGui.QLineEdit):

    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)
        self.setObjectName('searchWidget')
        self.setMinimumWidth(5)
        try:
            margin = self.textMargins()
            margin.setLeft(21)
            self.setTextMargins(margin)
        except:
            print 'studiolibrary: Text margins are not supported!'

        self.pushButton = SearchButton(self)
        self.pushButton.setObjectName('searchButton')
        self.pushButton.move(-3, 3)
        self.pushButton.show()
        pixmap = studiolibrary.pixmap('search', QtGui.QColor(255, 255, 255, 200))
        self.pushButton.setIcon(QtGui.QIcon(QtGui.QPixmap(pixmap)))
        self.setToolTip('Search through the visible items. Use "and", "or" for a more complex filter.')

    def setText(self, text):
        if not str(self.text()).strip() and not str(text).strip():
            text = ''
        QtGui.QLineEdit.setText(self, text)

    def keyPressEvent(self, event):
        if not str(self.text()).strip() and not str(event.text()).strip():
            self.setText('')
            return
        QtGui.QLineEdit.keyPressEvent(self, event)


class ContextMenu(QtGui.QMenu):

    def __init__(self, *args):
        QtGui.QMenu.__init__(self, *args)
        self._menus = []
        self._actions = []

    def actions(self):
        return self._actions

    def insertAction(self, actionBefore, action):
        if str(action.text()) not in self._actions:
            self._actions.append(str(action.text()))
            QtGui.QMenu.insertAction(self, actionBefore, action)

    def addAction(self, action):
        if str(action.text()) not in self._actions:
            self._actions.append(str(action.text()))
            QtGui.QMenu.addAction(self, action)

    def addMenu(self, menu):
        if str(menu.title()) not in self._menus:
            self._menus.append(str(menu.title()))
            QtGui.QMenu.addMenu(self, menu)


statusMSec = 6000

class StatusWidget(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        studiolibrary.loadUi(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setObjectName('statusWidget')
        self.setFixedHeight(18)
        self.setMinimumWidth(5)
        self._timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self._timer, QtCore.SIGNAL('timeout()'), self.clear)

    def setError(self, text, msec = statusMSec):
        icon = studiolibrary.icon('error14', ignoreOverride=True)
        self.ui.button.setIcon(icon)
        self.ui.message.setStyleSheet('color: rgb(222, 0, 0);')
        self.setText(text, msec)

    def setWarning(self, text, msec = statusMSec):
        icon = studiolibrary.icon('warning14', ignoreOverride=True)
        self.ui.button.setIcon(icon)
        self.ui.message.setStyleSheet('color: rgb(222, 180, 0);')
        self.setText(text, msec)

    def setInfo(self, text, msec = statusMSec):
        icon = studiolibrary.icon('info14', ignoreOverride=True)
        self.ui.button.setIcon(icon)
        self.ui.message.setStyleSheet('')
        self.setText(text, msec)

    def setText(self, text, msec = statusMSec):
        if not text:
            self.clear()
        else:
            self.ui.message.setText(text)
            self._timer.stop()
            self._timer.start(msec)

    def clear(self):
        self._timer.stop()
        self.ui.message.setText('')
        self.ui.message.setStyleSheet('')
        icon = studiolibrary.icon('blank', ignoreOverride=True)
        self.ui.button.setIcon(icon)


class Communicate(QtCore.QObject):
    if studiolibrary.isPySide():
        frameChanged = QtCore.Signal(str)
    else:
        frameChanged = QtCore.pyqtSignal(str)


class SequenceTimer(QtCore.QObject):

    def __init__(self, *args):
        QtCore.QObject.__init__(self, *args)
        self._fps = 12
        self._timer = None
        self._frame = 0
        self._frames = []
        self._dirname = None
        self._paused = False
        self.communicate = Communicate()

    def setDirname(self, dirname):
        self._dirname = dirname
        if os.path.isdir(dirname):
            self._frames = [ dirname + '/' + filename for filename in os.listdir(dirname) ]
            self._frames.sort()

    def dirname(self):
        return self._dirname

    def reset(self):
        if not self._timer:
            self._timer = QtCore.QTimer(self.parent())
            self._timer.setSingleShot(False)
            self.connect(self._timer, QtCore.SIGNAL('timeout()'), self._frameChanged)
        if not self._paused:
            self._frame = 0
        self._timer.stop()

    def pause(self):
        self._paused = True
        self._timer.stop()

    def stop(self):
        self._timer.stop()

    def start(self):
        self.reset()
        if self._timer:
            self._timer.start(1000.0 / self._fps)

    def frames(self):
        return self._frames

    def _frameChanged(self):
        if not self._frames:
            return
        self._frame += 1
        if self._frame >= len(self._frames):
            self._frame = 0
        self.communicate.frameChanged.emit(self._frames[self._frame])

    def frameChanged(self, filename):
        pass

    def percent(self):
        if len(self._frames) == self._frame + 1:
            _percent = 1
        else:
            _percent = float(len(self._frames) + self._frame) / len(self._frames) - 1
        return _percent

    def duration(self):
        return len(self._frames)

    def currentFilename(self):
        try:
            return self._frames[self.currentFrame()]
        except IndexError:
            pass

    def currentFrame(self):
        return self._frame

    def setCurrentFrame(self, frame):
        if frame < self.duration():
            self._frame = frame


class SequenceWidget(QtGui.QToolButton):

    def __init__(self, *args):
        QtGui.QToolButton.__init__(self, *args)
        self.setStyleSheet('border: 0px solid rgb(0, 0, 0, 20);')
        self._filename = None
        self._sequenceTimer = SequenceTimer(self)
        self._sequenceTimer.communicate.frameChanged.connect(lambda filename, self = self: self.frameChanged(filename))
        self.setSize(150, 150)
        self.setMouseTracking(True)
        self.setIcon(studiolibrary.icon('thumbnail'))

    def setSize(self, w, h):
        self._size = QtCore.QSize(w, h)
        self.setIconSize(self._size)
        self.setFixedSize(self._size)

    def setDirname(self, dirname):
        self._sequenceTimer.setDirname(dirname)
        if self._sequenceTimer.frames():
            self.setIcon(studiolibrary.icon(self._sequenceTimer.frames()[0]))

    def enterEvent(self, event):
        self._sequenceTimer.start()

    def leaveEvent(self, event):
        self._sequenceTimer.pause()

    def mouseMoveEvent(self, event):
        if isControlModifier():
            percent = 1.0 - float(self.width() - event.pos().x()) / float(self.width())
            frame = int(self._sequenceTimer.duration() * percent)
            self._sequenceTimer.setCurrentFrame(frame)
            self.setIcon(studiolibrary.icon(self._sequenceTimer.currentFilename()))

    def frameChanged(self, filename):
        if not isControlModifier():
            self._filename = filename
            self.setIcon(studiolibrary.icon(filename))

    def paintEvent(self, event):
        QtGui.QToolButton.paintEvent(self, event)
        painter = QtGui.QPainter()
        painter.begin(self)
        if self._filename:
            r = event.rect()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 80, 80)))
            painter.drawRect(r.x(), r.y(), self._sequenceTimer.percent() * r.width() - 1, 2)
        painter.end()


class MainWindow(QtGui.QWidget):

    def __init__(self, name = 'Default', **kwargs):
        QtGui.QWidget.__init__(self, None)
        studiolibrary.loadUi(self)
        self.setObjectName('studiolibrary' + name)
        studiolibrary.analytics().logScreen('Main')
        if studiolibrary.isMaya():
            import maya.cmds
            mayaOS = maya.cmds.about(os=True)
            mayaVersion = maya.cmds.about(v=True)
            aboutMaya = (mayaVersion + '-' + mayaOS).replace(' ', '-')
            studiolibrary.analytics().logEvent('About-Maya', aboutMaya)
        self._name = name
        self._color = 'rgb(245, 245, 0, 255)'
        self._padding = 7
        self._spacing = 0
        self._background = None
        self._backgroundPath = None
        self._pSize = None
        self._pShow = None
        self._dockArea = None
        self._isLocked = False
        self._isLoaded = False
        self._showFolders = False
        self._showDeleted = False
        self._sort = studiolibrary.SortOption.Ordered
        self._showLabelsAction = True
        self._plugins = {}
        self._kwargs = {'name': name}
        self.saveKeywords(kwargs)
        self._mayaDockWidget = None
        self._mayaLayoutWidget = None
        self.ui.infoFrame = InfoFrame(self)
        self.ui.dialogWidget = None
        self.ui.createWidget = None
        self.ui.previewWidget = None
        self.ui.statusWidget = StatusWidget(self)
        self.ui.foldersWidget = FoldersWidget(self)
        self.ui.previewFrame = PreviewFrame(self)
        self.ui.recordsWidget = RecordsWidget(self)
        self.connect(self.ui.updateButton, QtCore.SIGNAL('clicked()'), self.help)
        self.connect(self.ui.createButton, QtCore.SIGNAL('clicked()'), self.showNewMenu)
        self.connect(self.ui.settingsButton, QtCore.SIGNAL('clicked()'), self.showSettingsMenu)
        pixmap = studiolibrary.icon('cog', QtGui.QColor(255, 255, 255, 220), ignoreOverride=True)
        self.ui.settingsButton.setIcon(pixmap)
        pixmap = studiolibrary.icon('addItem', QtGui.QColor(255, 255, 255, 240), ignoreOverride=True)
        self.ui.createButton.setIcon(pixmap)
        self.ui.updateButton.hide()
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.ui.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
        self.ui.splitter.setHandleWidth(1)
        self.ui.splitter.setChildrenCollapsible(False)
        self.ui.viewLayout.insertWidget(1, self.ui.splitter)
        self.ui.splitter.insertWidget(0, self.ui.foldersWidget)
        self.connect(self.ui.foldersWidget, QtCore.SIGNAL('drop'), self.selectRecords)
        self.connect(self.ui.foldersWidget, QtCore.SIGNAL('selectionChanged()'), self.folderSelectionChanged)
        self.ui.splitter.insertWidget(1, self.ui.recordsWidget)
        self.connect(self.ui.recordsWidget, QtCore.SIGNAL('orderChanged()'), self.orderChanged)
        self.connect(self.ui.recordsWidget, QtCore.SIGNAL('itemSelectionChanged()'), self.recordSelectionChanged)
        self._contextMenu = ContextMenu
        vbox = QtGui.QVBoxLayout()
        self.ui.previewFrame.setLayout(vbox)
        self.ui.previewFrame.layout().setSpacing(0)
        self.ui.previewFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.ui.previewFrame.setMinimumWidth(5)
        self.ui.viewLayout.insertWidget(2, self.ui.previewFrame)
        self.ui.splitter.insertWidget(2, self.ui.previewFrame)
        self.ui.statusLayout.addWidget(self.ui.statusWidget)
        self.ui.newMenu = QtGui.QMenu(self)
        self.ui.newMenu.setIcon(studiolibrary.icon('new14'))
        self.ui.newMenu.setTitle('New')
        action = QtGui.QAction(studiolibrary.icon('folder14'), 'Folder', self.ui.newMenu)
        self.connect(action, QtCore.SIGNAL('triggered(bool)'), self.showCreateFolderDialog)
        self.ui.newMenu.addAction(action)
        self.ui.editRecordMenu = ContextMenu(self)
        self.ui.editRecordMenu.setTitle('Edit')
        self.ui.printPrettyAction = QtGui.QAction(studiolibrary.icon('print'), 'Print', self.ui.editRecordMenu)
        action.connect(self.ui.printPrettyAction, QtCore.SIGNAL('triggered(bool)'), self.printPrettyRecords)
        self.ui.editRecordMenu.addAction(self.ui.printPrettyAction)
        self.ui.deleteRecordAction = QtGui.QAction(studiolibrary.icon('trash'), 'Delete', self.ui.editRecordMenu)
        action.connect(self.ui.deleteRecordAction, QtCore.SIGNAL('triggered(bool)'), self.deleteSelectedRecords)
        self.ui.editRecordMenu.addAction(self.ui.deleteRecordAction)
        self.ui.deleteRenameAction = QtGui.QAction(studiolibrary.icon('rename'), 'Rename', self.ui.editRecordMenu)
        action.connect(self.ui.deleteRenameAction, QtCore.SIGNAL('triggered(bool)'), self.renameSelectedRecord)
        self.ui.editRecordMenu.addAction(self.ui.deleteRenameAction)
        self.ui.showRecordAction = QtGui.QAction(studiolibrary.icon('folder14'), 'Show in folder', self.ui.editRecordMenu)
        action.connect(self.ui.showRecordAction, QtCore.SIGNAL('triggered(bool)'), self.openSelectedRecords)
        self.ui.editRecordMenu.addAction(self.ui.showRecordAction)
        self.ui.editFolderMenu = ContextMenu(self)
        self.ui.editFolderMenu.setTitle('Edit')
        action = QtGui.QAction(studiolibrary.icon('trash'), 'Delete', self.ui.editFolderMenu)
        action.connect(action, QtCore.SIGNAL('triggered(bool)'), self.deleteSelectedFolders)
        self.ui.editFolderMenu.addAction(action)
        action = QtGui.QAction(studiolibrary.icon('rename'), 'Rename', self.ui.editFolderMenu)
        action.connect(action, QtCore.SIGNAL('triggered(bool)'), self.renameSelectedFolder)
        self.ui.editFolderMenu.addAction(action)
        action = QtGui.QAction(studiolibrary.icon('folder14'), 'Show in folder', self.ui.editFolderMenu)
        action.connect(action, QtCore.SIGNAL('triggered(bool)'), self.openSelectedFolders)
        self.ui.editFolderMenu.addAction(action)
        self.ui.sortMenu = QtGui.QMenu(self)
        self.ui.sortMenu.setTitle('Sort by')
        self._sortNameAction = QtGui.QAction('Name', self.ui.sortMenu)
        self._sortNameAction.setCheckable(True)
        self.connect(self._sortNameAction, QtCore.SIGNAL('triggered(bool)'), self.setSortName)
        self.ui.sortMenu.addAction(self._sortNameAction)
        self._sortModifiedAction = QtGui.QAction('Modified', self.ui.sortMenu)
        self._sortModifiedAction.setCheckable(True)
        self.connect(self._sortModifiedAction, QtCore.SIGNAL('triggered(bool)'), self.setSortModified)
        self.ui.sortMenu.addAction(self._sortModifiedAction)
        self._sortOrderedAction = QtGui.QAction('Ordered', self.ui.sortMenu)
        self._sortOrderedAction.setCheckable(True)
        self.connect(self._sortOrderedAction, QtCore.SIGNAL('triggered(bool)'), self.setSortOrdered)
        self.ui.sortMenu.addAction(self._sortOrderedAction)
        self.ui.settingsMenu = QtGui.QMenu(self)
        self.ui.settingsMenu.setIcon(studiolibrary.icon('settings14'))
        self.ui.settingsMenu.setTitle('Settings')
        self._librariesMenu = QtGui.QMenu(self)
        self._librariesMenu.setTitle('Libraries')
        self.ui.settingsMenu.addMenu(self._librariesMenu)
        self.ui.settingsMenu.addSeparator()
        self._showMenuAction = QtGui.QAction('Show menu', self.ui.settingsMenu)
        self._showMenuAction.setCheckable(True)
        self.connect(self._showMenuAction, QtCore.SIGNAL('triggered(bool)'), self.showMenu)
        self.ui.settingsMenu.addAction(self._showMenuAction)
        self._showFoldersAction = QtGui.QAction('Show folders', self.ui.settingsMenu)
        self._showFoldersAction.setCheckable(True)
        self.connect(self._showFoldersAction, QtCore.SIGNAL('triggered(bool)'), self.showFolders)
        self.ui.settingsMenu.addAction(self._showFoldersAction)
        self._showPreviewAction = QtGui.QAction('Show preview', self.ui.settingsMenu)
        self._showPreviewAction.setCheckable(True)
        self.connect(self._showPreviewAction, QtCore.SIGNAL('triggered(bool)'), self.showPreview)
        self.ui.settingsMenu.addAction(self._showPreviewAction)
        self._showStatusAction = QtGui.QAction('Show status', self.ui.settingsMenu)
        self._showStatusAction.setCheckable(True)
        self.connect(self._showStatusAction, QtCore.SIGNAL('triggered(bool)'), self.showStatus)
        self.ui.settingsMenu.addAction(self._showStatusAction)
        self._showStatusDialogAction = QtGui.QAction('Show dialogs', self.ui.settingsMenu)
        self._showStatusDialogAction.setCheckable(True)
        self.connect(self._showStatusDialogAction, QtCore.SIGNAL('triggered(bool)'), self.showStatusDialog)
        self.ui.settingsMenu.addAction(self._showStatusDialogAction)
        self.ui.settingsMenu.addSeparator()
        self._setTabletModeAction = QtGui.QAction('Tablet mode', self.ui.settingsMenu)
        self._setTabletModeAction.setCheckable(True)
        self.connect(self._setTabletModeAction, QtCore.SIGNAL('triggered(bool)'), self.reloadStyle)
        self.ui.settingsMenu.addAction(self._setTabletModeAction)
        self._showLabelsAction = QtGui.QAction('Show labels', self.ui.settingsMenu)
        self._showLabelsAction.setCheckable(True)
        self.connect(self._showLabelsAction, QtCore.SIGNAL('triggered(bool)'), self.showLabels)
        self.ui.settingsMenu.addAction(self._showLabelsAction)
        self._showSpacingAction = QtGui.QAction('Show spacing', self.ui.settingsMenu)
        self._showSpacingAction.setCheckable(True)
        self.connect(self._showSpacingAction, QtCore.SIGNAL('triggered(bool)'), self.showSpacing)
        self.ui.settingsMenu.addAction(self._showSpacingAction)
        if studiolibrary.isMaya():
            self.ui.settingsMenu.addSeparator()
            self._dockLeftAction = QtGui.QAction('Dock left', self.ui.settingsMenu)
            self.connect(self._dockLeftAction, QtCore.SIGNAL('triggered(bool)'), self.dockLeft)
            self.ui.settingsMenu.addAction(self._dockLeftAction)
            self._dockRightAction = QtGui.QAction('Dock right', self.ui.settingsMenu)
            self.connect(self._dockRightAction, QtCore.SIGNAL('triggered(bool)'), self.dockRight)
            self.ui.settingsMenu.addAction(self._dockRightAction)
        self.ui.settingsMenu.addSeparator()
        self._showSettingsAction = QtGui.QAction('Change root', self.ui.settingsMenu)
        self.connect(self._showSettingsAction, QtCore.SIGNAL('triggered(bool)'), self.browseAndSetRootPath)
        self.ui.settingsMenu.addAction(self._showSettingsAction)
        self._changeColorAction = QtGui.QAction('Change color', self.ui.settingsMenu)
        self.connect(self._changeColorAction, QtCore.SIGNAL('triggered(bool)'), self.changeColor)
        self.ui.settingsMenu.addAction(self._changeColorAction)
        separator = QtGui.QAction('', self.ui.settingsMenu)
        separator.setSeparator(True)
        self.ui.settingsMenu.addAction(separator)
        self._resetPreferenceAction = QtGui.QAction('Save settings', self.ui.settingsMenu)
        self.connect(self._resetPreferenceAction, QtCore.SIGNAL('triggered(bool)'), self.saveSettings)
        self.ui.settingsMenu.addAction(self._resetPreferenceAction)
        self._changeBackgroundAction = QtGui.QAction('Reset settings', self.ui.settingsMenu)
        self.connect(self._changeBackgroundAction, QtCore.SIGNAL('triggered(bool)'), self.resetSettings)
        self.ui.settingsMenu.addAction(self._changeBackgroundAction)
        separator = QtGui.QAction('', self.ui.settingsMenu)
        separator.setSeparator(True)
        self.ui.settingsMenu.addAction(separator)
        if studiolibrary.isMaya():
            self._showDebugAction = QtGui.QAction('Debug mode', self.ui.settingsMenu)
            self._showDebugAction.setCheckable(True)
            self._showDebugAction.setChecked(False)
            self.connect(self._showDebugAction, QtCore.SIGNAL('triggered(bool)'), self.showDebug)
            self.ui.settingsMenu.addAction(self._showDebugAction)
        self._helptAction = QtGui.QAction('Help', self.ui.settingsMenu)
        self.connect(self._helptAction, QtCore.SIGNAL('triggered(bool)'), self.help)
        self.ui.settingsMenu.addAction(self._helptAction)
        self.reloadFolders()
        self.updateThread = CheckForUpdatesThread(self)
        self.connect(self.updateThread, QtCore.SIGNAL('updateAvailable()'), self.setUpdateAvailable)
        self.updateThread.start()
        self.updateSettingsMenu()
        self.updateWindowTitle()
        self.shcut1 = QtGui.QShortcut(self)
        self.shcut1.setKey('Ctrl+f')
        self.connect(self.shcut1, QtCore.SIGNAL('activated()'), self.setFilterFocus)

    def setUpdateAvailable(self):
        self.ui.updateButton.show()

    def informationDialog(self, message, title = 'Information'):
        return QtGui.QMessageBox.information(self, title, str(message))

    def criticalDialog(self, message, title = 'Error'):
        return QtGui.QMessageBox.critical(self, title, str(message))

    def warningDialog(self, message, title = 'Warning'):
        return QtGui.QMessageBox.warning(self, title, str(message))

    def questionDialog(self, message, title = 'Question'):
        return QtGui.QMessageBox.question(self, title, str(message), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)

    def setError(self, text, msec = statusMSec):
        self.ui.statusWidget.setError(text, msec=msec)
        if self.isShowStatusDialog():
            self.criticalDialog(text)
        else:
            self.showStatus(True)

    def setWarning(self, text, msec = statusMSec):
        self.ui.statusWidget.setWarning(text, msec=msec)
        if self.isShowStatusDialog():
            self.warningDialog(text)
        else:
            self.showStatus(True)

    def isShowStatusDialog(self):
        return self._showStatusDialogAction.isChecked()

    def showStatusDialog(self, v):
        self._showStatusDialogAction.setChecked(v)

    def setInfo(self, text, msec = statusMSec):
        self.ui.statusWidget.setInfo(text, msec=msec)

    def event(self, event):
        if isinstance(event, QtGui.QStatusTipEvent):
            self.ui.statusWidget.setInfo(event.tip())
        return QtGui.QWidget.event(self, event)

    def updateWindowTitle(self):
        if self.isDocked():
            title = 'Studio Library - ' + self.name()
        else:
            title = 'Studio Library - ' + studiolibrary.__version__ + ' - ' + self.name()
        if self.isLocked():
            title += ' (Locked)'
        self.setWindowTitle(title)
        if studiolibrary.isMaya() and self._mayaDockWidget:
            import maya.cmds
            maya.cmds.dockControl(self._mayaDockWidget, edit=True, label=title)

    def setLocked(self, value):
        if value:
            self.ui.createButton.setEnabled(True)
            self.ui.createButton.setIcon(studiolibrary.icon('lock', QtGui.QColor(222, 222, 222, 222), ignoreOverride=True))
        else:
            self.ui.createButton.setEnabled(True)
            self.ui.createButton.setIcon(studiolibrary.icon('addItem', ignoreOverride=True))
            self.ui.createButton.show()
        self._isLocked = value
        self.updateWindowTitle()

    def kwargs(self):
        return self._kwargs

    def isLocked(self):
        return self._isLocked

    def setContextMenu(self, menu):
        self._contextMenu = menu

    def contextMenu(self, parent):
        return self._contextMenu(parent)

    def leaveEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def window(self):
        return self

    def isDocked(self):
        if studiolibrary.isMaya():
            import maya.cmds
            if self._mayaDockWidget:
                return not maya.cmds.dockControl(self._mayaDockWidget, query=True, floating=True)
        return False

    def dockArea(self):
        if not self.parent():
            return None
        return self._dockArea

    def dockLocationChanged(self, area):
        if studiolibrary.isPySide():
            if area == QtCore.Qt.DockWidgetArea.RightDockWidgetArea:
                self._dockArea = 2
            elif area == QtCore.Qt.DockWidgetArea.LeftDockWidgetArea:
                self._dockArea = 1
        else:
            self._dockArea = area
        self.updateWindowTitle()
        self.parentX().setMinimumWidth(15)

    def topLevelChanged(self, value):
        if value:
            self._dockArea = None
        self.updateWindowTitle()
        self.parentX().setMinimumWidth(15)

    def raiseWindow(self):
        if studiolibrary.isMaya() and self._mayaDockWidget:
            import maya.cmds
            maya.cmds.dockControl(self._mayaDockWidget, edit=True, visible=True, r=True)

    def dockLeft(self):
        self.setDockArea(1, self.width(), edit=True)

    def dockRight(self):
        self.setDockArea(2, self.width(), edit=True)

    def deleteDockWidget(self):
        if mutils.isMaya():
            import maya.cmds
            if maya.cmds.dockControl(str(self._mayaDockWidget), q=1, ex=1):
                maya.cmds.deleteUI(str(self._mayaDockWidget))
                self._mayaDockWidget = None
            if maya.cmds.columnLayout(str(self._mayaLayoutWidget), q=1, ex=1):
                maya.cmds.deleteUI(str(self._mayaLayoutWidget))
                self._mayaLayoutWidget = None

    def floating(self):
        if studiolibrary.isMaya():
            import maya.cmds
            if maya.cmds.dockControl(str(self.objectName()), q=1, ex=1):
                maya.cmds.dockControl(str(self.objectName()), e=1, fl=1)

    def setDockArea(self, dockArea = None, width = None, edit = False):
        self._dockArea = dockArea
        allowedAreas = ['right', 'left']
        if dockArea == 1:
            area = 'left'
            floating = False
        elif dockArea == 2:
            area = 'right'
            floating = False
        else:
            area = 'left'
            floating = True
        if studiolibrary.isMaya():
            import maya.cmds
            if not self._mayaDockWidget:
                self.deleteDockWidget()
                if not self._mayaLayoutWidget:
                    self._mayaLayoutWidget = maya.cmds.columnLayout(parent=str(self.objectName()))
                maya.cmds.layout(self._mayaLayoutWidget, edit=True, visible=False)
                self._mayaDockWidget = maya.cmds.dockControl(area=area, floating=False, r=True, content=str(self.objectName()), allowedArea=allowedAreas, width=15)
                self.connect(self.parent(), QtCore.SIGNAL('topLevelChanged(bool)'), self.topLevelChanged)
                self.connect(self.parent(), QtCore.SIGNAL('dockLocationChanged(Qt::DockWidgetArea)'), self.dockLocationChanged)
            self.updateWindowTitle()
            maya.cmds.dockControl(self._mayaDockWidget, edit=True, r=True, area=area, floating=floating, width=width)

    def folderSelectionChanged(self):
        self.reloadRecords()

    def closeDialogEvent(self, event):
        QtGui.QMainWindow.closeEvent(self, event)
        self.ui.dialogFrame.close()

    def showDialog(self, widget):
        if self._dialogWidget:
            self._dialogWidget.close()
        self._dialogWidget = widget
        self._dialogWidget.closeEvent = self.closeDialogEvent
        d = self.ui.dialogFrame
        d.ui.centerFrame.setMaximumSize(widget.maximumSize())
        d.ui.centerFrame.layout().addWidget(widget)
        widget.setParent(d.ui.centerFrame)
        self.ui.dialogFrame.show()

    def isShowLabels(self):
        return self.ui.recordsWidget.isShowLabels()

    def changeColor(self):
        color = self.settings().get('focusBackgroundColor')
        d = QtGui.QColorDialog(self)
        d.connect(d, QtCore.SIGNAL('currentColorChanged (const QColor&)'), self.setColor)
        d.open()
        if d.exec_():
            self.setColor(d.selectedColor())
            self.saveSettings()
        else:
            self.setColor(color)

    def changeBackground(self):
        path, extension = QtGui.QFileDialog.getOpenFileName(self, 'Select an image', '', '*.png')
        path = path.replace('\\', '/')
        if path:
            self.setBackground(path)

    def reloadStyle(self):

        def __decode(value):
            return value.decode('base64')

        def __encode(value):
            return value.encode('base64')

        style = studiolibrary.dirname() + '/style.qss'
        style2 = studiolibrary.dirname() + '/style.qssx'
        if os.path.exists(style):
            f = open(style, 'r')
            data = f.read()
            f.close()
            data = __encode(data)
            f = open(style2, 'w')
            f.write(data)
            f.close()
            data = __decode(data)
        else:
            data = __decode(_data)
        data = data.replace('DIRNAME', studiolibrary.dirname())
        data = data.replace('FOCUSBACKGROUNDCOLOR', self.color())
        data = data.replace('FOREGROUNDCOLOR', 'rgb(255, 255, 255)')
        data = data.replace('BACKGROUNDCOLOR', 'rgb(60, 60, 60)')
        data = data.replace('FOCUSCOLOR', 'rgb(240, 240, 240)')
        data = data.replace('COLOR', 'rgb(220, 220, 220)')
        if self.isTabletMode():
            data = data.replace('SCROLL_BAR_WIDTH', '16')
        else:
            data = data.replace('SCROLL_BAR_WIDTH', '8')
        spacing = self.spacing()
        if spacing == 0 or spacing == 1:
            border = '0'
        else:
            border = '1'
        data = data.replace('BORDER', border)
        data = data.replace('PADDING', str(self._padding))
        data = data.replace('SPACING', str(self.spacing()))
        if False:
            color = self.QColor()
            pixmap = studiolibrary.icon('addItem', color)
            self.ui.createButton.setIcon(pixmap)
        QtGui.QMainWindow.setStyleSheet(self, data)

    def setColor(self, color, force = True):
        if color is None:
            return
        if isinstance(color, QtGui.QColor):
            color = 'rgb(%d, %d, %d, %d)' % color.getRgb()
        self._color = color
        if force:
            self.reloadStyle()

    def QColor(self):
        color = self.color()
        a = 255
        try:
            r, g, b, a = color.replace('rgb(', '').replace(')', '').split(',')
        except:
            r, g, b = color.replace('rgb(', '').replace(')', '').split(',')

        return QtGui.QColor(int(r), int(g), int(b), int(a))

    def color(self):
        return self._color

    def spacing(self):
        return self._spacing

    def showSpacing(self, value):
        if value:
            self.setSpacing(5)
        else:
            self.setSpacing(1)

    def setSpacing(self, value, force = True):
        if value > 1:
            value = value
            self._showSpacingAction.setChecked(True)
        else:
            value = 1
            self._showSpacingAction.setChecked(False)
        self._spacing = value
        self.ui.recordsWidget.setSpacing(value)
        if force:
            self.reloadStyle()

    def selectedFolders(self):
        self.ui.foldersWidget.selectedFolders()

    def delete(self):
        self.deleteDockWidget()
        self.deleteSettings(load=False)
        studiolibrary.removeWindow(self.name())

    def setName(self, name):
        self._name = name

    def name(self):
        return self._name

    def settings(self):
        return studiolibrary.LibrarySettings(self.name())

    def openSelectedFolders(self):
        folders = self.selectedFolders()
        for folder in folders:
            folder.openLocation()

    def openSelectedRecords(self):
        records = self.selectedRecords()
        for record in records:
            record.openLocation()

        if not records:
            for folder in self.selectedFolders():
                folder.openLocation()

    def renameSelectedRecord(self):
        self.ui.recordsWidget.renameSelected()

    def printPrettyRecords(self):
        for r in self.ui.recordsWidget.selectedRecords():
            r.prettyPrint()

    def renameSelectedFolder(self):
        self.ui.foldersWidget.renameSelected()

    def restoreSelectedRecords(self):
        for record in self.selectedRecords():
            record.restore()

    def parentX(self):
        return self.parent() or self

    def loadSettings(self, ignoreWindowSettings = False):
        self.setRoot(self.kwargs().get('root', ''))
        settings = self.settings()
        try:
            self.setColor(settings.get('focusBackgroundColor'), force=False)
            self.setSpacing(settings.get('spacing'), force=False)
            self.showMenu(settings.get('showMenu'))
            self.showFolders(settings.get('showFolders'))
            self.showPreview(settings.get('showPreview'))
            self.showStatusDialog(settings.get('showStatusDialog'))
            self.showStatus(settings.get('showStatus'))
            self.showDeleted(settings.get('showDeleted'), force=False)
            self.showLabels(settings.get('showLabels'))
            self._setTabletModeAction.setChecked(settings.get('isTabletMode', False))
            self.reloadStyle()
            self.setSort(settings.get('sort'), force=False)
            self.ui.recordsWidget.setViewSize(settings.get('iconSize'))
            self.setFilter(settings.get('filter'))
            background = settings.get('background')
            background = background.replace('DIRNAME', studiolibrary.dirname())
            self.setBackground(background)
        except:
            self.parentX().move(100, 100)
            self.setError('An error has occurred while loading settings! Please check the script editor for the traceback.')
            import traceback
            traceback.print_exc()

        try:
            fSize, cSize, pSize = settings.get('sizes')
            if pSize == 0:
                pSize = 200
            if fSize == 0:
                fSize = 120
            self.ui.splitter.setSizes([fSize, cSize, pSize])
            self.ui.splitter.setStretchFactor(1, 1)
            if not ignoreWindowSettings:
                x, y, width, height = settings.get('geometry')
                if width == 0:
                    width = fSize + cSize + pSize
                dockArea = settings.get('dockArea')
                self.setDockArea(dockArea, width=width)
                if not self.isDocked():
                    self.parentX().setGeometry(x, y, width, height)
                self.parentX().setMinimumWidth(15)
        except:
            self.parentX().move(100, 100)
            self.setError('An error has occurred while loading settings! Please check the script editor for the traceback.')
            import traceback
            traceback.print_exc()
            raise

        self.loadPlugins(self.kwargs().get('plugins', []))
        self.ui.foldersWidget.restoreState(settings.get('foldersState'))
        self.selectRecords(settings.get('selectedRecords'))

    def resetSettings(self):
        try:
            kwargs = self.kwargs()
            s = LibrarySettings('None')
            settings = self.settings()
            settings.update(s)
            settings.save()
            self.saveKeywords(kwargs)
            self.loadSettings()
            self.clearSelection()
        except:
            import traceback
            traceback.print_exc()

    def deleteSettings(self, load = True):
        settings = self.settings()
        settings.delete()
        if load:
            self.loadSettings()
            self.clearSelection()

    def saveSettings(self):
        if not self.isLoaded():
            return
        try:
            geometry = (self.parentX().geometry().x(),
             self.parentX().geometry().y(),
             self.parentX().geometry().width(),
             self.parentX().geometry().height())
            settings = self.settings()
            settings.set('geometry', geometry)
            settings.set('sort', self._sort)
            settings.set('showLabels', self._showLabelsAction.isChecked())
            settings.set('showMenu', self._showMenuAction.isChecked())
            settings.set('showFolders', self._showFoldersAction.isChecked())
            settings.set('showPreview', self._showPreviewAction.isChecked())
            settings.set('showStatus', self._showStatusAction.isChecked())
            settings.set('showStatusDialog', self._showStatusDialogAction.isChecked())
            settings.set('spacing', self.spacing())
            settings.set('isTabletMode', self._setTabletModeAction.isChecked())
            settings.set('foldersState', self.ui.foldersWidget.currentState())
            settings.set('selectedRecords', [ record.dirname() for record in self.selectedRecords() ])
            settings.set('iconSize', self.ui.recordsWidget.viewSize())
            settings.set('sizes', self.ui.splitter.sizes())
            settings.set('focusBackgroundColor', self._color)
            settings.set('dockArea', self._dockArea)
            settings.set('kwargs', self.kwargs())
            if self._backgroundPath:
                settings.set('background', self._backgroundPath)
            settings.save()
        except:
            import traceback
            traceback.print_exc()

    def setBackground(self, path):
        pass

    def orderChanged(self):
        folders = self.selectedFolders()
        if len(folders) == 1:
            folder, = folders
            order = []
            for record in self.ui.recordsWidget.model().records():
                order.append(record.name())

            folder.setOrder(order)

    def recordSelectionChanged(self):
        records = self.selectedRecords()
        if self._pShow is not None and records:
            self.showPreview(self._pShow)
            self._pShow = None
        if self._pSize and records:
            fSize, cSize, pSize = self.ui.splitter.sizes()
            self.ui.splitter.setSizes([fSize, cSize, self._pSize])
            self._pSize = None
        if not records:
            self.clearPreviewWidget()

    def clearPreviewWidget(self):
        widget = PreviewWidget(None)
        self.setPreviewWidget(widget)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F5:
            self.reloadFolders()
        QtGui.QWidget.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        for record in self.selectedRecords():
            record.keyReleaseEvent(event)

        QtGui.QWidget.keyReleaseEvent(self, event)

    def setFilterFocus(self):
        pass

    def isLoaded(self):
        return self._isLoaded

    def showEvent(self, event):
        if not self._isLoaded:
            self.move(-50000, -50000)
        QtGui.QWidget.showEvent(self, event)
        try:
            if not self._isLoaded:
                self.loadSettings()
                self._isLoaded = True
        except:
            import traceback
            traceback.print_exc()

        if self._isLoaded:
            g = self.geometry()
            if g.x() < 0 or g.y() < 0:
                self.parentX().move(100, 100)

    def closeEvent(self, event):
        if self.isLoaded():
            self.saveSettings()
        QtGui.QWidget.closeEvent(self, event)

    def showMessage(self, text, repaint = True):
        self.ui.recordsWidget.showMessage(text, repaint=repaint)

    def resizeEvent(self, event):
        QtGui.QWidget.resizeEvent(self, event)

    def updateLayout(self):
        pass

    def browseRootFolder(self, root = '', msg = 'Please browse to change the current Studio Library root folder.'):
        dialog = WelcomeDialog(self)
        if not root:
            root = self.root()
        dialog.ui.heading.setText('Root Folder: %s' % root)
        dialog.ui.content.setText(msg)
        dialog.setDirectory(root)
        result = dialog.exec_()
        path = dialog.path()
        if not os.path.exists(path):
            raise Exception('Cannot find the root folder path \'%s\'. To set the root folder please use the command: studiolibrary.main(root="C:/path")' % path)
        return path

    def browseAndSetRootPath(self):
        path = self.browseRootFolder()
        self.setRoot(path)
        self.saveKeywords(self.kwargs())

    def root(self):
        return self.kwargs().get('root', '')

    def setRoot(self, path):
        if not os.path.exists(path):
            path = self.browseRootFolder(root=path, msg="Cannot find the root folder '%s'! Please choose a new root folder for storing the data." % path)
        self.kwargs()['root'] = path
        self.clearRecords()
        self.clearPreviewWidget()
        self.ui.foldersWidget.setRoot(path)

    def setCreateWidget(self, widget):
        if widget and not self._pSize:
            fSize, cSize, pSize = self.ui.splitter.sizes()
            self._pSize = pSize
            self._pShow = self.isShowPreview()
            self.ui.splitter.setSizes([fSize, cSize, widget.minimumWidth()])
        self.showPreview(True)
        self.ui.recordsWidget.clearSelection()
        self.setPreviewWidget(widget)

    def setPreviewWidget(self, widget):
        if self.ui.previewWidget != widget:
            for i in range(self.ui.previewFrame.layout().count()):
                widget2 = self.ui.previewFrame.layout().itemAt(i).widget()
                self.ui.previewFrame.layout().removeWidget(widget2)
                widget2.setParent(self)
                widget2.hide()
                widget2.close()
                widget2.destroy()
                del widget2

        self.ui.previewWidget = widget
        if self.isShowPreview():
            if self.ui.previewWidget:
                self.ui.previewFrame.layout().addWidget(self.ui.previewWidget)
                self.ui.previewWidget.show()

    def selectRecords(self, records):
        self.ui.recordsWidget.selectRecords(records)

    def selectFolders(self, folders):
        self.ui.foldersWidget.selectFolders(folders)

    def clearSelection(self):
        self.ui.foldersWidget.clearSelection()

    def selectedRecords(self):
        return self.ui.recordsWidget.selectedRecords()

    def selectedFolders(self):
        return self.ui.foldersWidget.selectedFolders()

    def setViewMode(self, mode):
        return self.ui.recordsWidget.setViewMode(mode)

    def viewMode(self):
        return self.ui.recordsWidget.viewMode()

    def sort(self):
        return self._sort

    def setSort(self, sort, force = True):
        self._sort = sort
        if sort == studiolibrary.SortOption.Ordered:
            self.ui.recordsWidget.setDropEnabled(True)
        else:
            self.ui.recordsWidget.setDropEnabled(False)
        self._sortNameAction.setChecked(studiolibrary.SortOption.Name == sort)
        self._sortOrderedAction.setChecked(studiolibrary.SortOption.Ordered == sort)
        self._sortModifiedAction.setChecked(studiolibrary.SortOption.Modified == sort)
        if force:
            self.reloadRecords()

    def setSortName(self):
        self.setSort(studiolibrary.SortOption.Name)

    def setSortModified(self):
        self.setSort(studiolibrary.SortOption.Modified)

    def setSortOrdered(self):
        self.setSort(studiolibrary.SortOption.Ordered)

    def plugins(self):
        return self._plugins

    def plugin(self, name):
        return self.plugins().get(name, None)

    def unloadPlugins(self):
        for name, plugin in self._plugins.items():
            self.unloadPlugin(name)

    def unloadPlugin(self, name):
        plugin = self._plugins.get(name, None)
        if plugin:
            studiolibrary.unloadPlugin(plugin)
            del self._plugins[name]
        else:
            print "Cannot find plugin with name '%s'" % name

    def loadPlugin(self, name):
        if name not in self._plugins.keys():
            plugin = studiolibrary.loadPlugin(name, self)
            self._plugins.setdefault(name, plugin)
        return self._plugins.get(name)

    def loadPlugins(self, plugins):
        for name in plugins:
            self.loadPlugin(name)

    def reloadFolders(self):
        self.ui.foldersWidget.reload()

    def clearRecords(self):
        self.ui.recordsWidget.clear()

    def reloadRecords(self):
        t = time.time()
        records = []
        selectedRecords = self.selectedRecords()
        folders = self.ui.foldersWidget.selectedFolders()
        if not folders:
            self.ui.recordsWidget.clear()
        for folder in folders:
            records.extend(folder.records(sort=self.sort(), deleted=self.isShowDeleted(), parent=self.ui.recordsWidget))
            self.ui.recordsWidget.setRecords(records)

        if selectedRecords:
            self.selectRecords(selectedRecords)
        if self.selectedRecords() != selectedRecords:
            self.recordSelectionChanged()
        self.setLoadedMessage(t)

    def setLoadedMessage(self, t):
        recordCount = self.ui.recordsWidget.model().recordsCount()
        hiddenCount = self.ui.recordsWidget.model().hiddenRecordsCount()
        t = time.time() - t
        plural = ''
        if recordCount != 1:
            plural = 's'
        hiddenText = ''
        if hiddenCount > 0:
            hiddenText = '%d items hidden.' % hiddenCount
        self.ui.statusWidget.setInfo('Loaded %s item%s in %0.3f seconds. %s' % (recordCount,
         plural,
         t,
         hiddenText))

    def help(self):
        studiolibrary.analytics().logScreen('Help')
        import webbrowser
        webbrowser.open('http://www.studiolibrary.com')

    def deleteSelectedRecords(self):
        records = self.ui.recordsWidget.selectedRecords()
        if records:
            result = self.window().questionDialog('Are you sure you want to delete the selected record/s %s' % [ r.name() for r in records ])
            if result == QtGui.QMessageBox.Yes:
                for record in records:
                    record.delete()

                self.reloadRecords()

    def deleteSelectedFolders(self):
        self.ui.foldersWidget.deleteSelected()

    def filter(self):
        return str(self.ui.searchWidget.text()).strip()

    def setFilter(self, text):
        t = time.time()
        records = self.ui.recordsWidget.selectedRecords()
        self.ui.recordsWidget.model().setFilter(str(text))
        self.selectRecords(records)
        self.setLoadedMessage(t)
        if not self.ui.recordsWidget.selectedRecords():
            self.clearPreviewWidget()

    def showNewMenu(self):
        if not self.isLocked():
            point = self.ui.createButton.rect().bottomLeft()
            point = self.ui.createButton.mapToGlobal(point)
            self.ui.newMenu.exec_(point)

    def saveKeywords(self, kwargs = None):
        settings = self.settings()
        self._kwargs = kwargs or {}
        if not kwargs.get('root', None):
            self._kwargs['root'] = settings.get('kwargs', {}).get('root', '')
        if not kwargs.get('plugins', None):
            self._kwargs['plugins'] = settings.get('kwargs', {}).get('plugins', [])
        settings['kwargs'] = self._kwargs
        settings.save()
        self.fixKeywordPluginSettings(settings)

    @staticmethod
    def fixKeywordPluginSettings(settings):
        """
        This method will fix an issue when upgrading to 1.6.
        When upgrading the old plugin names are still stored,
        so the setting need to reflect the new naming convention.
        """
        dirty = False
        plugins = settings.get('kwargs', {}).get('plugins', [])
        oldplugins = ['posePlugin',
         'animationPlugin',
         'mirrorTablePlugin',
         'selectionSetPlugin',
         'lockPlugin']
        for p in plugins:
            if p in oldplugins:
                dirty = True
                i = plugins.index(p)
                plugins[i] = 'studiolibraryplugins.' + p.lower()

        if dirty:
            settings['kwargs']['plugins'] = plugins
            settings.save()

    def loadLibrary(self, name, kwargs = None):
        for a in self._libraryActions:
            if str(a.text()) == name:
                a.setChecked(True)
            else:
                a.setChecked(False)

        self.saveSettings()
        self.unloadPlugins()
        self.setName(name)
        if kwargs is None:
            kwargs = self.settings().get('kwargs', {})
        self.saveKeywords(kwargs)
        self.updateWindowTitle()
        self.loadSettings(ignoreWindowSettings=True)

    def showSortMenu(self):
        point = self.ui.sortButton.rect().bottomLeft()
        point = self.ui.sortButton.mapToGlobal(point)
        self.ui.sortMenu.exec_(point)

    def updateSettingsMenu(self):
        self._libraryActions = []
        self._librariesMenu.clear()
        for name in studiolibrary.libraries():
            action = Action(name, self._librariesMenu)
            action.setCallback(self.loadLibrary, name)
            action.setCheckable(True)
            if self.name() == name:
                action.setChecked(True)
            self._libraryActions.append(action)
            self._librariesMenu.addAction(action)

    def showSettingsMenu(self):
        point = self.ui.settingsButton.rect().bottomRight()
        point = self.ui.settingsButton.mapToGlobal(point)
        self.updateSettingsMenu()
        self.ui.settingsMenu.show()
        point.setX(point.x() - self.ui.settingsMenu.width())
        action = self.ui.settingsMenu.exec_(point)

    def isShowDeleted(self):
        pass

    def showDeleted(self, value, force = True):
        pass

    def isShowFolders(self):
        return self._showFoldersAction.isChecked()

    def setSplitterWidth(self, index, width):
        size = self.ui.splitter.sizes()
        size[index] = width
        self.ui.splitter.setSizes(size)

    def showFolders(self, value):
        if value:
            self.ui.foldersWidget.show()
        else:
            self.ui.foldersWidget.hide()
        self.updateLayout()
        self._showFoldersAction.setChecked(value)

    def showPreview(self, value):
        if value:
            if not self.ui.previewFrame.isVisible():
                self.ui.previewFrame.show()
                if self.ui.previewWidget:
                    self.setPreviewWidget(self.ui.previewWidget)
        else:
            self.ui.previewFrame.hide()
        self._showPreviewAction.setChecked(value)

    def showStatus(self, value):
        if value:
            if not self.ui.statusWidget.isVisible():
                self.ui.statusWidget.show()
        else:
            self.ui.statusWidget.hide()
        self._showStatusAction.setChecked(value)

    def isTabletMode(self):
        return bool(self._setTabletModeAction.isChecked())

    def showMenu(self, value):
        if value:
            self.ui.menuFrame.show()
        else:
            self.ui.menuFrame.hide()
        self._showMenuAction.setChecked(value)

    def isShowMenu(self):
        return self._showMenuAction.isChecked()

    def isShowPreview(self):
        return self._showPreviewAction.isChecked()

    def showDebug(self, value):
        mutils.setDebug(value)

    def showLabels(self, value):
        if value:
            self.ui.recordsWidget.showLabels(value)
        else:
            self.ui.recordsWidget.showLabels(False)
        self._showLabelsAction.setChecked(value)

    def showCreateFolderDialog(self):
        self.ui.foldersWidget.createFolder()


class NewFolderDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        studiolibrary.loadUi(self)
        self.setWindowTitle('Create Folder')
        self._text = ''
        self.connect(self.ui.cancelButton, QtCore.SIGNAL('clicked()'), self.close)
        self.connect(self.ui.createButton, QtCore.SIGNAL('clicked()'), self.create)

    def text(self):
        return self._text

    def create(self):
        text = str(self.ui.lineEdit.text()).strip()
        if text:
            self._text = text
            self.close()


class TopLevelItem(QtGui.QTreeWidgetItem):

    def __init__(self, parent):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(QtGui.QFont.DemiBold)
        self.setFont(0, font)
        self.setExpanded(True)


class FileSystemModel(QtGui.QFileSystemModel):

    def __init__(self, *args):
        QtGui.QFileSystemModel.__init__(self, *args)
        self._invalid = ['.studioLibrary']
        self.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)

    def columnCount(self, *args):
        return 1

    def hasChildren(self, index):
        for plugin in self._window.plugins().values():
            extension = plugin.extension()
            if extension and extension not in self._invalid:
                self._invalid.append(extension)

        path = str(self.filePath(index))
        folder = studiolibrary.Folder(path)
        dirname = folder.dirname()
        if os.path.exists(dirname):
            for name in os.listdir(dirname):
                if os.path.isdir(dirname + '/' + name):
                    valid = [ item for item in self._invalid if item in name ]
                    if not valid:
                        return True

        return False

    def data(self, index, role):
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                dirname = str(self.filePath(index))
                folder = studiolibrary.Folder(dirname)
                pixmap = QtGui.QIcon(folder.pixmap())
                if pixmap:
                    return QtGui.QIcon(folder.pixmap())
        if role == QtCore.Qt.FontRole:
            if index.column() == 0:
                dirname = str(self.filePath(index))
                folder = studiolibrary.Folder(dirname)
                if folder.exists():
                    if folder.bold():
                        font = QtGui.QFont()
                        font.setBold(True)
                        return font
        if role == QtCore.Qt.DisplayRole:
            text = QtGui.QFileSystemModel.data(self, index, role)
            return text


class SortFilterProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self, parent):
        self._parent = parent
        QtGui.QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        path = str(self.sourceModel().filePath(index))
        if '.studioLibrary' in path:
            return False
        for plugin in self._parent.window().plugins().values():
            if plugin.match(path):
                return False

        return True


class FoldersWidget(QtGui.QTreeView):

    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self._window = parent
        self._sourceModel = FileSystemModel(self)
        self._sourceModel._window = parent
        proxyModel = SortFilterProxyModel(self)
        proxyModel.setSourceModel(self._sourceModel)
        self.setModel(proxyModel)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHeaderHidden(True)
        self.setAcceptDrops(True)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setIndentation(7)
        self.setMinimumWidth(35)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QtGui.QTreeWidget.ExtendedSelection)
        self._items = []
        self.connect(self.selectionModel(), QtCore.SIGNAL('selectionChanged (const QItemSelection&,const QItemSelection&)'), self.selectionChangedX)

    def window(self):
        return self._window

    def selectionChangedX(self, folder1, folder2):
        for plugin in self.window().plugins().values():
            plugin.folderSelectionChanged(folder1, folder2)

        self.emit(QtCore.SIGNAL('selectionChanged()'))

    def currentState(self):
        sourceModel = self.model().sourceModel()
        state = {}
        index1 = self.selectionModel().selectedIndexes() or []
        index2 = self.model().persistentIndexList() or []
        index1.extend(index2)
        for i in index1:
            index = self.model().mapToSource(i)
            key = str(sourceModel.filePath(index))
            state.setdefault(key, {})
            state[key]['isSelected'] = self.selectionModel().isSelected(i)
            state[key]['isExpanded'] = self.isExpanded(i)

        return state

    def restoreState(self, state):
        self.selectionModel().clear()
        self.collapseAll()
        root = self.window().root()
        sourceModel = self.model().sourceModel()
        for path in state or []:
            if root in path:
                i = sourceModel.index(path)
                index = self.model().mapFromSource(i)
                if index:
                    isExpanded = state[path].get('isExpanded', False)
                    self.setExpanded(index, isExpanded)
                    if state[path].get('isSelected', False):
                        self.selectionModel().select(index, QtGui.QItemSelectionModel.Select)
                        self.emit(QtCore.SIGNAL('clicked (const QModelIndex&)'), index)

    def items(self):
        return []

    def setRoot(self, path):
        self.model().sourceModel().setRootPath(path)
        i = self.model().sourceModel().index(path)
        index = self.model().mapFromSource(i)
        self.setRootIndex(index)

    def selectFolders(self, folders):
        for name in folders:
            self.selectFolder(name)

    def selectFolder(self, path):
        dirname = os.path.dirname(path)
        index = self.model().sourceModel().index(dirname)
        index = self.model().mapFromSource(index)
        self.setExpanded(index, True)
        index = self.model().sourceModel().index(path)
        index = self.model().mapFromSource(index)
        self.selectionModel().clear()
        self.selectionModel().select(index, QtGui.QItemSelectionModel.Select)

    def renameSelected(self):
        folders = self.selectedFolders()
        if folders:
            folder, = folders
            name, accept = QtGui.QInputDialog.getText(self.window(), 'Rename Folder', 'New Name', QtGui.QLineEdit.Normal, folder.name())
            if accept:
                folder.rename(str(name))
                self.reload()
                self.selectFolder(folder.path())

    def deleteSelected(self):
        folders = self.selectedFolders()
        result = self.window().questionDialog("Are you sure you want to delete the selected folders '%s'" % [ f.name() for f in folders ])
        if result == QtGui.QMessageBox.Yes:
            for folder in folders:
                folder.delete()

            self.reload()

    def selectedFolder(self):
        folders = self.selectedFolders()
        if folders:
            return folders[-1]

    def selectedFolders(self):
        folders = []
        for index in self.selectedIndexes():
            index = self.model().mapToSource(index)
            path = self.model().sourceModel().filePath(index)
            folder = studiolibrary.Folder(str(path), parent=self)
            folders.append(folder)

        return folders

    def dragEnterEvent(self, event):
        event.accept()

    def clearSelection(self):
        self.selectionModel().clearSelection()

    def dragMoveEvent(self, event):
        index = self.indexAt(event.pos())
        if index:
            self.selectionModel().select(index, QtGui.QItemSelectionModel.ClearAndSelect)
            self.emit(QtCore.SIGNAL('clicked (const QModelIndex&)'), index)

    def dropEvent(self, event):
        if self.window().isLocked():
            return
        mimeData = event.mimeData()
        if hasattr(mimeData, 'records'):
            records = event.mimeData().records
            event.setDropAction(QtCore.Qt.IgnoreAction)
            folder = self.folderAt(event.pos())
            self.moveRecords(records, folder=folder)

    def moveRecords(self, records, folder = None, reload = True):
        if not folder:
            folder = self.selectedFolder()
        if folder:
            for record in records:
                try:
                    record.rename(folder.dirname() + '/' + record.name(), save=False)
                except:
                    import traceback
                    traceback.print_exc()

        if reload:
            self.window().reloadRecords()
            self.window().selectRecords(records)

    def showMenu(self):
        menu = self.window().contextMenu(self)
        folders = self.selectedFolders()
        for folder in folders:
            folder.contextMenu(menu, folders)

        if not folders:
            if not self.window().isLocked():
                menu.addMenu(self.window().ui.newMenu)
            menu.addSeparator()
            menu.addMenu(self.window().ui.settingsMenu)
        action = menu.exec_(QtGui.QCursor.pos())
        menu.close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            QtGui.QTreeView.mousePressEvent(self, event)
            self.showMenu()
        else:
            QtGui.QTreeView.mousePressEvent(self, event)

    def reload(self):
        pass

    def createFolder(self):
        dialog = NewFolderDialog(self.window())
        dialog.exec_()
        if dialog.text():
            folders = self.selectedFolders()
            if len(folders) == 1:
                folder = folders[-1]
                path = folder.dirname() + '/' + dialog.text()
            else:
                path = self.window().root() + '/' + dialog.text()
            if not os.path.exists(path):
                os.makedirs(path)
            folder = studiolibrary.Folder(path, parent=self)
            folder.save()
            self.selectFolder(folder.dirname())

    def folderAt(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        index = self.model().mapToSource(index)
        return studiolibrary.Folder(self.model().sourceModel().filePath(index), parent=self)


class RecordsWidget(QtGui.QListView):

    def __init__(self, parent):
        QtGui.QListView.__init__(self, parent)
        self.setStyleSheet('\nQListView::item:selected {\nbackground-color: rgb(255, 15, 255);\n}\n')
        self.setSelectionRectVisible(True)
        self.setDragEnabled(True)
        self._dropEnabled = False
        policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.setSizePolicy(policy)
        self.setIconSize(QtCore.QSize(90, 110))
        self.setGridSize(QtCore.QSize(90, 110))
        self.setLayoutMode(QtGui.QListView.Batched)
        self.setBatchSize(300)
        self.setResizeMode(QtGui.QListView.Adjust)
        self.setViewMode(QtGui.QListView.IconMode)
        self.setMinimumWidth(5)
        self.setMouseTracking(True)
        delegate = Delegate(self)
        self.setItemDelegate(delegate)
        self.setSelectionMode(QtGui.QListView.ExtendedSelection)
        model = Model([])
        self.setModel(model)
        self.connect(self, QtCore.SIGNAL('doubleClicked (const QModelIndex&)'), self.recordDoubleClicked)
        self._window = parent
        self._previousSelection = []
        self._dragAccepted = False
        self._dragStartIndex = False
        self._isMouseOver = False
        self._previousRecord = None
        self._recordMousePress = None
        self._drag = None
        self._viewSize = 90
        self._opacity = 255
        self._message = ''
        self._buttonDown = None
        self._zoomIndex = None
        self._zoomAmount = None
        self._isShowLabels = False
        self._fadeOutTimer = QtCore.QTimer(self)
        self.connect(self._fadeOutTimer, QtCore.SIGNAL('timeout()'), self.fadeOut)
        self._waitTimer = QtCore.QTimer(self)
        self.connect(self._waitTimer, QtCore.SIGNAL('timeout()'), self.wait)

    def window(self):
        return self._window

    def isShowLabels(self):
        return self._isShowLabels

    def showLabels(self, value):
        self._isShowLabels = value
        self.setViewSize(self.viewSize())
        self.repaint()

    def showMessage(self, text, repaint = True):
        self._message = text
        self._opacity = 255
        self._waitTimer.stop()
        self._waitTimer.start(500)
        if repaint:
            self.repaintMessage()

    def wait(self):
        self._fadeOutTimer.start(1)

    def repaintMessage(self):
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(18)
        m = QtGui.QFontMetrics(font)
        size = self.size()
        w = size.width()
        h = size.height()
        x = w / 2 - m.width(self._message) / 2 - 50
        y = h / 2
        w = m.width(self._message) + 100
        h = 120
        self.repaint(x, y, w, h)

    def fadeOut(self):
        if self._opacity > 0:
            self._opacity -= 2
            self.repaintMessage()
        else:
            self._fadeOutTimer.stop()
            self._waitTimer.stop()

    def records(self):
        return self.model().records()

    def paintEvent(self, e):
        QtGui.QListView.paintEvent(self, e)
        if self._message and self._opacity > 0:
            qp = QtGui.QPainter(self.viewport())
            size = self.size()
            w = size.width()
            h = size.height()
            qp.setPen(QtCore.Qt.NoPen)
            qp.setBrush(QtGui.QColor(0, 0, 0, self._opacity / 2))
            qp.setRenderHints(QtGui.QPainter.Antialiasing)
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(18)
            m = QtGui.QFontMetrics(font)
            x = w / 2 - m.width(self._message) / 2 - 25
            y = h / 2
            qp.drawRoundRect(x, y, m.width(self._message) + 50, 120, 15, 25)
            qp.setFont(font)
            qp.setPen(QtGui.QColor(255, 255, 255, self._opacity))
            qp.drawText(w / 2 - m.width(self._message) / 2 + 7, h / 2 + 67, self._message)

    def renameSelected(self):
        records = self.selectedRecords()
        if records:
            record = records[-1]
            name, accept = QtGui.QInputDialog.getText(self.window(), 'Rename Record', 'New Name', QtGui.QLineEdit.Normal, record.name())
            if accept:
                record.rename(str(name), save=False)

    def setDropEnabled(self, value):
        self._dropEnabled = value

    def selectRecord(self, record):
        self.selectRecords([record])

    def clearSelection(self):
        self.selectionModel().clearSelection()

    def selectRecords(self, records):
        if not records:
            return
        indexes = []
        record = None
        self.selectionModel().clearSelection()
        for record in records:
            if isinstance(record, basestring):
                if '/' in record:
                    indexes.extend([ self.model().index(i, 0) for i, r in enumerate(self.model().records()) if r.dirname() == record ])
                else:
                    indexes.extend([ self.model().index(i, 0) for i, r in enumerate(self.model().records()) if r.name() == record ])
            else:
                indexes.extend([ self.model().index(i, 0) for i, r in enumerate(self.model().records()) if r.dirname() == record.dirname() ])

        self.selectIndexes(indexes)
        records = self.selectedRecords()
        if records:
            records[-1].clicked()

    def selectIndexes(self, indexes):
        for index in indexes:
            self.selectionModel().setCurrentIndex(index, QtGui.QItemSelectionModel.Select)

    def recordDoubleClicked(self, event):
        records = self.selectedRecords()
        if records:
            try:
                records[-1].doubleClicked()
            except:
                import traceback
                print traceback.format_exc()

    def setViewSize(self, value):
        if self.isShowLabels():
            margin = 13
        else:
            margin = 0
        if value < 20:
            value = 20
        self._viewSize = value
        if value > 30:
            self.setViewMode(QtGui.QListView.IconMode)
        else:
            value = 20
            margin = 0
            self.setViewMode(QtGui.QListView.ListMode)
        self.setIconSize(QtCore.QSize(value, value))
        self.setGridSize(QtCore.QSize(value, value + margin))
        if value > 30 and self.window()._padding == '0':
            self.window()._padding = '7'
            self.setStyleSheet('QListView:item{padding:  -%spx 0px 7px 0px;}' % self.window().spacing())
        elif value < 30:
            self.window()._padding = '0'
            self.setStyleSheet('QListView:item{padding:  -%spx 0px 0px 0px;}' % self.window().spacing())

    def viewSize(self):
        return self._viewSize

    def selectedRecords(self):
        records = []
        for index in self.selectedIndexes():
            record = self.model().records()[index.row()]
            records.append(record)

        return records

    def recordHover(self, record, event):
        if record:
            record.mouseMoveEvent(event)

    def recordEnter(self, record, event):
        self._dragStartIndex = None
        if record:
            record.mouseEnterEvent(event)

    def recordLeave(self, record, event):
        if record:
            record.mouseLeaveEvent(event)

    def selectionChanged(self, item1, item2):
        records = self.selectedRecords()
        for plugin in self.window().plugins().values():
            plugin.recordSelectionChanged(item1, item2)

        self.emit(QtCore.SIGNAL('itemSelectionChanged()'))
        for record in records:
            record.selectionChanged(item1, item2)

    def clear(self):
        if self.model():
            self.model().setRecords([])

    def setRecords(self, records):
        if self.model():
            self.model().setRecords(records)

    def dragEnterEvent(self, event):
        if self._dropEnabled:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self._dropEnabled:
            event.accept()
            if self._buttonDown != QtCore.Qt.MidButton:
                self.window().mouseMoveEvent(event)
        else:
            event.ignore()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if hasattr(mimeData, 'records'):
            records = mimeData.records
            record = self.recordAt(event.pos())
            move = False
            folder = self.window().ui.foldersWidget.selectedFolder()
            for r in records:
                if folder != r.folder():
                    move = True

            if move and record:
                self.window().ui.foldersWidget.moveRecords(records, reload=False)
            elif move:
                self.window().ui.foldersWidget.moveRecords(records, reload=True)
            if record:
                for r in records:
                    self.model().removeRecord(r)
                    self.model().insertRecord(record._index.row(), r)

                self.selectRecords(records)
                self.emit(QtCore.SIGNAL('orderChanged()'))

    def leaveEvent(self, event):
        self.recordLeave(self._previousRecord, event)
        self._previousRecord = None
        self._isMouseOver = False
        QtGui.QListView.leaveEvent(self, event)

    def enterEvent(self, event):
        self._isMouseOver = True

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self._zoomIndex = None
            self._zoomAmount = None
        for record in self.selectedRecords():
            record.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        return QtGui.QListView.keyReleaseEvent(self, event)

    def mousePressEvent(self, event):
        self._buttonDown = event.button()
        record = self.recordAt(event.pos())
        if not record:
            if event.button() == QtCore.Qt.LeftButton:
                QtGui.QListView.mousePressEvent(self, event)
                self.clearSelection()
            if event.button() == QtCore.Qt.RightButton:
                self.showMenu()
            self._recordMousePress = None
        else:
            event._parent = self
            self._recordMousePress = record
            if event.button() == QtCore.Qt.LeftButton:
                self.endDrag()
                self._dragStartPos = event.pos()
                self._dragStartIndex = self.indexAt(event.pos())
                self._previousSelection = self.selectedRecords()
            elif event.button() == QtCore.Qt.RightButton:
                self.endDrag()
                if record is not None:
                    record.mousePressEvent(event)
                self._recordMousePress = None
                self.showMenu()
            record.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        record = self.recordAt(event.pos())
        event._record = record
        self._buttonDown = None
        if self._recordMousePress:
            event._parent = self
            self._recordMousePress.mouseReleaseEvent(event)
            self._recordMousePress = None
        else:
            QtGui.QListView.mouseReleaseEvent(self, event)
        self.endDrag()
        self.repaint()

    def mouseMoveEvent(self, event):
        event._parent = self
        record = self.recordAt(event.pos())
        if self._recordMousePress:
            self._recordMousePress.mouseMoveEvent(event)
        else:
            self.updateRecordEvent(event)
        if record and not self._drag and self._dragStartIndex and self._dragStartIndex.isValid():
            event._record = self._recordMousePress
            self.startDrag(event)
        else:
            if self._buttonDown != QtCore.Qt.MidButton:
                self.window().mouseMoveEvent(event)
            QtGui.QListView.mouseMoveEvent(self, event)
        if self._buttonDown:
            self.repaint()

    def updateRecordEvent(self, event):
        record = self.recordAt(event.pos())
        if record:
            if id(self._previousRecord) != id(record):
                self.recordLeave(self._previousRecord, event)
                self.recordEnter(record, event)
            self.recordHover(record, event)
        elif self._previousRecord:
            self.recordLeave(self._previousRecord, event)
        self._previousRecord = record

    def wheelEvent(self, event):
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier or modifiers == QtCore.Qt.AltModifier:
            selectedIndexes = self.selectedIndexes()
            if selectedIndexes:
                self._zoomIndex = selectedIndexes[0]
            elif self._zoomAmount is None:
                self._zoomIndex = self.indexAt(QtCore.QPoint(event.pos()))
            self._zoomAmount = numSteps * 5
            value = self.viewSize() + self._zoomAmount
            self.setViewSize(value)
            self.window().showMessage('Zoom: %s%%' % str(value), repaint=False)
            if self._zoomIndex:
                self.scrollTo(self._zoomIndex, QtGui.QAbstractItemView.PositionAtCenter)
            event.accept()
        else:
            QtGui.QListView.wheelEvent(self, event)
        self.updateRecordEvent(event)

    def selectedPlugins(self):
        plugins = []
        for record in self.selectedRecords():
            if record.plugin() not in plugins:
                plugins.append(record.plugin())

        return plugins

    def showMenu(self):
        menu = self.window().contextMenu(self)
        records = self.selectedRecords()
        for plugin in self.window().plugins().values():
            plugin.recordContextMenu(menu, records)

        if not records:
            if not self.window().isLocked():
                menu.addMenu(self.window().ui.newMenu)
            menu.addSeparator()
            menu.addMenu(self.window().ui.sortMenu)
            menu.addMenu(self.window().ui.settingsMenu)
        point = QtGui.QCursor.pos()
        point.setX(point.x() + 3)
        point.setY(point.y() + 3)
        menu.exec_(point)
        menu.close()

    def startDrag(self, event):
        if self.window().isLocked():
            return
        point = self._dragStartPos - event.pos()
        if point.x() > 10 or point.y() > 10 or point.x() < -10 or point.y() < -10:
            index = event._record._index
            selected = self.model().data(index, QtCore.Qt.UserRole)
            mimeData = QtCore.QMimeData()
            mimeData.records = self.selectedRecords()
            self._drag = QtGui.QDrag(self)
            self._drag.setMimeData(mimeData)
            pixmap = QtGui.QPixmap()
            rect = self.visualRect(index)
            pixmap = pixmap.grabWidget(self, rect)
            self._drag.setPixmap(pixmap)
            self._drag.setHotSpot(QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2))
            self._drag.setPixmap(pixmap)
            result = self._drag.start(QtCore.Qt.MoveAction)

    def endDrag(self):
        self._buttonDown = None
        self._dragStartIndex = None
        if self._drag:
            del self._drag
            self._drag = None

    def recordAt(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        record = self.model().records()[index.row()]
        if record.visualRect() and record.visualRect().contains(pos):
            record._index = index
            return record


class Delegate(QtGui.QStyledItemDelegate):

    def __init__(self, *args):
        QtGui.QStyledItemDelegate.__init__(self, *args)

    def paint(self, painter, option, index):
        return QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        result = QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        if index.column() == 0:
            record = index.model().records()[index.row()]
            if record:
                record.setRect(QtCore.QRect(option.rect))
                record.paint(painter, option)
        return result

    def paint(self, painter, option, index):
        if index.column() == 0:
            record = index.model().records()[index.row()]
            if record:
                record.setRect(QtCore.QRect(option.rect))
                record.paint(painter, option)


class Model(QtCore.QAbstractTableModel):

    def __init__(self, records, *args, **kwargs):
        QtCore.QAbstractTableModel.__init__(self, *args)
        self._iconSize = QtCore.QSize(90, 90)
        self.setRecords(records)
        self._filters = [re.compile('.*')]
        self._filteredRecords = []

    def recordsCount(self):
        return len(self._allRecords)

    def hiddenRecordsCount(self):
        return len(self._allRecords) - len(self._filteredRecords)

    def records(self):
        return self._filteredRecords

    def setRecords(self, records):
        self._allRecords = records or []
        self.update()

    def setFilter(self, filter):
        self._filters = []
        try:
            filter = filter.replace('.', '[.]')
            filter = filter.replace(' or ', '|')
            filter = filter.lower()
            for filter in filter.split(' and '):
                self._filters.append(re.compile(filter))

        except:
            pass

        self.update()

    def filters(self):
        return self._filters

    def update(self):
        self._filteredRecords = []
        for record in self._allRecords:
            valid = True
            for filter in self.filters():
                if filter and not filter.search(str(record).lower()):
                    valid = False

            if valid:
                self._filteredRecords.append(record)

        self.reset()

    def insertRecord(self, i, record):
        self.records().insert(i, record)

    def removeRecord(self, record):
        for i, r in enumerate(self.records()):
            if id(r) == id(record) or r.path() == record.path():
                self.records().pop(i)

        self.reset()

    def addRecord(self, record):
        self.records().append(record)

    def columnCount(self, index):
        return 1

    def rowCount(self, index):
        return len(self._filteredRecords)

    def setIconSize(self, size):
        size.setHeight(size.height())
        self._iconSize = size

    def iconSize(self):
        return self._iconSize

    def data(self, index, role):
        if index.column() == 0:
            return self.indexData(index, role)
        return QtCore.QVariant()

    def indexData(self, index, role):
        record = self._filteredRecords[index.row()]
        return record.indexData(self, index, role)

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def removeRow(self, row, index):
        self._filteredRecords.pop(row)
        self.reset()
        return True


_data = 'ClFXaWRnZXQgewoJY29sb3I6IENPTE9SOwp9CgpRV2lkZ2V0I01haW5Gb3JtIHsKICAgIGJhY2tn\ncm91bmQtY29sb3I6IEJBQ0tHUk9VTkRDT0xPUjsKfQoKUVB1c2hCdXR0b24jY3JlYXRlQnV0dG9u\nLCBRUHVzaEJ1dHRvbiNzZXR0aW5nc0J1dHRvbiwgU2VhcmNoV2lkZ2V0IHsKCWJhY2tncm91bmQt\nY29sb3I6IEZPQ1VTQkFDS0dST1VORENPTE9SOwp9CgpRUHVzaEJ1dHRvbiNwaW5CdXR0b24sIFFQ\ndXNoQnV0dG9uI3NlbGVjdENvbnRyb2xzQnV0dG9uIHsKCWJvcmRlci10b3AtbGVmdC1yYWRpdXM6\nIDBweDsKICAgIGJvcmRlci1ib3R0b20tbGVmdC1yYWRpdXM6IDBweDsKfQoKU2VxdWVuY2VXaWRn\nZXQgewogICAgYm9yZGVyOiAwcHggc29saWQgcmdiKDAsIDAsIDAsIDIwKTsKfQoKUUxpbmVFZGl0\nI25hbWVzcGFjZXMsIFFDb21ib0JveCNjb250cm9scyB7Cglib3JkZXItdG9wLXJpZ2h0LXJhZGl1\nczogMHB4OwogICAgYm9yZGVyLWJvdHRvbS1yaWdodC1yYWRpdXM6IDBweDsKfQoKUVdpZGdldDpk\naXNhYmxlZCB7Cgljb2xvcjogcmdiKDE1MCwgMTUwLCAxNTAsIDIzNSk7Cn0KClFXaWRnZXQjU3R1\nZGlvTGlicmFyeVdpbmRvdyAsIFFEaWFsb2csIFFNYWluV2luZG93LCBRQ29tYm9Cb3ggUUFic3Ry\nYWN0SXRlbVZpZXcgewoJYmFja2dyb3VuZC1jb2xvcjogQkFDS0dST1VORENPTE9SOwp9CgpRTWVu\ndSwgUUNvbWJvQm94IFFBYnN0cmFjdEl0ZW1WaWV3ICAgewoJYm9yZGVyOiAxcHggc29saWQgQkFD\nS0dST1VORENPTE9SOwoJYmFja2dyb3VuZC1jb2xvcjogQkFDS0dST1VORENPTE9SOwp9CgpRV2lk\nZ2V0ewoJYm9yZGVyOiAwcHggc29saWQgcmdiYSg0MCwxNTUsNDApOwp9CgpTZXF1ZW5jZVdpZGdl\ndCB7CiAgICBjb2xvcjogcmdiKDQwLCA0MCwgNDApOwogICAgYm9yZGVyOiAxcHggc29saWQgcmdi\nYSgwLCAwLCAwLCAxNTApOwogICAgYmFja2dyb3VuZC1jb2xvcjogcmdiKDI1NCwgMjU1LCAyMzAs\nIDIwMCk7Cn0KClFEaWFsb2cjRGlhbG9newoJYm9yZGVyOiAxcHggc29saWQgcmdiYSgwLDAsMCw1\nMCk7CgliYWNrZ3JvdW5kLWNvbG9yOiByZ2IoNjAsIDYwLCA2MCwgMjU1KTsKfQoKUVB1c2hCdXR0\nb24gewogICAgYm9yZGVyLXJhZGl1czogMHB4OwogICAgYm9yZGVyOiAwcHggc29saWQgcmdiYSgw\nLDAsMCw1MCk7CiAgICBjb2xvcjogcmdiKDIzMCwgMjMwLCAyMzApOwogICAgaGVpZ2h0OiAyN3B4\nOwogICAgcGFkZGluZzogMCA4cHg7Cn0KClFQdXNoQnV0dG9uI3NhdmVCdXR0b24sIFFQdXNoQnV0\ndG9uI2FwcGx5QnV0dG9uLCBRUHVzaEJ1dHRvbiNhY2NlcHRCdXR0b24sClFQdXNoQnV0dG9uI2Ny\nZWF0ZUJ1dHRvbjEsClFQdXNoQnV0dG9uI2Jyb3dzZUJ1dHRvbnsKCWNvbG9yOiBGT0NVU0NPTE9S\nOwogICAgYmFja2dyb3VuZC1jb2xvcjogRk9DVVNCQUNLR1JPVU5EQ09MT1I7Cn0KClFTcGxpdHRl\ncjo6aGFuZGxlOmhvcml6b250YWwgewoJYmFja2dyb3VuZC1jb2xvcjogcmdiKDI1NSwgMjU1LCAy\nNTUsIDIwKTsKfQoKUVNwbGl0dGVyOjpoYW5kbGU6aG9yaXpvbnRhbDpob3ZlciB7CiAgICBiYWNr\nZ3JvdW5kLWNvbG9yOiBGT0NVU0JBQ0tHUk9VTkRDT0xPUjsKfQoKUUxpc3RWaWV3OjppdGVtIHsK\nCWJvcmRlci1zdHlsZTogc29saWQ7CglvdXRsaW5lOiBub25lOwoJYmFja2dyb3VuZC1jb2xvcjog\ncmdiKDI1NSwgMjU1LCAyNTUsIDI1KTsKCW1hcmdpbjogU1BBQ0lOR3B4IDBweCAwcHggU1BBQ0lO\nR3B4OwoJcGFkZGluZzogIC1TUEFDSU5HcHggMHB4IFBBRERJTkdweCAwcHg7Cglib3JkZXI6IEJP\nUkRFUnB4IHNvbGlkIHJnYigyNTUsIDI1NSwgMjU1LCAyNSk7Cn0KClFMaXN0Vmlldzo6aXRlbTpo\nb3ZlciB7CglvdXRsaW5lOiBub25lOwoJYmFja2dyb3VuZC1jb2xvcjogcmdiKDI1NSwgMjU1LCAy\nNTUsIDQ1KTsKfQoKUUxpc3RWaWV3OjppdGVtOnNlbGVjdGVkLCBRTGlzdFZpZXc6Oml0ZW06c2Vs\nZWN0ZWQ6YWN0aXZlIHsKCWJvcmRlcjogMXB4IHNvbGlkIEZPQ1VTQkFDS0dST1VORENPTE9SOwoJ\nc2hvdy1kZWNvcmF0aW9uLXNlbGVjdGVkOiAxOwp9CgpRTGlzdFZpZXcgewoJb3V0bGluZTogbm9u\nZTsKCWJhY2tncm91bmQtY29sb3I6IHJnYigwLCAwLCAwLCAwKTsKCWJvcmRlcjogMHB4IHNvbGlk\nIHJnYigxODAsIDE4MCwgMTgwLCAxNTApOwoJc2hvdy1kZWNvcmF0aW9uLXNlbGVjdGVkOiAxOyAv\nKiBtYWtlIHRoZSBzZWxlY3Rpb24gc3BhbiB0aGUgZW50aXJlIHdpZHRoIG9mIHRoZSB2aWV3ICov\nCn0KClFUcmVlVmlldyB7CiAgICBvdXRsaW5lOiBub25lOwogICAgYm9yZGVyOiAwcHg7CiAgICBi\nYWNrZ3JvdW5kLWNvbG9yOnJnYigwLCAwLCAwLCAwKTsKfQoKUVRyZWVWaWV3OjppdGVtIHsKCWhl\naWdodDogIDIycHg7Cn0KClFUcmVlVmlldzo6aXRlbTpmb2N1c3sKCWJvcmRlcjogMHB4IHNvbGlk\nIHJnYigyMjAsIDIyMCwgMjIwLCAxODApOwoJb3V0bGluZTogbm9uZTsKfQoKUVRyZWVWaWV3Ojpp\ndGVtOmhvdmVyLApRVHJlZVZpZXc6OmJyYW5jaDpob3ZlciB7Cglib3JkZXI6IDBweCBzb2xpZCBy\nZ2IoMjIwLCAyMjAsIDIyMCwgMTgwKTsKCW91dGxpbmU6IG5vbmU7CgliYWNrZ3JvdW5kLWNvbG9y\nOiBxbGluZWFyZ3JhZGllbnQoeDE6IDAsIHkxOiAwLCB4MjogMCwgeTI6IDEsIHN0b3A6IDAgcmdi\nKDAsMTgwLDI0NSwgMCksIHN0b3A6IDEgcmdiKDAsMTQwLDIzMCwgMCkpOwp9CgpRVHJlZVZpZXc6\nOml0ZW06c2VsZWN0ZWQsIFFUcmVlVmlldzo6aXRlbTpzZWxlY3RlZDphY3RpdmUsClFMaXN0Vmll\ndzo6aXRlbTpzZWxlY3RlZCwgUUxpc3RWaWV3OjppdGVtOnNlbGVjdGVkOmFjdGl2ZSwgUVRyZWVW\naWV3OjpicmFuY2g6c2VsZWN0ZWQgewogICAgYm9yZGVyLXN0eWxlOiBzb2xpZDsKICAgIG91dGxp\nbmU6IG5vbmU7CiAgICBjb2xvcjogRk9SRUdST1VORENPTE9SOwogICAgYmFja2dyb3VuZC1jb2xv\ncjogRk9DVVNCQUNLR1JPVU5EQ09MT1I7Cn0KClFUcmVlVmlldzo6aXRlbTpzZWxlY3RlZCB7CiAg\nICBib3JkZXItbGVmdDogMHB4ICBGT0NVU0JBQ0tHUk9VTkRDT0xPUjsKfQoKUVNsaWRlcjo6Z3Jv\nb3ZlOmhvcml6b250YWwgewogICAgaGVpZ2h0OiAzcHg7IC8qIHRoZSBncm9vdmUgZXhwYW5kcyB0\nbyB0aGUgc2l6ZSBvZiB0aGUgc2xpZGVyIGJ5IGRlZmF1bHQuIGJ5IGdpdmluZyBpdCBhIGhlaWdo\ndCwgaXQgaGFzIGEgZml4ZWQgc2l6ZSAqLwogICAgYmFja2dyb3VuZDogIHJnYigwLDAsMCwwKTsK\nfQoKUVNsaWRlcjo6aGFuZGxlOmhvcml6b250YWwgewoJYmFja2dyb3VuZDogIEZPQ1VTQkFDS0dS\nT1VORENPTE9SOwogICAgd2lkdGg6IDEwcHg7CiAgICBoZWlnaHQ6IDJweDsKICAgIG1hcmdpbjog\nLTRweCAwOyAvKiBoYW5kbGUgaXMgcGxhY2VkIGJ5IGRlZmF1bHQgb24gdGhlIGNvbnRlbnRzIHJl\nY3Qgb2YgdGhlIGdyb292ZS4gRXhwYW5kIG91dHNpZGUgdGhlIGdyb292ZSAqLwogICAgYm9yZGVy\nLXJhZGl1czogNXB4OwogfQoKUVNsaWRlcjo6YWRkLXBhZ2U6aG9yaXpvbnRhbCB7CiAgICBib3Jk\nZXI6IDBweCBzb2xpZCAjOTk5OTk5OwogICAgYmFja2dyb3VuZC1jb2xvcjogcmdiKDAsIDAsIDAs\nIDgwKTsKfQoKUVNsaWRlcjo6c3ViLXBhZ2U6aG9yaXpvbnRhbCB7CiAgICBib3JkZXItdG9wOiAx\ncHggc29saWQgRk9DVVNCQUNLR1JPVU5EQ09MT1I7CiAgICBib3JkZXItYm90dG9tOiAxcHggc29s\naWQgRk9DVVNCQUNLR1JPVU5EQ09MT1I7CiAgICBiYWNrZ3JvdW5kLWNvbG9yOiBGT0NVU0JBQ0tH\nUk9VTkRDT0xPUjsKfQoKUVNjcm9sbEJhcjp2ZXJ0aWNhbCB7Cgl3aWR0aDogU0NST0xMX0JBUl9X\nSURUSHB4Owp9CgpRU2Nyb2xsQmFyOmhvcml6b250YWwgewoJaGVpZ2h0OiBTQ1JPTExfQkFSX1dJ\nRFRIcHg7Cn0KClFTY3JvbGxCYXI6dmVydGljYWwsClFTY3JvbGxCYXI6aG9yaXpvbnRhbHsKCWJv\ncmRlcjogMHB4IHNvbGlkIGdyZXk7CgliYWNrZ3JvdW5kOiAgcmdiKDI1NSwyNTUsIDI1NSwgMCk7\nCgltYXJnaW46IDBweDsKfQoKUVNjcm9sbEJhcjo6aGFuZGxlOnZlcnRpY2FsLApRU2Nyb2xsQmFy\nOjpoYW5kbGU6aG9yaXpvbnRhbHsKCWJhY2tncm91bmQ6ICByZ2IoMjU1LDI1NSwyNTUsNTApOwoJ\nbWluLWhlaWdodDogMHB4Owp9CgpRU2Nyb2xsQmFyOjpoYW5kbGU6dmVydGljYWw6aG92ZXIsClFT\nY3JvbGxCYXI6OmhhbmRsZTpob3Jpem9udGFsOmhvdmVyIHsKCWJhY2tncm91bmQ6ICByZ2IoMjU1\nLDI1NSwyNTUsMTUwKTsKfQoKUVNjcm9sbEJhcjo6YWRkLWxpbmU6dmVydGljYWwsClFTY3JvbGxC\nYXI6OmFkZC1saW5lOmhvcml6b250YWwgewoJYm9yZGVyOiAwcHggc29saWQgZ3JleTsKCWJhY2tn\ncm91bmQ6ICByZ2IoODAsIDgwLCA4MCk7CgloZWlnaHQ6IDBweDsKCXN1YmNvbnRyb2wtcG9zaXRp\nb246IGJvdHRvbTsKCXN1YmNvbnRyb2wtb3JpZ2luOiBtYXJnaW47Cn0KClFTY3JvbGxCYXI6OnN1\nYi1saW5lOnZlcnRpY2FsLApRU2Nyb2xsQmFyOjpzdWItbGluZTpob3Jpem9udGFsIHsKCWJvcmRl\ncjogMHB4IHNvbGlkIGdyZXk7CgliYWNrZ3JvdW5kOiAgcmdiKDgwLCA4MCwgODApOwoJaGVpZ2h0\nOiAwcHg7CglzdWJjb250cm9sLXBvc2l0aW9uOiB0b3A7CglzdWJjb250cm9sLW9yaWdpbjogbWFy\nZ2luOwp9CgpRU2Nyb2xsQmFyOjp1cC1hcnJvdzp2ZXJ0aWNhbCwgUVNjcm9sbEJhcjo6ZG93bi1h\ncnJvdzp2ZXJ0aWNhbCB7Cglib3JkZXI6IDBweCBzb2xpZCBncmV5OwoJd2lkdGg6IDBweDsKCWhl\naWdodDogMHB4OwoJYmFja2dyb3VuZDogd2hpdGU7Cn0KClFTY3JvbGxCYXI6OmFkZC1wYWdlOmhv\ncml6b250YWwsIFFTY3JvbGxCYXI6OmFkZC1wYWdlOnZlcnRpY2FsLCAgUVNjcm9sbEJhcjo6YWRk\nLXBhZ2U6aG9yaXpvbnRhbCwgUVNjcm9sbEJhcjo6c3ViLXBhZ2U6dmVydGljYWwgewoJYmFja2dy\nb3VuZDogbm9uZTsKfQoKU2VhcmNoV2lkZ2V0IHsKCWZvbnQtc2l6ZTogMTZweDsKICAgIGJvcmRl\nci1yYWRpdXM6IDJweDsKCWhlaWdodDogMjdweDsKCWNvbG9yOiByZ2IoMjU1LCAyNTUsIDI1NSwg\nMjEwKTsKICAgIGJvcmRlcjogMHB4IHNvbGlkIHJnYig2MCwgNjAsIDYwLCAyMDApOwogICAgYm9y\nZGVyLXJpZ2h0OiAwcHggc29saWQgcmdiKDE0MCwgMTQwLCAxNDAsIDEwMCk7Cgp9CgpRTGluZUVk\naXQgewoJZm9udC1zaXplOiAxNHB4OwogICAgYm9yZGVyLXJhZGl1czogMHB4OwoJY29sb3I6IHJn\nYigyNTUsIDI1NSwgMjU1LCAyMTApOwogICAgYm9yZGVyOiAwcHggc29saWQgcmdiKDYwLCA2MCwg\nNjAsIDIwMCk7CiAgICBib3JkZXItcmlnaHQ6IDBweCBzb2xpZCByZ2IoMTQwLCAxNDAsIDE0MCwg\nMTAwKTsKCn0KClFQdXNoQnV0dG9uI3NlYXJjaEJ1dHRvbiB7CgloZWlnaHQ6IDI3cHg7Cgl3aWR0\naDogMTBweDsKICAgIGJvcmRlcjogMHB4IHNvbGlkIHJnYig2MCwgNjAsIDYwLCAyMDApOwogICAg\nYm9yZGVyLXJpZ2h0OiAwcHggc29saWQgcmdiKDE0MCwgMTQwLCAxNDAsIDEwMCk7Cgp9CgpRQ29t\nYm9Cb3ggewoJd2lkdGg6IDEwcHg7Cglmb250LXNpemU6IDE0cHg7CiAgICBib3JkZXItcmFkaXVz\nOiAwcHg7CglwYWRkaW5nLWxlZnQ6IDJweDsKCWNvbG9yOiByZ2IoMjU1LCAyNTUsIDI1NSwgMjEw\nKTsKICAgIGJvcmRlcjogMHB4IHNvbGlkIHJnYig2MCwgNjAsIDYwLCAyMDApOwoKfQoKCi8qCkhP\nVkVSCiovClFQdXNoQnV0dG9uOmhvdmVyLCBTZWFyY2hXaWRnZXQ6aG92ZXJ7CiAgICBiYWNrZ3Jv\ndW5kLWNvbG9yOiByZ2JhKDAsIDAsIDAsIDE2MCk7Cn0KClFQdXNoQnV0dG9uOnByZXNzZWQsIFNl\nYXJjaFdpZGdldDpwcmVzc2VkewogICAgYmFja2dyb3VuZC1jb2xvcjogcmdiYSgwLCAwLCAwLCA4\nMCk7Cn0KCgpRTGluZUVkaXQ6Zm9jdXMsIFNlYXJjaFdpZGdldDpmb2N1cyB7CiAgICBib3JkZXI6\nIDJweCBzb2xpZCBGT0NVU0JBQ0tHUk9VTkRDT0xPUjsKfQoKCi8qCldJREdFVCBCQUNLR1JPVU5E\nIEZPQ1VTQkFDS0dST1VORENPTE9SCiovCgpRUHVzaEJ1dHRvbiwgUUxpbmVFZGl0LCBRQ29tYm9C\nb3ggewoJYmFja2dyb3VuZC1jb2xvcjogcmdiYSgwLCAwLCAwLCA4MCk7Cn0KClFQdXNoQnV0dG9u\nI3NlYXJjaEJ1dHRvbiB7CgliYWNrZ3JvdW5kLWNvbG9yOiByZ2JhKDAsIDAsIDAsIDApOwp9CgpJ\nbmZvRnJhbWUgewoJYmFja2dyb3VuZC1jb2xvcjogcmdiYSgwLCAwLCAwKTsKfQoKUUNvbWJvQm94\nOjpkcm9wLWRvd24gewogICAgd2lkdGg6IDFweDsKCWJhY2tncm91bmQtY29sb3I6IHJnYigyNTUs\nIDI1NSwgMjU1LCAwKTsKfQoKUUNvbWJvQm94Ojpkb3duLWFycm93IHsKICAgIHdpZHRoOiAxcHg7\nCglpbWFnZTogIHVybChESVJOQU1FL3VpL2ltYWdlcy9udWxsLnBuZyk7CiAgICBiYWNrZ3JvdW5k\nLWNvbG9yOiByZ2IoMjU1LCAyNTUsIDI1NSwgMCk7Cn0KCgpRTWVudTo6aXRlbSB7Cglib3JkZXI6\nIDFweCBzb2xpZCByZ2IoMCwwLDAsMCk7CglwYWRkaW5nOiAycHggMjVweCAycHggMjBweDsKfQoK\nUU1lbnU6Oml0ZW06c2VsZWN0ZWQgewoJY29sb3I6IEZPQ1VTQ09MT1I7CgliYWNrZ3JvdW5kLWNv\nbG9yOiBGT0NVU0JBQ0tHUk9VTkRDT0xPUjsKfQoKUUNvbWJvQm94IFFBYnN0cmFjdEl0ZW1WaWV3\nIHsKCXNlbGVjdGlvbi1iYWNrZ3JvdW5kLWNvbG9yOiBGT0NVU0JBQ0tHUk9VTkRDT0xPUjsKCXNl\nbGVjdGlvbi1jb2xvcjogcmdiKDI1NSwgMjU1LCAyNTUsIDIxMCk7Cn0KClFNZW51OjpzZXBhcmF0\nb3IsIFFDb21ib0JveCwgUUFic3RyYWN0SXRlbVZpZXc6OnNlcGFyYXRvcnsKCWhlaWdodDogMnB4\nOwoJcGFkZGluZzogMXB4IDFweCAxcHggMXB4Owp9CgpEaWFsb2dGcmFtZSA+IFFXaWRnZXQgewoJ\nYmFja2dyb3VuZC1jb2xvcjogcXJhZGlhbGdyYWRpZW50KHNwcmVhZDpwYWQsIGN4OjAuNSwgY3k6\nMC41LCByYWRpdXM6MC41LCBmeDowLjUsIGZ5OjAuNSwgc3RvcDowIHJnYmEoMCwgMCwgMCwgODEp\nLCBzdG9wOjEgcmdiYSgwLCAwLCAwLCAxNTApKTsKCWJhY2tncm91bmQtY29sb3I6IHFyYWRpYWxn\ncmFkaWVudChzcHJlYWQ6cGFkLCBjeDowLjUsIGN5OjAuNSwgcmFkaXVzOjAuNSwgZng6MC41LCBm\neTowLjUsIHN0b3A6MCByZ2JhKDAsIDAsIDAsIDEwMCksIHN0b3A6MSByZ2JhKDAsIDAsIDAsIDE5\nMCkpOwp9CgpRVHJlZVZpZXc6OmJyYW5jaDpoYXMtY2hpbGRyZW46IWhhcy1zaWJsaW5nczpjbG9z\nZWQsClFUcmVlVmlldzo6YnJhbmNoOmNsb3NlZDpoYXMtY2hpbGRyZW46aGFzLXNpYmxpbmdzIHsK\nICAgIGJvcmRlci1pbWFnZTogbm9uZTsKICAgIGltYWdlOiB1cmwoRElSTkFNRS91aS9pbWFnZXMv\nYnJhbmNoQ2xvc2VkLnBuZyk7Cn0KClFUcmVlVmlldzo6YnJhbmNoOm9wZW46aGFzLWNoaWxkcmVu\nOiFoYXMtc2libGluZ3MsClFUcmVlVmlldzo6YnJhbmNoOm9wZW46aGFzLWNoaWxkcmVuOmhhcy1z\naWJsaW5ncyAgewogICAgYm9yZGVyLWltYWdlOiBub25lOwogICAgaW1hZ2U6IHVybChESVJOQU1F\nL3VpL2ltYWdlcy9icmFuY2hPcGVuLnBuZyk7Cn0KClFMaW5lIHsKCWJhY2tncm91bmQtY29sb3I6\nIHJnYigyNTUsIDE3MCwgMCk7Cn0KClFQdXNoQnV0dG9uOmNoZWNrZWR7Cgljb2xvcjogcmdiKDMw\nLCAzMCwgMzApOwogICAgYmFja2dyb3VuZC1jb2xvcjogRk9DVVNCQUNLR1JPVU5EQ09MT1I7Cn0K\nClFXaWRnZXQjbWVudUZyYW1lewoJYmFja2dyb3VuZC1jb2xvcjogRk9DVVNCQUNLR1JPVU5EQ09M\nT1I7Cn0KCi8qIENIRUNLIEJPWCAqLwpRQ2hlY2tCb3g6OmluZGljYXRvciB7Cgl3aWR0aDogMThw\neDsKCWhlaWdodDogMThweDsKfQoKUU1lbnU6OmluZGljYXRvcjpub24tZXhjbHVzaXZlIHsKCXdp\nZHRoOiAxNHB4OwoJaGVpZ2h0OiAxNHB4OwoJcGFkZGluZy1sZWZ0OiAycHg7Cn0KUUNoZWNrQm94\nOjppbmRpY2F0b3I6Y2hlY2tlZCwgIFFNZW51OjppbmRpY2F0b3I6bm9uLWV4Y2x1c2l2ZTpjaGVj\na2VkIHsKICAgIGltYWdlOiAgdXJsKERJUk5BTUUvdWkvaW1hZ2VzL2NoZWNrZWRPbi5wbmcpCn0K\nUUNoZWNrQm94OjppbmRpY2F0b3I6dW5jaGVja2VkLCAgUU1lbnU6OmluZGljYXRvcjpub24tZXhj\nbHVzaXZlOnVuY2hlY2tlZCAgewogICAgaW1hZ2U6ICB1cmwoRElSTkFNRS91aS9pbWFnZXMvY2hl\nY2tlZE9mZi5wbmcpCn0KUUNoZWNrQm94OjppbmRpY2F0b3I6ZGlzYWJsZWQsICBRTWVudTo6aW5k\naWNhdG9yOm5vbi1leGNsdXNpdmU6ZGlzYWJsZWQgIHsKICAgIGltYWdlOiAgdXJsKERJUk5BTUUv\ndWkvaW1hZ2VzL2NoZWNrZWRPZmYucG5nKQp9CgovKiBSQURJTyBCVVRUT04gKi8KUVJhZGlvQnV0\ndG9uOjppbmRpY2F0b3IgewoJd2lkdGg6IDE4cHg7CgloZWlnaHQ6IDE4cHg7Cn0KUVJhZGlvQnV0\ndG9uOjppbmRpY2F0b3I6Y2hlY2tlZCB7CiAgICBpbWFnZTogIHVybChESVJOQU1FL3VpL2ltYWdl\ncy9yYWRpb09uLnBuZykKfQpRUmFkaW9CdXR0b246OmluZGljYXRvcjp1bmNoZWNrZWQgewogICAg\naW1hZ2U6ICB1cmwoRElSTkFNRS91aS9pbWFnZXMvcmFkaW9PZmYucG5nKQp9CgojbmFtZXNwYWNl\nRWRpdCwgUUNvbWJvQm94LCBRTGluZUVkaXQgewoJaGVpZ2h0OiAyNXB4OwoJcGFkZGluZzogMCA0\ncHg7Cglib3JkZXItcmFkaXVzOiAwcHg7CgliYWNrZ3JvdW5kLWNvbG9yOiByZ2IoMjU1LCAyNTUs\nIDI1NSwgNSk7Cglib3JkZXItYm90dG9tOiAwcHggc29saWQgcmdiKDI1NSwgMjU1LCAyNTUsIDUw\nKTsKfQoKI25hbWVzcGFjZUVkaXQ6Zm9jdXMsIFFDb21ib0JveDpmb2N1cywgUUxpbmVFZGl0OmZv\nY3VzICB7Cglib3JkZXI6IDBweCBzb2xpZCBGT0NVU0JBQ0tHUk9VTkRDT0xPUjsKCWJhY2tncm91\nbmQtY29sb3I6IHJnYigyNTUsIDI1NSwgMjU1LCA1KTsKCWJvcmRlci1ib3R0b206IDJweCBzb2xp\nZCBGT0NVU0JBQ0tHUk9VTkRDT0xPUjsKfQoKCiNuYW1lc3BhY2VFZGl0LCBRQ29tYm9Cb3gsIFFM\naW5lRWRpdCAgewoJc2VsZWN0aW9uLWNvbG9yOiByZ2IoMjU1LCAyNTUsIDI1NSwgMjU1KTsKCXNl\nbGVjdGlvbi1iYWNrZ3JvdW5kLWNvbG9yOiBGT0NVU0JBQ0tHUk9VTkRDT0xPUjsKfQoKCiNuYW1l\nc3BhY2VFZGl0OmhvdmVyLCBRQ29tYm9Cb3g6aG92ZXIsIFFMaW5lRWRpdDpob3ZlciB7CgliYWNr\nZ3JvdW5kLWNvbG9yOiByZ2IoMjU1LCAyNTUsIDI1NSwgMTApOwp9CgoKI3ByZXZpZXdCdXR0b25z\nIFFQdXNoQnV0dG9uIHsKICAgIGhlaWdodDogMzVweDsKCWJvcmRlci1yYWRpdXM6IDBweDsKCWJv\ncmRlcjogMHB4IHNvbGlkIHJnYmEoMCwwLDAsNTApOwoJcGFkZGluZzogMCA4cHg7Cgljb2xvcjog\ncmdiKDI1NSwgMjU1LCAyNTUpOwogICAgYmFja2dyb3VuZC1jb2xvcjogRk9DVVNCQUNLR1JPVU5E\nQ09MT1I7Cn0KCgojcHJldmlld0J1dHRvbnMgUVB1c2hCdXR0b246aG92ZXIgewoJY29sb3I6IHJn\nYigyNTUsIDI1NSwgMjU1LCAxNTApOwp9CgoKUVB1c2hCdXR0b24jdXBkYXRlQnV0dG9uIHsKICAg\nIGhlaWdodDogMjRweDsKICAgIGJvcmRlci1yYWRpdXM6IDFweDsKICAgIGJhY2tncm91bmQtY29s\nb3I6IHJnYigyNTUsIDI1NSwgMjU1LCAyMjApOwoJY29sb3I6IEZPQ1VTQkFDS0dST1VORENPTE9S\nOwp9CgpRUHVzaEJ1dHRvbiN1cGRhdGVCdXR0b246aG92ZXIgewogICAgYmFja2dyb3VuZC1jb2xv\ncjogcmdiKDI1NSwgMjU1LCAyNTUsIDI1NSk7Cn0KCgojbWFpbldpZGdldCB7CiAgICBwYWRkaW5n\nOiAwcHg7CiAgICBtYXJnaW46MHB4Owp9CgojbXlMYWJlbCB7CiAgICBwYWRkaW5nLWxlZnQ6IDVw\neDsKICAgIGJhY2tncm91bmQtY29sb3I6IHRyYW5zcGFyZW50Owp9CgojbWFpbldpZGdldDpob3Zl\nciwgI215TGFiZWw6aG92ZXIgewogICAgYmFja2dyb3VuZDogRk9DVVNCQUNLR1JPVU5EQ09MT1I7\nCiAgICBjb2xvcjogcmdiKDI1NSwgMjU1LCAyNTUpOwp9CgojbXlPcHRpb24gewogICAgY29sb3I6\nIHJnYigwLCAwLCAwLCA1MCk7CiAgICBtYXJnaW46IDFweDsKICAgIGJhY2tncm91bmQtY29sb3I6\nIHJnYigyNTUsIDI1NSwgMjU1LCA1KTsKfQoKI215T3B0aW9uOmhvdmVyIHsKICAgIGNvbG9yOiBG\nT0NVU0JBQ0tHUk9VTkRDT0xPUjsKICAgIGJhY2tncm91bmQtY29sb3I6IHJnYigyNTUsIDI1NSwg\nMjU1LCAyMjApOwp9\n'
if __name__ == '__main__':
    import studiolibrary
    studiolibrary.main()
