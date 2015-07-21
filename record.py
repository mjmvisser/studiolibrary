#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary\record.py
"""
"""
import os
import shutil
import studiolibrary
try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore

def createRecordFromPath(path, window):
    """
    @type path: str
    @type window: QtGui.QWidget
    @rtype Record | None
    """
    plugins = window.plugins().values()
    for plugin in plugins:
        if plugin.match(path):
            name = os.path.basename(path)
            folder = studiolibrary.Folder(os.path.dirname(path))
            return plugin.record(folder=folder, name=name, plugin=plugin, parent=window)


class RecordEvent:

    def __init__(self, record):
        """
        @type record: Record
        """
        self._state = True
        self._record = record

    def record(self):
        """
        @rtype: Record
        """
        return self._record


class Record(studiolibrary.Folder):
    savedEventHook = studiolibrary.EventHook()
    savingEventHook = studiolibrary.EventHook()

    @staticmethod
    def disconnectAllEventHooks():
        """
        """
        Record.savedEventHook.disconnectAll()
        Record.savingEventHook.disconnectAll()

    def __init__(self, folder = None, name = None, plugin = None, parent = None, data = None):
        """
        @type folder: Folder
        @type name: str
        @type parent: QtCore.QObject
        @type data: dict[]
        """
        self._margin = 4
        self._rect = None
        self._name = None
        self._index = None
        self._pixmap = None
        self._plugin = None
        self._folder = None
        if data:
            self.setParent(parent)
            self.setPlugin(plugin)
            self.setName(name)
            self.setFolder(folder)
            studiolibrary.Folder.__init__(self, self.path(), parent, read=False)
            self.update(data)
        else:
            self.setParent(parent)
            self.setPlugin(plugin)
            self.setName(name)
            self.setFolder(folder)
            studiolibrary.Folder.__init__(self, self.path(), parent)

    @classmethod
    def createFromPath(cls, path, plugin):
        """
        @type path: str
        @type plugin: str
        @rtype: Record
        """
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        folder = studiolibrary.Folder(dirname)
        plugin = studiolibrary.loadPlugin(plugin)
        r = cls(folder=folder)
        r.setName(basename)
        r.setPlugin(plugin)
        return r

    def rename(self, path, save = True, force = False):
        """
        @type path: str
        @type save: bool
        @type force: bool
        """
        path = path.replace('\\', '/')
        dirname, basename, extension = studiolibrary.splitPath(path)
        if extension != self.plugin().extension():
            path += self.plugin().extension()
        studiolibrary.Folder.rename(self, path, save, force)

    def setName(self, name):
        """
        @type name: str
        """
        self._name = name

    def name(self):
        """
        @rtype: str
        """
        plugin = self.plugin()
        name = self._name
        if plugin and name:
            extension = plugin.extension()
            if name and extension not in name:
                return name + extension
        return name or ''

    def setFolder(self, folder):
        """
        @type folder: Folder
        """
        self._folder = folder

    def setPath(self, path):
        """
        @type path: str
        """
        if not path.endswith('.dict') and os.path.isdir(path):
            self.setName(os.path.basename(path))
            self.setFolder(studiolibrary.Folder(os.path.dirname(path)))
            path = self.path()
        studiolibrary.Folder.setPath(self, path)

    def path(self):
        """
        @rtype: str
        """
        if self.name():
            return self.folder().dirname() + '/' + self.name() + '/.studioLibrary/record.dict'
        else:
            return ''

    def folder(self):
        """
        @rtype : studiolibrary.Folder
        """
        return self._folder

    def setPlugin(self, plugin):
        """
        @type : studiolibrary.Plugin
        """
        self._plugin = plugin

    def plugin(self):
        """
        @rtype : studiolibrary.Plugin
        """
        return self._plugin

    def setContextMenu(self, menu):
        """
        @type menu: QtCore.QMenu
        """
        self.window().setContextMenu(menu)

    def icon(self):
        """
        @rtype: str
        """
        if self.errors():
            return studiolibrary.image('pluginError')
        icon_ = self.get('icon', '') or 'thumbnail.jpg'
        icon_ = icon_.replace('DIRNAME', self.dirname())
        if '/' not in icon_:
            icon2 = self.dirname() + '/' + icon_
            return icon2
        return icon_

    def pixmap(self):
        """
        @rtype: QtCore.QPixmap
        """
        if not self.iconVisibility():
            return studiolibrary.pixmap('')
        if not self._pixmap:
            icon = self.icon()
            if os.path.exists(icon):
                self._pixmap = studiolibrary.pixmap(icon)
            else:
                self._pixmap = studiolibrary.pixmap(studiolibrary.image('thumbnail'))
        return self._pixmap

    def save(self, content = None, icon = None, version = True, force = False):
        """
        @type content: list[str]
        @type icon: str
        @type version: str
        @type force: bool
        """
        e = RecordEvent(record=self)
        self.savingEvent(e)
        if not content:
            content = []
        if not self.name():
            raise Exception('Cannot save record! Please set a name for the record.')
        if not self.plugin():
            raise Exception('Cannot save record! Please set a plugin for the record.')
        window = self.window()
        if window:
            folders = window.selectedFolders()
            if len(folders) != 1:
                raise Exception('Please select ONE folder.')
            self.setFolder(folders[0])
        if self.exists():
            if force:
                self.retire()
            elif window:
                result = window.questionDialog("The chosen name '%s' already exists!\n Would you like to create a new version?" % self.name(), 'New version')
                if result == QtGui.QMessageBox.Yes:
                    self.retire()
                else:
                    raise Exception("Cannot save record because record already exists! '%s'" % self.name())
            else:
                raise Exception("Cannot save record because record already exists! '%s'" % self.name())
        studiolibrary.Folder.save(self)
        if icon:
            shutil.move(icon, self.icon())
        for path in content or []:
            basename = os.path.basename(path)
            destination = self.dirname() + '/' + basename
            shutil.move(path, destination)

        self.reloadRecords()
        studiolibrary.analytics().logEvent('Create', self.plugin().name())
        self.savedEvent(e)
        if window:
            selected = window.selectedRecords()
            if not selected and window.filter():
                msg = 'Successfully created! \nHowever it could not be selected \nbecause a search filter is active!'
                window.informationDialog(msg)

    def delete(self):
        """
        """
        studiolibrary.Folder.delete(self)
        self.reloadRecords()

    def reloadRecords(self):
        """
        """
        if self.window():
            if self.window().ui.previewWidget:
                self.window().ui.previewWidget.close()
            self.window().reloadRecords()
            self.window().selectRecords([self])

    def savingEvent(self, recordEvent):
        self.savingEventHook.emit(recordEvent)

    def savedEvent(self, recordEvent):
        self.savedEventHook.emit(recordEvent)

    def mousePressEvent(self, event):
        self.clicked()
        self.plugin().hideInfoWidget()
        return QtGui.QListView.mousePressEvent(event._parent, event)

    def mouseReleaseEvent(self, event):
        if event._record:
            QtGui.QListView.mouseReleaseEvent(event._parent, event)

    def mouseMoveEvent(self, event):
        self.plugin().infoWindow().move(event.globalX() + 15, event.globalY() + 20)

    def mouseEnterEvent(self, event):
        self.plugin().showInfoWidget(self, wait=1500)

    def mouseLeaveEvent(self, event):
        self.plugin().hideInfoWidget()

    def keyPressEvent(self, event):
        self.plugin().hideInfoWidget()

    def keyReleaseEvent(self, event):
        self.plugin().hideInfoWidget()

    def repaint(self):
        if self.index():
            self.parent().update(self.index())

    def index(self):
        return self._index

    def clicked(self):
        self.plugin().showPreviewWidget(None, self)

    def doubleClicked(self):
        pass

    def selectionChanged(self, *args, **kwargs):
        pass

    def contextMenu(self, menu, records):
        if not self.window().isLocked():
            menu.addMenu(self.window().ui.newMenu)
            menu.addMenu(self.window().ui.editRecordMenu)
        menu.addSeparator()
        menu.addMenu(self.window().ui.sortMenu)
        menu.addMenu(self.window().ui.settingsMenu)

    def indexData(self, parent, index, role):
        """
        This method is abstract and can be re-implemented in any sub-class.
        """
        name = self.name()
        if role == QtCore.Qt.DecorationRole:
            return parent.iconSize()
        if role == QtCore.Qt.DisplayRole:
            if '.deleted' in name:
                name = name.split('.')
                name = '.'.join(name[:-2])
            if self.parent().isShowLabels() or self.window().viewMode() != QtGui.QListView.IconMode:
                return ' ' + name
            else:
                return ''

    def setRect(self, rect):
        self._rect = rect

    def setMargin(self, margin):
        self._margin = margin

    def rect(self):
        spacing = self.parent().spacing()
        padding = self._margin
        r = self._rect
        if r:
            iconMode = self.window().viewMode() == QtGui.QListView.IconMode
            if iconMode:
                if self.parent().isShowLabels():
                    margin = 13
                else:
                    margin = 0
                rect = QtCore.QRect(r.x() + spacing + padding, r.y() + spacing + padding, r.width() - (spacing + padding * 2) + 1, r.height() - (spacing + (margin + padding * 2 - 1)))
            else:
                rect = QtCore.QRect(r.x() + spacing + 2, r.y() + spacing + 2, r.height() - spacing - 2, r.height() - spacing - 3)
            return rect

    def visualRect(self):
        spacing = self.parent().spacing()
        r = self._rect
        if r:
            return QtCore.QRect(r.x() + spacing, r.y() + spacing, r.width() - spacing, r.height() - spacing)
        return self.rect()

    def paint(self, painter, option):
        painter.save()
        rect = self.rect()
        if rect:
            _isActive = False
            if option.state & QtGui.QStyle.State_Selected:
                _isActive = True
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            if _isActive:
                color = self.window().QColor()
                painter.setBrush(QtGui.QBrush(color))
            else:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 20)))
            painter.drawRect(self.visualRect())
            isListView = self.window().ui.recordsWidget.viewMode() == QtGui.QListView.ListMode
            if self.window().isShowLabels() or isListView:
                textRect = self.visualRect()
                textRect.setHeight(textRect.height() - 1)
                textRect.setLeft(textRect.left() + 2)
                textRect.setWidth(textRect.width() - 4)
                font = QtGui.QFont()
                metrics = QtGui.QFontMetrics(font)
                if isListView:
                    textRect.setLeft(textRect.left() + 25)
                if _isActive:
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
                else:
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 200)))
                if metrics.width(self.name()) < textRect.width() and not isListView:
                    painter.drawText(textRect, QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, self.name())
                else:
                    painter.drawText(textRect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom, self.name())
            pixmap = self.pixmap()
            if isinstance(pixmap, QtGui.QPixmap):
                rect = QtCore.QRect(rect.x() - 1, rect.y() - 1, rect.width() + 1, rect.height() + 1)
                painter.drawPixmap(rect, pixmap)
            if not isListView:
                pixmap = self.plugin().pixmap()
                if isinstance(pixmap, QtGui.QPixmap):
                    painter.setOpacity(0.5)
                    rect = QtCore.QRect(rect.x(), rect.y(), 13, 13)
                    painter.drawPixmap(rect, pixmap)
        painter.restore()
