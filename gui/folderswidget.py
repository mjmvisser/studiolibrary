#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\gui\folderswidget.py
import os
import logging
from PySide import QtGui
from PySide import QtCore
import studiolibrary
__all__ = ['FoldersWidget']
logger = logging.getLogger(__name__)

class FolderCache():

    def __init__(self):
        self._cache = {}
        self._enabled = True

    def enabled(self):
        """
        :rtype: bool
        """
        return self._enabled

    def setEnabled(self, value):
        """
        :type value: bool
        """
        self._enabled = value

    def clear(self):
        """
        :rtype: None
        """
        self._cache = {}

    def cache(self):
        """
        :rtype: dict
        """
        return self._cache

    def fromPath(self, path):
        """
        :type path: str
        """
        if self.enabled():
            cache = self.cache()
            if path not in cache:
                cache[path] = studiolibrary.Folder(path)
            return cache[path]
        return studiolibrary.Folder(path)


class FoldersWidget(QtGui.QTreeView):
    CACHE_ENABLED = True
    SELECT_CHILDREN_ENABLED = False
    onDropped = QtCore.Signal(object)
    onDropping = QtCore.Signal(object)
    onClicked = QtCore.Signal(object)
    onOrderChanged = QtCore.Signal()
    onDoubleClicked = QtCore.Signal(object)
    onShowContextMenu = QtCore.Signal(object)
    onSelectionChanged = QtCore.Signal(object, object)

    def __init__(self, parent):
        """
        :type parent: studiolibrary.LibraryWidget
        """
        QtGui.QTreeView.__init__(self, parent)
        self._filter = []
        self._isLocked = False
        self._signalsEnabled = True
        self._selectChildren = False
        self._isSelectChildrenEnabled = self.SELECT_CHILDREN_ENABLED
        self._folderCache = FolderCache()
        self._sourceModel = FileSystemModel(self)
        proxyModel = SortFilterProxyModel(self)
        proxyModel.setSourceModel(self._sourceModel)
        self.setIndentation(7)
        self.setMinimumWidth(35)
        self.setAcceptDrops(True)
        self.setModel(proxyModel)
        self.setHeaderHidden(True)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setCacheEnabled(self.CACHE_ENABLED)
        self.setSelectionMode(QtGui.QTreeWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.connect(self.selectionModel(), QtCore.SIGNAL('selectionChanged (const QItemSelection&,const QItemSelection&)'), self.selectionChangedX)

    def setCacheEnabled(self, value):
        """
        :type value:  bool
        :rtype: None
        """
        self.folderCache().setEnabled(value)

    def cacheEnabled(self):
        """
        :rtype: bool
        """
        return self.folderCache().enabled()

    def setLocked(self, value):
        """
        :rtype: bool
        """
        self._isLocked = value

    def isLocked(self):
        """
        :rtype: bool
        """
        return self._isLocked

    def folderCache(self):
        """
        :rtype: FolderCache
        """
        return self._folderCache

    def clearCache(self):
        """
        :rtype: None
        """
        self._folderCache.clear()

    def folderFromIndex(self, index):
        """
        :type index: QtCore.QModelIndex
        :rtype: studiolibrary.Folder
        """
        path = self.pathFromIndex(index)
        return self.folderFromPath(path)

    def folderFromPath(self, path):
        """
        :type path: str
        :rtype: studiolibrary.Folder
        """
        folder = self.folderCache().fromPath(path)
        return folder

    def indexFromPath(self, path):
        """
        :type path: str
        :rtype: QtCore.QModelIndex
        """
        index = self.model().sourceModel().index(path)
        return self.model().mapFromSource(index)

    def pathFromIndex(self, index):
        """
        :type index: QtCore.QModelIndex
        :rtype: str
        """
        index = self.model().mapToSource(index)
        return self.model().sourceModel().filePath(index)

    def setSelectChildren(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self._isSelectChildrenEnabled = value

    def isSelectChildrenEnabled(self):
        """
        :rtype: bool
        """
        return self._isSelectChildrenEnabled

    def selectChildren(self):
        """
        :rtype: None
        """
        if not self.isSelectChildrenEnabled():
            logging.debug('Select children has been disabled')
            return
        paths = []
        folder = self.selectedFolder()
        folders = self.selectedFolders()
        if folders:
            for name in os.listdir(folder.path()):
                if '.' not in name:
                    path = folder.path() + '/' + name
                    paths.append(path)

        self.selectFoldersFromPaths(paths)

    def selectionChangedX(self, selected, deselected):
        """
        :type selected: list[studiolibrary.Folder]
        :type deselected: list[studiolibrary.Folder]
        :rtype: None
        """
        if self._signalsEnabled:
            self.onSelectionChanged.emit(selected, deselected)

    def currentState(self):
        """
        :rtype: None
        """
        state = []
        for folder in self.selectedFolders():
            state.append(folder.path())

        return state

    def restoreState(self, state):
        """
        :rtype state: list[]
        """
        self.selectFoldersFromPaths(state)

    def setRootPath(self, path, invalid = None):
        """
        :type path: str
        """
        self.model().sourceModel().setRootPath(path)
        self.model().sourceModel().setInvalid(invalid)
        index = self.indexFromPath(path)
        self.setRootIndex(index)

    def rootPath(self):
        """
        :rtype: str
        """
        return self.model().sourceModel().rootPath()

    def selectFolders(self, folders):
        """
        :type folders: list[studiolibrary.Folder]
        :rtype: None
        """
        paths = [ folder.path() for folder in folders ]
        self.selectFoldersFromPaths(paths)

    def selectFoldersFromPaths(self, paths):
        """
        :type paths: list[str]
        :rtype: None
        """
        if not paths:
            return
        self._signalsEnabled = False
        for path in paths[:-1]:
            self.selectFolderFromPath(path)

        self._signalsEnabled = True
        self.selectFolderFromPath(paths[-1])

    def selectFolder(self, folder, mode = QtGui.QItemSelectionModel.Select):
        """
        :type folder: studiolibrary.Folder
        :rtype: None
        """
        self.selectFolderFromPath(folder.path(), mode=mode)

    def expandParentsFromPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        for i in range(0, 4):
            path = os.path.dirname(path)
            index = self.indexFromPath(path)
            if index and not self.isExpanded(index):
                self.setExpanded(index, True)

    def selectFolderFromPath(self, path, mode = QtGui.QItemSelectionModel.Select):
        """
        :type path: str
        :rtype: None
        """
        self.expandParentsFromPath(path)
        index = self.indexFromPath(path)
        self.selectionModel().select(index, mode)

    def showRenameDialog(self, parent = None):
        """
        :rtype: None
        """
        folder = self.selectedFolder()
        if folder:
            name, accept = QtGui.QInputDialog.getText(parent, 'Rename Folder', 'New Name', QtGui.QLineEdit.Normal, folder.name())
            if accept:
                folder.rename(str(name))
                self.selectFolder(folder)

    def showDeleteDialog(self, parent = None):
        """
        :rtype: None
        """
        folders = self.selectedFolders()
        msg = 'Are you sure you want to delete the selected folders {0}'
        msg = msg.format([ folder.name() for folder in folders ])
        title = 'Deleted Selected Folders'
        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel
        result = QtGui.QMessageBox.question(parent, title, msg, buttons)
        if result == QtGui.QMessageBox.Yes:
            for folder in folders:
                folder.delete()

    def selectedFolder(self):
        """
        :rtype: None | studiolibrary.Folder
        """
        folders = self.selectedFolders()
        if folders:
            return folders[-1]

    def selectedFolders(self):
        """
        :rtype: list[studiolibrary.Folder]
        """
        folders = []
        for index in self.selectedIndexes():
            path = self.pathFromIndex(index)
            folder = self.folderFromPath(path)
            folders.append(folder)

        return folders

    def dragEnterEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        event.accept()

    def clearSelection(self):
        """
        :rtype: None
        """
        self.selectionModel().clearSelection()

    def dragMoveEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        mimeData = event.mimeData()
        if mimeData.hasUrls() and not self.isLocked():
            event.accept()
        else:
            event.ignore()
        folder = self.folderAt(event.pos())
        if folder:
            self.selectFolder(folder, QtGui.QItemSelectionModel.ClearAndSelect)

    def dropEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if self.isLocked():
            logger.debug('Folder is locked! Cannot accept drop!')
            return
        self.onDropped.emit(event)

    def mousePressEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if len(self.selectedFolders()) == 1:
            self._selectChildren = True
        if event.button() == QtCore.Qt.RightButton:
            QtGui.QTreeView.mousePressEvent(self, event)
            self.showMenu()
        else:
            QtGui.QTreeView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if event.button() == QtCore.Qt.MidButton:
            return
        QtGui.QTreeView.mouseReleaseEvent(self, event)
        if self._selectChildren:
            self.selectChildren()
            self._selectChildren = False

    def showMenu(self):
        """
        :rtype: None
        """
        menu = QtGui.QMenu(self)
        self.onShowContextMenu.emit(menu)
        if self.isLocked():
            self.lockedMenu(menu)
        else:
            self.contextMenu(menu)
        action = menu.exec_(QtGui.QCursor.pos())
        menu.close()

    def lockedMenu(self, menu):
        """
        :type menu: QtGui.QMenu
        :rtype: None
        """
        action = QtGui.QAction('Locked', menu)
        action.setEnabled(False)
        menu.addAction(action)

    def contextMenu(self, menu):
        """
        :type menu: QtGui.QMenu
        :rtype: None
        """
        folders = self.selectedFolders()
        if not folders:
            return
        separator = QtGui.QAction('Separator1', menu)
        separator.setSeparator(True)
        menu.addAction(separator)
        icon = studiolibrary.resource().icon('settings14')
        settingsMenu = QtGui.QMenu(self)
        settingsMenu.setIcon(icon)
        settingsMenu.setTitle('Settings')
        action = QtGui.QAction('Refresh', settingsMenu)
        action.triggered.connect(self.clearCache)
        settingsMenu.addAction(action)
        separator = QtGui.QAction('Separator2', settingsMenu)
        separator.setSeparator(True)
        settingsMenu.addAction(separator)
        action = QtGui.QAction('Show icon', settingsMenu)
        action.setCheckable(True)
        action.setChecked(self.isFolderIconVisible())
        action.triggered[bool].connect(self.setFolderIconVisible)
        settingsMenu.addAction(action)
        action = QtGui.QAction('Show bold', settingsMenu)
        action.setCheckable(True)
        action.setChecked(self.isFolderBold())
        action.triggered[bool].connect(self.setFolderBold)
        settingsMenu.addAction(action)
        separator = QtGui.QAction('Separator2', settingsMenu)
        separator.setSeparator(True)
        settingsMenu.addAction(separator)
        action = QtGui.QAction('Change icon', settingsMenu)
        action.triggered.connect(self.browseFolderIcon)
        settingsMenu.addAction(action)
        action = QtGui.QAction('Change color', settingsMenu)
        action.triggered.connect(self.browseFolderColor)
        settingsMenu.addAction(action)
        separator = QtGui.QAction('Separator3', settingsMenu)
        separator.setSeparator(True)
        settingsMenu.addAction(separator)
        action = QtGui.QAction('Reset settings', settingsMenu)
        action.triggered.connect(self.resetFolderSettings)
        settingsMenu.addAction(action)
        menu.addMenu(settingsMenu)

    def createFolder(self, parent = None):
        """
        :rtype: None
        """
        dialog = studiolibrary.NewFolderDialog(parent)
        dialog.exec_()
        if dialog.text():
            folders = self.selectedFolders()
            if len(folders) == 1:
                folder = folders[-1]
                path = folder.path() + '/' + dialog.text()
            else:
                path = self.rootPath() + '/' + dialog.text()
            folder = self.folderFromPath(path)
            folder.save()
            self.selectFolder(folder)

    def folderAt(self, pos):
        """
        :type pos: QtGui.QPoint
        :rtype: None or studiolibrary.Folder
        """
        index = self.indexAt(pos)
        if not index.isValid():
            return
        path = self.pathFromIndex(index)
        folder = self.folderFromPath(path)
        return folder

    def setFolderIconVisible(self, value):
        """
        :type value: Bool
        """
        for folder in self.selectedFolders():
            folder.setIconVisible(value)

    def isFolderIconVisible(self):
        """
        :rtype: bool
        """
        for folder in self.selectedFolders():
            if not folder.isIconVisible():
                return False

        return True

    def setFolderBold(self, value):
        """
        :type value: Bool
        """
        for folder in self.selectedFolders():
            folder.setBold(value)

    def isFolderBold(self):
        """
        :rtype: bool
        """
        for folder in self.selectedFolders():
            if not folder.isBold():
                return False

        return True

    def setFolderColor(self, color):
        """
        :type color:
        :return:
        """
        for folder in self.selectedFolders():
            folder.setColor(color)

    def resetFolderSettings(self):
        """
        :rtype:
        """
        for folder in self.selectedFolders():
            folder.reset()

    def browseFolderIcon(self):
        """
        :rtype: None
        """
        path, ext = QtGui.QFileDialog.getOpenFileName(self.parent(), 'Select an image', '', '*.png')
        path = str(path).replace('\\', '/')
        if path:
            for folder in self.selectedFolders():
                folder.setIconPath(path)

    def browseFolderColor(self):
        """
        :rtype: None
        """
        dialog = QtGui.QColorDialog(self.parent())
        dialog.currentColorChanged.connect(self.setFolderColor)
        dialog.open()
        if dialog.exec_():
            self.setFolderColor(dialog.selectedColor())


class FileSystemModel(QtGui.QFileSystemModel):

    def __init__(self, foldersWidget):
        """
        :type foldersWidget: FoldersWidget
        """
        QtGui.QFileSystemModel.__init__(self, foldersWidget)
        self._invalid = []
        self._foldersWidget = foldersWidget
        self.setFilter(QtCore.QDir.AllDirs)

    def foldersWidget(self):
        """
        :rtype: FoldersWidget
        """
        return self._foldersWidget

    def columnCount(self, *args):
        """
        :type args: list
        :rtype: int
        """
        return 1

    def setInvalid(self, invalid):
        """
        :type invalid: list or None
        """
        self._invalid = invalid or []

    def isPathValid(self, path):
        """
        :type path: str
        :rtype: bool
        """
        if os.path.isdir(path):
            path = path.lower()
            valid = [ item for item in self._invalid if path.endswith(item) ]
            if not valid:
                return True
        return False

    def hasChildren(self, index):
        """
        :type index: QtCore.QModelIndex
        :rtype: bool
        """
        path = str(self.filePath(index))
        if os.path.isdir(path):
            for name in os.listdir(path):
                if self.isPathValid(path + '/' + name):
                    return True

        return False

    def data(self, index, role):
        """
        :type index: QtCore.QModelIndex
        :type role:
        :rtype:
        """
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                dirname = str(self.filePath(index))
                folder = self.foldersWidget().folderFromPath(dirname)
                pixmap = QtGui.QIcon(folder.pixmap())
                if pixmap:
                    return QtGui.QIcon(folder.pixmap())
        if role == QtCore.Qt.FontRole:
            if index.column() == 0:
                dirname = str(self.filePath(index))
                folder = self.foldersWidget().folderFromPath(dirname)
                if folder.exists():
                    if folder.isBold():
                        font = QtGui.QFont()
                        font.setBold(True)
                        return font
        if role == QtCore.Qt.DisplayRole:
            text = QtGui.QFileSystemModel.data(self, index, role)
            return text


class SortFilterProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self, parent):
        """
        :type parent: QtGui.QWidget
        """
        self._parent = parent
        QtGui.QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        """
        :type sourceRow:
        :type sourceParent:
        :rtype: bool
        """
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        path = str(self.sourceModel().filePath(index))
        return self.sourceModel().isPathValid(path)
