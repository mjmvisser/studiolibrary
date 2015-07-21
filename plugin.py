#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary\plugin.py
"""
"""
import os
import imp
import studiolibrary
try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore

__all__ = ['loadPlugin',
 'unloadPlugin',
 'Plugin',
 'PluginSettings']

class PluginSettings(studiolibrary.Settings):

    def __init__(self, name):
        studiolibrary.Settings.__init__(self, 'Plugins', name)


class TracebackWidget(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        studiolibrary.loadUi(self)

    def setTraceback(self, text):
        self.ui.label.setText(text)


def loadedPlugins():
    """
    @rtype: dict[]
    """
    return Plugin._plugins


def loadPlugin(path, parent = None):
    """
    @type path: str
    @type parent: QWidget
    """
    path = path.replace('\\', '/')
    if os.path.exists(path):
        dirname, basename, extension = studiolibrary.splitPath(path)
        module = imp.load_source(basename, path)
    else:
        exec 'import ' + path
        module = eval(path)
    p = module.Plugin(parent)
    if not parent:
        Plugin._plugins.setdefault(p.name(), p)
    p.setPath(path)
    p.load()
    Plugin._plugins.setdefault(p.name(), p)
    return p


def unloadPlugin(p):
    """
    @type p: Plugin
    """
    p.unload()
    if p.name() in Plugin._plugins:
        del Plugin._plugins[p.name()]


class Plugin(QtCore.QObject):
    _plugins = {}

    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        self._loaded = False
        self._icon = ''
        self._name = None
        self._action = None
        self._pixmap = None
        self._settings = None
        self._extension = None
        self._infoWidget = None
        self._editWidget = None
        self._createWidget = None
        self._previewWidget = None
        self._tracebackWidget = None
        self._currentRecord = None
        self._record = studiolibrary.Record
        self._infoTimer = QtCore.QTimer(self)
        self._infoTimer.setSingleShot(True)
        self.connect(self._infoTimer, QtCore.SIGNAL('timeout()'), self._showInfoWidget)

    def folderSelectionChanged(self, folder1, folder2):
        pass

    def recordSelectionChanged(self, record1, record2):
        pass

    def recordContextMenu(self, menu, records):
        for record in records:
            if isinstance(record, self._record):
                record.contextMenu(menu, records)

    def infoWindow(self):
        return self.window().ui.infoFrame

    def setInfoWidget(self, widget):
        self._infoWidget = widget

    def infoWidget(self, parent, record):
        if self._infoWidget:
            return self.loadWidget(self._infoWidget, parent, record)

    def hideInfoWidget(self):
        if self._infoWidget:
            self._infoTimer.stop()
            self._currentRecord = None
            self.parent().ui.infoFrame.hide()

    def showInfoWidget(self, record, wait = None):
        if self._infoWidget:
            self._currentRecord = record
            if wait:
                self._infoTimer.start(wait)
            else:
                self._showInfoWidget()

    def _showInfoWidget(self):
        record = self._currentRecord
        parent = self.infoWindow().ui.mainFrame
        self.deleteChildren(parent)
        widget = self.infoWidget(parent, record)
        if widget:
            width = 190
            height = 80
            if studiolibrary.isPySide():
                self.infoWindow().setFixedWidth(width)
                self.infoWindow().setFixedHeight(height)
            else:
                widget.parent().setFixedWidth(width)
                widget.parent().setFixedHeight(height)
            self.infoWindow().show()

    def setCreateWidget(self, widget):
        self._createWidget = widget

    def createWidget(self, parent, record):
        return self.loadWidget(self._createWidget, parent, record)

    def showCreateWidget(self, record = None):
        folders = self.window().selectedFolders()
        if not folders:
            self.window().setError('Please create or select a folder to add to.')
        elif len(folders) > 1:
            self.window().setError('Too many folders selected! Please select only one folder to add to.')
        else:
            folder, = folders
            if not record:
                record = self.record(folder, parent=self.window().ui.recordsWidget)
                record.setPlugin(self)
            _w = self.createWidget(None, record)
            self.window().setCreateWidget(_w)

    def setEditWidget(self, widget):
        self._editWidget = widget

    def editWidget(self, parent, record):
        return self.loadWidget(self._editWidget, parent, record)

    def showEditWidget(self, parent, record):
        if self._previewWidget:
            if self.window().ui.previewWidget:
                self.window().ui.previewWidget.close()
            widget = self.editWidget(parent, record)
            self.window().setPreviewWidget(widget)

    def setPreviewWidget(self, widget):
        self._previewWidget = widget

    def previewWidget(self, parent, record):
        return self.loadWidget(self._previewWidget, parent, record)

    def showPreviewWidget(self, parent, record):
        if self._previewWidget:
            if self.window().ui.previewWidget:
                self.window().ui.previewWidget.close()
            widget = self.previewWidget(parent, record)
            self.window().setPreviewWidget(widget)

    @staticmethod
    def loadWidget(widget, parent, record):
        w = None
        try:
            if record.errors():
                w = TracebackWidget(None)
                w.setTraceback(record.errors())
            elif widget:
                w = widget(None, record)
        except:
            import traceback
            msg = traceback.format_exc()
            w = TracebackWidget(None)
            w.setTraceback(msg)
            traceback.print_exc()

        if w and parent:
            parent.layout().addWidget(w)
        return w

    @staticmethod
    def deleteWidget(widget):
        widget.hide()
        widget.close()
        widget.destroy()
        del widget

    def deleteChildren(self, widget):
        for i in range(widget.layout().count()):
            child = widget.layout().itemAt(i).widget()
            widget.layout().removeWidget(child)
            self.deleteWidget(child)

    def tracebackWidget(self, parent):
        if not self._tracebackWidget:
            self._tracebackWidget = TracebackWidget(parent)
        return self._tracebackWidget

    def match(self, path):
        if path.endswith(self.extension()):
            return True
        return False

    def pixmap(self):
        if not self._pixmap:
            icon = self.icon()
            if os.path.exists(str(icon)):
                self._pixmap = QtGui.QPixmap(icon)
        return self._pixmap

    def setExtension(self, extension):
        if not extension.startswith('.'):
            extension = '.' + extension
        self._extension = extension

    def extension(self):
        """
        @rtype : str
        """
        if not self._extension:
            return '.' + self.name().lower()
        return self._extension

    def setRecord(self, record):
        self._record = record

    def record(self, *args, **kwargs):
        return self._record(*args, **kwargs)

    def dirname(self):
        import inspect
        return os.path.dirname(inspect.getfile(self.__class__))

    def settings(self):
        if not self._settings:
            self._settings = studiolibrary.Settings('Plugins', self.name())
        return self._settings

    def setName(self, name):
        self._name = name

    def name(self):
        return self._name

    def records(self, folder, parent):
        return list()

    def setPath(self, path):
        self._path = path

    def path(self):
        return self._path

    def setIcon(self, icon):
        self._icon = icon

    def icon(self):
        return self._icon

    def isLoaded(self):
        return self._loaded

    def window(self):
        if self.parent():
            return self.parent().window()

    def load(self):
        if self.window():
            self._action = QtGui.QAction(studiolibrary.icon(self.icon()), self.name(), self.window().ui.newMenu)
            self.window().connect(self._action, QtCore.SIGNAL('triggered(bool)'), self.showCreateWidget)
            self.window().ui.newMenu.addAction(self._action)

    def unload(self):
        if self.window() and self._action:
            self.window().ui.newMenu.removeAction(self._action)
