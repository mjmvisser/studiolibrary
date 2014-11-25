#Embedded file name: C:/Users/hovel/Dropbox/packages/studioLibrary/1.5.8/build27/studioLibrary\gui.py
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

import studioLibrary
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
    if studioLibrary.isPySide():
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


def styleSheet(self):
    try:
        if isinstance(self, studioLibrary.MainWindow):
            return QtCore.QString('')
    except:
        pass

    return __test(self)


try:
    __test = QtGui.QMainWindow.styleSheet
    QtGui.QMainWindow.styleSheet = styleSheet
    QtGui.QMainWindow.styleSheet = styleSheet
except:
    import traceback
    traceback.print_exc()

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


class LibrarySettings(studioLibrary.Settings):

    def __init__(self, name):
        studioLibrary.Settings.__init__(self, 'Library', name)
        self.setdefault('sort', studioLibrary.Ordered)
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
        studioLibrary.loadUi(self)

    def window(self):
        return self.parent().window()

    def mousePressEvent(self, event):
        self.close()


class PreviewWidget(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        studioLibrary.loadUi(self)

    def window(self):
        return self.parent().window()


class FoldersFrame(QtGui.QFrame):

    def __init__(self, *args):
        QtGui.QFrame.__init__(self, *args)
        studioLibrary.loadUi(self)

    def window(self):
        return self.parent().window()


class InfoFrame(QtGui.QMainWindow):

    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self, parent, QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        studioLibrary.loadUi(self)

    def _show(self, rect):
        QtGui.QMainWindow.show(self)


class AboutDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        studioLibrary.loadUi(self)


class WelcomeDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        studioLibrary.loadUi(self)
        self.ui.cancelButton.clicked.connect(self.close)
        self.ui.browseButton.clicked.connect(self.browse)
        self.setWindowTitle('Studio Library - %s' % studioLibrary.version())
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
        if studioLibrary.isUpdateAvailable():
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
            print 'studioLibrary: Text margins are not supported!'

        self.pushButton = SearchButton(self)
        self.pushButton.setObjectName('searchButton')
        self.pushButton.move(-3, 3)
        self.pushButton.show()
        pixmap = studioLibrary.pixmap('search', QtGui.QColor(255, 255, 255, 200))
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
        studioLibrary.loadUi(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setObjectName('statusWidget')
        self.setFixedHeight(18)
        self.setMinimumWidth(5)
        self._timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self._timer, QtCore.SIGNAL('timeout()'), self.clear)

    def setError(self, text, msec = statusMSec):
        icon = studioLibrary.icon('error14', ignoreOverride=True)
        self.ui.button.setIcon(icon)
        self.ui.message.setStyleSheet('color: rgb(222, 0, 0);')
        self.setText(text, msec)

    def setWarning(self, text, msec = statusMSec):
        icon = studioLibrary.icon('warning14', ignoreOverride=True)
        self.ui.button.setIcon(icon)
        self.ui.message.setStyleSheet('color: rgb(222, 180, 0);')
        self.setText(text, msec)

    def setInfo(self, text, msec = statusMSec):
        icon = studioLibrary.icon('info14', ignoreOverride=True)
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
        icon = studioLibrary.icon('blank', ignoreOverride=True)
        self.ui.button.setIcon(icon)


class Communicate(QtCore.QObject):
    if studioLibrary.isPySide():
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
        self.setIcon(studioLibrary.icon('thumbnail'))

    def setSize(self, w, h):
        self._size = QtCore.QSize(w, h)
        self.setIconSize(self._size)
        self.setFixedSize(self._size)

    def setDirname(self, dirname):
        self._sequenceTimer.setDirname(dirname)
        if self._sequenceTimer.frames():
            self.setIcon(studioLibrary.icon(self._sequenceTimer.frames()[0]))

    def enterEvent(self, event):
        self._sequenceTimer.start()

    def leaveEvent(self, event):
        self._sequenceTimer.pause()

    def mouseMoveEvent(self, event):
        if isControlModifier():
            percent = 1.0 - float(self.width() - event.pos().x()) / float(self.width())
            frame = int(self._sequenceTimer.duration() * percent)
            self._sequenceTimer.setCurrentFrame(frame)
            self.setIcon(studioLibrary.icon(self._sequenceTimer.currentFilename()))

    def frameChanged(self, filename):
        if not isControlModifier():
            self._filename = filename
            self.setIcon(studioLibrary.icon(filename))

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
        studioLibrary.loadUi(self)
        self.setObjectName('studioLibrary' + name)
        analytics = studioLibrary.Analytics()
        analytics.logScreen('Main')
        if mutils.isMaya():
            import maya.cmds
            mayaOS = maya.cmds.about(os=True)
            mayaVersion = maya.cmds.about(v=True)
            aboutMaya = (mayaVersion + '-' + mayaOS).replace(' ', '-')
            analytics.logEvent('About-Maya', aboutMaya)
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
        self._sort = studioLibrary.Ordered
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
        pixmap = studioLibrary.icon('cog', QtGui.QColor(255, 255, 255, 220), ignoreOverride=True)
        self.ui.settingsButton.setIcon(pixmap)
        pixmap = studioLibrary.icon('addItem', QtGui.QColor(255, 255, 255, 240), ignoreOverride=True)
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
        self.ui.newMenu.setIcon(studioLibrary.icon('new14'))
        self.ui.newMenu.setTitle('New')
        action = QtGui.QAction(studioLibrary.icon('folder14'), 'Folder', self.ui.newMenu)
        self.connect(action, QtCore.SIGNAL('triggered(bool)'), self.showCreateFolderDialog)
        self.ui.newMenu.addAction(action)
        self.ui.editRecordMenu = ContextMenu(self)
        self.ui.editRecordMenu.setTitle('Edit')
        self.ui.printPrettyAction = QtGui.QAction(studioLibrary.icon('print'), 'Print', self.ui.editRecordMenu)
        action.connect(self.ui.printPrettyAction, QtCore.SIGNAL('triggered(bool)'), self.printPrettyRecords)
        self.ui.editRecordMenu.addAction(self.ui.printPrettyAction)
        self.ui.deleteRecordAction = QtGui.QAction(studioLibrary.icon('trash'), 'Delete', self.ui.editRecordMenu)
        action.connect(self.ui.deleteRecordAction, QtCore.SIGNAL('triggered(bool)'), self.deleteSelectedRecords)
        self.ui.editRecordMenu.addAction(self.ui.deleteRecordAction)
        self.ui.deleteRenameAction = QtGui.QAction(studioLibrary.icon('rename'), 'Rename', self.ui.editRecordMenu)
        action.connect(self.ui.deleteRenameAction, QtCore.SIGNAL('triggered(bool)'), self.renameSelectedRecord)
        self.ui.editRecordMenu.addAction(self.ui.deleteRenameAction)
        self.ui.showRecordAction = QtGui.QAction(studioLibrary.icon('folder14'), 'Show in folder', self.ui.editRecordMenu)
        action.connect(self.ui.showRecordAction, QtCore.SIGNAL('triggered(bool)'), self.openSelectedRecords)
        self.ui.editRecordMenu.addAction(self.ui.showRecordAction)
        self.ui.editFolderMenu = ContextMenu(self)
        self.ui.editFolderMenu.setTitle('Edit')
        action = QtGui.QAction(studioLibrary.icon('trash'), 'Delete', self.ui.editFolderMenu)
        action.connect(action, QtCore.SIGNAL('triggered(bool)'), self.deleteSelectedFolders)
        self.ui.editFolderMenu.addAction(action)
        action = QtGui.QAction(studioLibrary.icon('rename'), 'Rename', self.ui.editFolderMenu)
        action.connect(action, QtCore.SIGNAL('triggered(bool)'), self.renameSelectedFolder)
        self.ui.editFolderMenu.addAction(action)
        action = QtGui.QAction(studioLibrary.icon('folder14'), 'Show in folder', self.ui.editFolderMenu)
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
        self.ui.settingsMenu.setIcon(studioLibrary.icon('settings14'))
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
        if mutils.isMaya():
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
        if mutils.isMaya():
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
            title = 'Studio Library - ' + studioLibrary.__version__ + ' - ' + self.name()
        if self.isLocked():
            title += ' (Locked)'
        self.setWindowTitle(title)
        if mutils.isMaya() and self._mayaDockWidget:
            import maya.cmds
            maya.cmds.dockControl(self._mayaDockWidget, edit=True, label=title)

    def setLocked(self, value):
        if value:
            self.ui.createButton.setEnabled(True)
            self.ui.createButton.setIcon(studioLibrary.icon('lock', QtGui.QColor(222, 222, 222, 222), ignoreOverride=True))
        else:
            self.ui.createButton.setEnabled(True)
            self.ui.createButton.setIcon(studioLibrary.icon('addItem', ignoreOverride=True))
            self.ui.createButton.show()
        self.updateWindowTitle()
        self._isLocked = value

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
        if mutils.isMaya():
            import maya.cmds
            if self._mayaDockWidget:
                return not maya.cmds.dockControl(self._mayaDockWidget, query=True, floating=True)
        return False

    def dockArea(self):
        if not self.parent():
            return None
        return self._dockArea

    def dockLocationChanged(self, area):
        if studioLibrary.isPySide():
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
        if mutils.isMaya() and self._mayaDockWidget:
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
        if mutils.isMaya():
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
        if mutils.isMaya():
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
            result = []
            for i in range(2, len(value), 3):
                result.append(value[i])

            result = ''.join(result)
            return result.decode('base64')

        def __encode(value):
            end = False
            result = []
            a = value.encode('base64')
            for block in a:
                r = __rand()
                if block == '=':
                    end = True
                if end and block != '=':
                    break
                result.extend([r, block])

            return ''.join(result)

        def __rand():
            return ''.join([ random.choice('FEW57wefABCxqJHPEYEUDFJCVDFCDwpkyncvr135965dfbxcc') for i in xrange(2) ])

        style = studioLibrary.dirname() + '/style.qss'
        style2 = studioLibrary.dirname() + '/style.qssx'
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
        data = data.replace('DIRNAME', studioLibrary.dirname())
        data = data.replace('FOCUSBACKGROUNDCOLOR', self.color())
        data = data.replace('FOREGROUNDCOLOR', 'rgb(255, 255, 255)')
        data = data.replace('BACKGROUNDCOLOR', 'rgb(30, 30, 30)')
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
            pixmap = studioLibrary.icon('addItem', color)
            self.ui.createButton.setIcon(pixmap)
        import inspect
        try:
            inspect.getfile(QtGui.QMainWindow.setStyleSheet)
        except:
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
        studioLibrary.removeWindow(self.name())

    def setName(self, name):
        self._name = name

    def name(self):
        return self._name

    def settings(self):
        return studioLibrary.LibrarySettings(self.name())

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
            background = background.replace('DIRNAME', studioLibrary.dirname())
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

    def styleSheet(self):
        return QtCore.QString('')

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
            raise Exception('Cannot find the root folder path \'%s\'. To set the root folder please use the command: studioLibrary.main(root="C:/path")' % path)
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
        if sort == studioLibrary.Ordered:
            self.ui.recordsWidget.setDropEnabled(True)
        else:
            self.ui.recordsWidget.setDropEnabled(False)
        self._sortNameAction.setChecked(studioLibrary.Name == sort)
        self._sortOrderedAction.setChecked(studioLibrary.Ordered == sort)
        self._sortModifiedAction.setChecked(studioLibrary.Modified == sort)
        if force:
            self.reloadRecords()

    def setSortName(self):
        self.setSort(studioLibrary.Name)

    def setSortModified(self):
        self.setSort(studioLibrary.Modified)

    def setSortOrdered(self):
        self.setSort(studioLibrary.Ordered)

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
            studioLibrary.unloadPlugin(plugin)
            del self._plugins[name]
        else:
            print "Cannot find plugin with name '%s'" % name

    def loadPlugin(self, name):
        if name not in self._plugins.keys():
            plugin = studioLibrary.loadPlugin(name, self)
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
        analytics = studioLibrary.Analytics()
        analytics.logScreen('Help')
        import webbrowser
        webbrowser.open('http://www.studioLibrary.com')

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
        for name in studioLibrary.libraries():
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
        studioLibrary.loadUi(self)
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
        folder = studioLibrary.Folder(path)
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
                folder = studioLibrary.Folder(dirname)
                pixmap = QtGui.QIcon(folder.pixmap())
                if pixmap:
                    return QtGui.QIcon(folder.pixmap())
        if role == QtCore.Qt.FontRole:
            if index.column() == 0:
                dirname = str(self.filePath(index))
                folder = studioLibrary.Folder(dirname)
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
            folder = studioLibrary.Folder(str(path), parent=self)
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
            folder = studioLibrary.Folder(path, parent=self)
            folder.save()
            self.selectFolder(folder.dirname())

    def folderAt(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        index = self.model().mapToSource(index)
        return studioLibrary.Folder(self.model().sourceModel().filePath(index), parent=self)


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


_data = '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\n'
if __name__ == '__main__':
    import studioLibrary
    studioLibrary.main()
