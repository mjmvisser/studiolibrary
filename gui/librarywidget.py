#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\gui\librarywidget.py
import time
import logging
from functools import partial
from PySide import QtGui
from PySide import QtCore
import studioqt
import studiolibrary
__all__ = ['LibraryWidget']
logger = logging.getLogger(__name__)

class LibraryWidget(studiolibrary.MayaDockWidgetMixin, QtGui.QWidget):

    @staticmethod
    def generateUniqueObjectName(name):
        """
        :type name: str
        :rtype: str
        """
        names = [ w.objectName() for w in studiolibrary.Library.windows() ]
        return studiolibrary.generateUniqueName(name, names)

    def setUniqueObjectName(self, name):
        """
        :type name: str
        :rtype: None
        """
        uniqueName = self.generateUniqueObjectName(name)
        self.setObjectName(uniqueName)

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        QtGui.QWidget.__init__(self, None)
        studiolibrary.MayaDockWidgetMixin.__init__(self, None)
        studioqt.loadUi(self)
        logger.info("Loading library window '{0}'".format(library.name()))
        self.setUniqueObjectName('studiolibrary')
        studiolibrary.analytics().logScreen('MainWindow')
        self._pSize = None
        self._pShow = None
        self._library = None
        self._isDebug = False
        self._isLocked = False
        self._isLoaded = False
        self._showFolders = False
        self._updateThread = None
        self._showLabelsAction = True
        self._saveSettingsOnClose = True
        self.ui.dialogWidget = None
        self.ui.createWidget = None
        self.ui.previewWidget = None
        self._isFoldersWidgetVisible = True
        self._isPreviewWidgetVisible = True
        self._isMenuBarWidgetVisible = True
        self._isStatusBarWidgetVisible = True
        self.ui.previewFrame = QtGui.QFrame(self)
        self.ui.statusWidget = studiolibrary.StatusWidget(self)
        self.ui.recordsWidget = studioqt.ListWidget(self)
        self.ui.foldersWidget = studiolibrary.FoldersWidget(self)
        self.setMinimumWidth(5)
        self.setMinimumHeight(5)
        pixmap = studioqt.pixmap('settings', color=self.iconColor())
        self.ui.settingsButton.setIconSize(QtCore.QSize(26, 26))
        self.ui.settingsButton.setIcon(pixmap)
        pixmap = studioqt.pixmap('add', color=self.iconColor())
        self.ui.createButton.setIconSize(QtCore.QSize(32, 32))
        self.ui.createButton.setIcon(pixmap)
        self.ui.updateButton.hide()
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.ui.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
        self.ui.splitter.setHandleWidth(1)
        self.ui.splitter.setChildrenCollapsible(False)
        self.ui.viewLayout.insertWidget(1, self.ui.splitter)
        self.ui.splitter.insertWidget(0, self.ui.foldersWidget)
        self.ui.splitter.insertWidget(1, self.ui.recordsWidget)
        self.ui.splitter.setStretchFactor(0, False)
        self.ui.splitter.setStretchFactor(2, False)
        vbox = QtGui.QVBoxLayout()
        self.ui.previewFrame.setLayout(vbox)
        self.ui.previewFrame.layout().setSpacing(0)
        self.ui.previewFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.ui.previewFrame.setMinimumWidth(5)
        self.ui.viewLayout.insertWidget(2, self.ui.previewFrame)
        self.ui.splitter.insertWidget(2, self.ui.previewFrame)
        self.ui.statusLayout.addWidget(self.ui.statusWidget)
        self.ui.updateButton.clicked.connect(self.help)
        self.ui.createButton.clicked.connect(self.showNewMenu)
        self.ui.settingsButton.clicked.connect(self.showSettingsMenu)
        self.dockingChanged.connect(self.updateWindowTitle)
        folderWidget = self.foldersWidget()
        folderWidget.onDropped.connect(self.onRecordDropped)
        folderWidget.onSelectionChanged.connect(self.folderSelectionChanged)
        folderWidget.onShowContextMenu.connect(self.onShowFolderContextMenu)
        recordsWidget = self.recordsWidget()
        recordsWidget.itemDropped.connect(self.onRecordDropped)
        recordsWidget.itemOrderChanged.connect(self.onRecordOrderChanged)
        recordsWidget.onShowContextMenu.connect(self.onShowRecordContextMenu)
        recordsWidget.onSelectionChanged.connect(self.onRecordSelectionChanged)
        studiolibrary.Record.onSaved.connect(self.onRecordSaved)
        studiolibrary.SettingsDialog.onColorChanged.connect(self.onSettingsColorChanged)
        studiolibrary.SettingsDialog.onBackgroundColorChanged.connect(self.onSettingsBackgroundColorChanged)
        self.checkForUpdates()
        self.setLibrary(library)

    def iconColor(self):
        """
        :rtype: studioqt.Color
        """
        return studioqt.Color(245, 245, 245)

    def newMenu(self):
        """
        Return the new menu for adding new folders and records.
        
        :rtype: QtGui.QMenu
        """
        color = self.iconColor()
        icon = studiolibrary.resource().icon('add', color=color)
        menu = QtGui.QMenu(self)
        menu.setIcon(icon)
        menu.setTitle('New')
        icon = studiolibrary.resource().icon('folder', color=color)
        action = QtGui.QAction(icon, 'Folder', menu)
        action.triggered.connect(self.showCreateFolderDialog)
        menu.addAction(action)
        icon = studiolibrary.resource().icon('add_library', color=color)
        action = QtGui.QAction(icon, 'Library', menu)
        action.triggered.connect(self.showNewLibraryDialog)
        menu.addAction(action)
        separator = QtGui.QAction('', menu)
        separator.setSeparator(True)
        menu.addAction(separator)
        for name in self.library().plugins():
            plugin = self.plugin(name)
            action = plugin.newAction(parent=menu)
            if action:
                callback = partial(self.showCreateWidget, plugin=plugin)
                action.triggered.connect(callback)
                menu.addAction(action)

        return menu

    def recordEditMenu(self):
        """
        Return the edit menu for deleting, renaming records.
        
        :rtype: QtGui.QMenu
        """
        menu = QtGui.QMenu(self)
        menu.setTitle('Edit')
        action = QtGui.QAction('Delete', menu)
        action.triggered.connect(self.deleteSelectedRecords)
        menu.addAction(action)
        action = QtGui.QAction('Rename', menu)
        action.triggered.connect(self.renameSelectedRecord)
        menu.addAction(action)
        action = QtGui.QAction('Show in folder', menu)
        action.triggered.connect(self.openSelectedRecords)
        menu.addAction(action)
        return menu

    def folderEditMenu(self):
        """
        Return the edit menu for deleting, renaming folders.
        
        :rtype: QtGui.QMenu
        """
        menu = QtGui.QMenu(self)
        menu.setTitle('Edit')
        action = QtGui.QAction('Delete', menu)
        action.triggered.connect(self.deleteSelectedFolders)
        menu.addAction(action)
        action = QtGui.QAction('Rename', menu)
        action.triggered.connect(self.renameSelectedFolder)
        menu.addAction(action)
        action = QtGui.QAction('Show in folder', menu)
        action.triggered.connect(self.openSelectedFolders)
        menu.addAction(action)
        return menu

    def settingsMenu(self):
        """
        Return the settings menu for changing the library widget.
        
        :rtype: QtGui.QMenu
        """
        icon = studioqt.icon('settings', color=self.iconColor())
        menu = QtGui.QMenu('', self)
        menu.setTitle('Settings')
        menu.setIcon(icon)
        libraries = studiolibrary.LibrariesMenu(menu)
        menu.addMenu(libraries)
        menu.addSeparator()
        action = QtGui.QAction('Settings', menu)
        action.triggered[bool].connect(self.showSettingsDialog)
        menu.addAction(action)
        separator = QtGui.QAction('', menu)
        separator.setSeparator(True)
        menu.addAction(separator)
        action = QtGui.QAction('Show menu', menu)
        action.setCheckable(True)
        action.setChecked(self.isMenuBarWidgetVisible())
        action.triggered[bool].connect(self.setMenuBarWidgetVisible)
        menu.addAction(action)
        action = QtGui.QAction('Show folders', menu)
        action.setCheckable(True)
        action.setChecked(self.isFoldersWidgetVisible())
        action.triggered[bool].connect(self.setFoldersWidgetVisible)
        menu.addAction(action)
        action = QtGui.QAction('Show preview', menu)
        action.setCheckable(True)
        action.setChecked(self.isPreviewWidgetVisible())
        action.triggered[bool].connect(self.setPreviewWidgetVisible)
        menu.addAction(action)
        action = QtGui.QAction('Show status', menu)
        action.setCheckable(True)
        action.setChecked(self.isStatusBarWidgetVisible())
        action.triggered[bool].connect(self.setStatusBarWidgetVisible)
        menu.addAction(action)
        menu.addSeparator()
        viewMenu = self.recordsWidget().settingsMenu(parent=menu)
        menu.addMenu(viewMenu)
        if studiolibrary.isMaya():
            menu.addSeparator()
            dockMenu = self.dockMenu()
            menu.addMenu(dockMenu)
        menu.addSeparator()
        action = QtGui.QAction('Debug mode', menu)
        action.setCheckable(True)
        action.setChecked(self.isDebug())
        action.triggered[bool].connect(self.setDebugMode)
        menu.addAction(action)
        action = QtGui.QAction('Help', menu)
        action.triggered.connect(self.help)
        menu.addAction(action)
        return menu

    def showNewMenu(self):
        """
        :rtype: QtGui.QAction
        """
        if not self.isLocked():
            menu = self.newMenu()
            point = self.ui.createButton.rect().bottomLeft()
            point = self.ui.createButton.mapToGlobal(point)
            return menu.exec_(point)

    def showSettingsMenu(self):
        """
        :rtype: QtGui.QAction
        """
        menu = self.settingsMenu()
        point = self.ui.settingsButton.rect().bottomRight()
        point = self.ui.settingsButton.mapToGlobal(point)
        menu.show()
        x = point.x() - menu.width()
        point.setX(x)
        return menu.exec_(point)

    def onShowFolderContextMenu(self, menu):
        """
        :type menu: QtGui.QMenu
        :rtype: None
        """
        folders = self.selectedFolders()
        if self.isLocked():
            return
        menu.addMenu(self.newMenu())
        if len(folders) == 1:
            menu.addMenu(self.folderEditMenu())
        if not folders:
            menu.addSeparator()
            menu.addMenu(self.settingsMenu())

    def onShowRecordContextMenu(self):
        """
        :rtype: None
        """
        records = self.recordsWidget().selectedItems()
        self.showRecordContextMenu(records=records)

    def showRecordContextMenu(self, records):
        """
        :type records: list[studiolibrary.Record]
        :rtype QtGui.QAction
        """
        menu = self.recordContextMenu(records)
        point = QtGui.QCursor.pos()
        point.setX(point.x() + 3)
        point.setY(point.y() + 3)
        action = menu.exec_(point)
        menu.close()
        return action

    def recordContextMenu(self, records):
        """
        :type records: list[studiolibrary.Record]
        :rtype: studiolibrary.ContextMenu
        """
        menu = studiolibrary.ContextMenu(self)
        for plugin in self.plugins().values():
            plugin.recordContextMenu(menu, records)

        if not self.isLocked():
            menu.addMenu(self.newMenu())
            menu.addMenu(self.recordEditMenu())
        menu.addSeparator()
        menu.addMenu(self.settingsMenu())
        return menu

    def folderSelectionChanged(self, selectedFolders, deselectedFolders):
        """
        :type selectedFolders: list[studiolibrary.Folder]
        :type deselectedFolders: list[studiolibrary.Folder]
        :rtype: None
        """
        for plugin in self.plugins().values():
            plugin.folderSelectionChanged(selectedFolders, deselectedFolders)

        self.reloadRecords()

    def onRecordOrderChanged(self):
        """
        :rtype: None
        """
        folders = self.selectedFolders()
        if len(folders) == 1:
            folder, = folders
            order = []
            for item in self.recordsWidget().items():
                order.append(item.text())

            folder.setOrder(order)

    def recordsFromUrls(self, urls):
        """
        :type urls: list[QtGui.QUrl]
        :rtype: list[studiolibrary.Records]
        """
        records = []
        for url in urls:
            path = url.path()
            record = self.library().recordFromPath(path)
            records.append(record)

        return records

    def onRecordDropped(self, event):
        """
        :type event: list[studiolibrary.Record]
        :rtype: None
        """
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            folder = self.selectedFolder()
            row = self.recordsWidget().rowAt(event.pos())
            records = self.recordsFromUrls(mimeData.urls())
        self.moveRecordsToFolder(records, folder, row=row)

    def moveRecordsToFolder(self, records, folder, row = -1):
        """
        :type records: list[studiolibrary.Record]
        :type folder: studiolibrary.Folder
        :rtype: None
        """
        movedRecords = []
        try:
            for record in records:
                item = self.recordsWidget().itemFromUrl(record.url())
                if not item:
                    path = folder.path() + '/' + record.name()
                    record.rename(path)
                    movedRecords.append(record)

        except Exception as msg:
            self.setError(msg)
            raise
        finally:
            if movedRecords:
                self.recordsWidget().moveItems(row, movedRecords)
            self.selectRecords(movedRecords)

    def onRecordSelectionChanged(self):
        """
        """
        record = self.recordsWidget().selectedItem()
        self.setPreviewWidgetFromRecord(record)

    def onRecordSaved(self, record):
        """
        :type record: studiolibrary.Record
        :rtype: None
        """
        folder = self.selectedFolder()
        if folder and folder.path() == record.dirname():
            path = record.path()
            self.reloadRecords()
            self.selectRecordsFromPaths([path])

    def onSettingsColorChanged(self, settingsWindow):
        """
        :type settingsWindow: studiolibrary.SettingsWindow
        :rtype: None
        """
        if self.library() == settingsWindow.library():
            self.library().setAccentColor(settingsWindow.color())
            self.reloadStyleSheet()

    def onSettingsBackgroundColorChanged(self, settingsWindow):
        """
        :type settingsWindow: studiolibrary.SettingsWindow
        :rtype: None
        """
        if self.library() == settingsWindow.library():
            self.library().setBackgroundColor(settingsWindow.backgroundColor())
            self.reloadStyleSheet()

    def showNewLibraryDialog(self):
        """
        :rtype: None
        """
        studiolibrary.Library.showNewLibraryDialog()

    def recordsWidget(self):
        """
        :rtype: studiolibrary.RecordsWidget
        """
        return self.ui.recordsWidget

    def foldersWidget(self):
        """
        :rtype: studiolibrary.FoldersWidget
        """
        return self.ui.foldersWidget

    def previewWidget(self):
        """
        :rtype: studiolibrary.QWidget
        """
        return self.ui.previewWidget

    def isListView(self):
        """
        :type: bool
        """
        return self.ui.recordsWidget.viewMode() == QtGui.QListView.ListMode

    def isIconView(self):
        """
        :type: bool
        """
        return self.ui.recordsWidget.viewMode() == QtGui.QListView.IconMode

    def checkForUpdates(self):
        """
        :rtype: None
        """
        if studiolibrary.CHECK_FOR_UPDATES_ENABLED:
            if not self._updateThread:
                self._updateThread = studiolibrary.CheckForUpdatesThread(self)
                self.connect(self._updateThread, QtCore.SIGNAL('updateAvailable()'), self.setUpdateAvailable)
            self._updateThread.start()
        else:
            logger.debug('Check for updates has been disabled!')

    def setLibrary(self, library):
        """
        :type library: studiolibrary.Library
        """
        self._library = library
        self.reloadLibrary()

    def reloadLibrary(self):
        """
        :rtype: None
        """
        self.clearRecords()
        self.clearPreviewWidget()
        self.loadPlugins()
        self.setRootPath(self.library().path())
        self.updateWindowTitle()

    def setRootPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        invalid = ['.', '.studiolibrary']
        for name, plugin in self.plugins().items():
            invalid.append(plugin.extension())

        self.ui.foldersWidget.clearSelection()
        self.ui.foldersWidget.setRootPath(path, invalid=invalid)

    def library(self):
        """
        :rtype: studiolibrary.Library
        """
        return self._library

    def showSettingsDialog(self):
        """
        """
        library = self.library()
        name = library.name()
        location = library.path()
        result = library.execSettingsDialog()
        if result == QtGui.QDialog.Accepted:
            self.saveSettings()
            if location != library.path():
                self.reloadLibrary()
            if name != library.name():
                self.updateWindowTitle()
        self.reloadStyleSheet()

    def isPreviewWidgetVisible(self):
        """
        :rtype: bool
        """
        return self._isPreviewWidgetVisible

    def isFoldersWidgetVisible(self):
        """
        :rtype: bool
        """
        return self._isFoldersWidgetVisible

    def isStatusBarWidgetVisible(self):
        """
        :rtype: bool
        """
        return self._isStatusBarWidgetVisible

    def isMenuBarWidgetVisible(self):
        """
        :rtype: bool
        """
        return self._isMenuBarWidgetVisible

    def setPreviewWidgetVisible(self, value):
        """
        :type value: bool
        """
        value = bool(value)
        self._isPreviewWidgetVisible = value
        if value:
            self.ui.previewFrame.show()
        else:
            self.ui.previewFrame.hide()

    def setFoldersWidgetVisible(self, value):
        """
        :type value: bool
        """
        value = bool(value)
        self._isFoldersWidgetVisible = value
        if value:
            self.ui.foldersWidget.show()
        else:
            self.ui.foldersWidget.hide()

    def setMenuBarWidgetVisible(self, value):
        """
        :type value: bool
        """
        value = bool(value)
        self._isMenuBarWidgetVisible = value
        if value:
            self.ui.menuFrame.show()
        else:
            self.ui.menuFrame.hide()

    def setStatusBarWidgetVisible(self, value):
        """
        :type value: bool
        """
        value = bool(value)
        self._isStatusBarWidgetVisible = value
        if value:
            self.ui.statusWidget.show()
        else:
            self.ui.statusWidget.hide()

    def showCreateWidget(self, plugin):
        """
        Show the record create widget for a given plugin.
        
        :type plugin: studiolibrary.Plugin
        :rtype: None
        """
        widget = plugin.createWidget(parent=self.ui.previewFrame)
        self.setCreateWidget(widget)

    def clearPreviewWidget(self):
        """
        Set the default preview widget.
        """
        widget = studiolibrary.PreviewWidget(None)
        self.setPreviewWidget(widget)

    def setCreateWidget(self, widget):
        """
        :type widget: QtGui.QWidget
        :rtype: None
        """
        self.setPreviewWidgetVisible(True)
        self.ui.recordsWidget.clearSelection()
        self.setPreviewWidget(widget)

    def setPreviewWidgetFromRecord(self, record):
        """
        :type record: studiolibrary.Record
        :rtype: None
        """
        if record:
            plugin = record.plugin()
            try:
                previewWidget = plugin.previewWidget(None, record)
                self.setPreviewWidget(previewWidget)
            except Exception as msg:
                self.setError(msg)
                raise

        else:
            self.clearPreviewWidget()

    def setPreviewWidget(self, widget):
        """
        :type widget: QtGui.QWidget
        :rtype: None
        """
        if self.ui.previewWidget == widget:
            msg = 'Preview widget already contains widget "{0}"'
            msg.format(widget)
            logger.debug(msg)
        else:
            self.closePreviewWidget()
            self.ui.previewWidget = widget
            if self.ui.previewWidget:
                self.ui.previewFrame.layout().addWidget(self.ui.previewWidget)
                self.ui.previewWidget.show()

    def closePreviewWidget(self):
        """
        Close and delete the preview widget.
        """
        if self.ui.previewWidget:
            self.ui.previewWidget.close()
        for i in range(self.ui.previewFrame.layout().count()):
            widget2 = self.ui.previewFrame.layout().itemAt(i)
            if widget2:
                widget2 = widget2.widget()
                self.ui.previewFrame.layout().removeWidget(widget2)
                widget2.setParent(self)
                widget2.hide()
                widget2.close()
                widget2.destroy()
                del widget2

    def reloadStyleSheet(self):
        """
        :rtype: None
        """
        styleSheet = self.library().styleSheet()
        theme = self.library().theme()
        color = studioqt.Color.fromString(theme['RECORD_TEXT_COLOR'])
        self.recordsWidget().setTextColor(color)
        color = studioqt.Color.fromString(theme['RECORD_TEXT_SELECTED_COLOR'])
        self.recordsWidget().setTextSelectedColor(color)
        color = studioqt.Color.fromString(theme['RECORD_BACKGROUND_COLOR'])
        self.recordsWidget().setBackgroundColor(color)
        color = studioqt.Color.fromString(theme['RECORD_BACKGROUND_SELECTED_COLOR'])
        self.recordsWidget().setBackgroundSelectedColor(color)
        self.setStyleSheet(styleSheet)

    def centerWindow(self):
        """
        :rtype: None
        """
        geometry = self.frameGeometry()
        pos = QtGui.QApplication.desktop().cursor().pos()
        screen = QtGui.QApplication.desktop().screenNumber(pos)
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        geometry.moveCenter(centerPoint)
        self.move(geometry.topLeft())

    def settings(self):
        """
        :rtype: studiolibrary.MetaFile
        """
        settings = self.library().settings()
        geometry = (self.parentX().geometry().x(),
         self.parentX().geometry().y(),
         self.parentX().geometry().width(),
         self.parentX().geometry().height())
        settings.set('geometry', geometry)
        settings.set('sizes', self.ui.splitter.sizes())
        settings.set('dockSettings', self.dockSettings())
        settings.set('foldersSettings', self.ui.foldersWidget.currentState())
        settings.set('recordsSettings', self.recordsWidget().settings())
        settings.set('isFoldersWidgetVisible', self.isFoldersWidgetVisible())
        settings.set('isPreviewWidgetVisible', self.isPreviewWidgetVisible())
        settings.set('isMenuBarWidgetVisible', self.isMenuBarWidgetVisible())
        settings.set('isStatusBarWidgetVisible', self.isStatusBarWidgetVisible())
        return settings

    def setSettings(self, settings):
        """
        :type settings: studiolibrary.MetaFile
        """
        sizes = settings.get('sizes', [120, 280, 160])
        if len(sizes) == 3:
            self.setSizes(sizes)
        x, y, width, height = settings.get('geometry', [200,
         200,
         670,
         550])
        self.parentX().setGeometry(x, y, width, height)
        if x < 0 or y < 0:
            self.parentX().move(200, 200)
        dockSettings = settings.get('dockSettings', {})
        self.setDockSettings(dockSettings)
        foldersSettings = settings.get('foldersSettings', {})
        self.ui.foldersWidget.restoreState(foldersSettings)
        recordsSettings = settings.get('recordsSettings', {})
        self.recordsWidget().setSettings(recordsSettings)
        value = settings.get('isFoldersWidgetVisible', True)
        self.setFoldersWidgetVisible(value)
        value = settings.get('isMenuBarWidgetVisible', True)
        self.setMenuBarWidgetVisible(value)
        value = settings.get('isPreviewWidgetVisible', True)
        self.setPreviewWidgetVisible(value)
        value = settings.get('isStatusBarWidgetVisible', True)
        self.setStatusBarWidgetVisible(value)

    def loadSettings(self):
        """
        :rtype: None
        """
        try:
            settings = self.library().readSettings()
            self.setSettings(settings.data())
        finally:
            self.reloadRecords()

        self._isLoaded = True

    def isLoaded(self):
        """
        :rtype: bool
        """
        return self._isLoaded

    def saveSettings(self):
        """
        :rtype: None
        """
        settings = self.settings()
        settings.save()

    def setSizes(self, sizes):
        """
        :type sizes: (int, int, int)
        :rtype: None
        """
        fSize, cSize, pSize = sizes
        if pSize == 0:
            pSize = 200
        if fSize == 0:
            fSize = 120
        self.ui.splitter.setSizes([fSize, cSize, pSize])
        self.ui.splitter.setStretchFactor(1, 1)

    def event(self, event):
        """
        :type event: QtGui.QEvent
        :rtype: None
        """
        if isinstance(event, QtGui.QStatusTipEvent):
            self.ui.statusWidget.setInfo(event.tip())
        return QtGui.QWidget.event(self, event)

    def keyPressEvent(self, event):
        """
        :type event: QtGui.QKeyEvent
        :rtype: None
        """
        if event.key() == QtCore.Qt.Key_F5:
            self.reloadFolders()
        QtGui.QWidget.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        """
        :type event: QtGui.QKeyEvent
        :rtype: None
        """
        for record in self.selectedRecords():
            record.keyReleaseEvent(event)

        QtGui.QWidget.keyReleaseEvent(self, event)

    def closeEvent(self, event):
        """
        :type event: QtGui.QEvent
        :rtype: None
        """
        self.saveSettings()
        QtGui.QWidget.closeEvent(self, event)

    def showEvent(self, event):
        """
        :type event: QtGui.QEvent
        :rtype: None
        """
        QtGui.QWidget.showEvent(self, event)
        try:
            if not self.isLoaded():
                self.loadSettings()
        except Exception as msg:
            raise
        finally:
            self.reloadStyleSheet()

    def setUpdateAvailable(self):
        self.ui.updateButton.show()

    def warningDialog(self, message, title = 'Warning'):
        return QtGui.QMessageBox.warning(self, title, str(message))

    def criticalDialog(self, message, title = 'Error'):
        return QtGui.QMessageBox.critical(self, title, str(message))

    def informationDialog(self, message, title = 'Information'):
        return QtGui.QMessageBox.information(self, title, str(message))

    def questionDialog(self, message, title = 'Question'):
        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel
        return QtGui.QMessageBox.question(self, title, str(message), buttons)

    def setError(self, text, msec = 6000):
        text = str(text)
        self.ui.statusWidget.setError(text, msec=msec)

    def setWarning(self, text, msec = 6000):
        text = str(text)
        self.ui.statusWidget.setWarning(text, msec=msec)
        if self.isShowStatusDialog():
            self.warningDialog(text)
        else:
            self.showStatus(True)

    def setInfo(self, text, msec = 6000):
        self.ui.statusWidget.setInfo(text, msec=msec)

    def updateWindowTitle(self):
        title = 'Studio Library - '
        if self.isDocked():
            title += self.library().name()
        else:
            title += studiolibrary.__version__ + ' - ' + self.library().name()
        if self.isLocked():
            title += ' (Locked)'
        self.setWindowTitle(title)

    def showMessage(self, text, repaint = True):
        self.ui.recordsWidget.showMessage(text, repaint=repaint)

    def setLoadedMessage(self, elapsedTime):
        """
        :type elapsedTime: time.time
        """
        recordCount = len(self.ui.recordsWidget.items())
        hiddenCount = self.ui.recordsWidget.itemsHiddenCount()
        plural = ''
        if recordCount != 1:
            plural = 's'
        hiddenText = ''
        if hiddenCount > 0:
            hiddenText = '%d items hidden.' % hiddenCount
        self.ui.statusWidget.setInfo('Loaded %s item%s in %0.3f seconds. %s' % (recordCount,
         plural,
         elapsedTime,
         hiddenText))

    def setLocked(self, value):
        self._isLocked = value
        self.foldersWidget().setLocked(value)
        self.recordsWidget().setLocked(value)
        self.updateNewButton()
        self.updateWindowTitle()

    def isLocked(self):
        """
        :rtype: bool
        """
        return self._isLocked

    def updateNewButton(self):
        if self.isLocked():
            pixmap = studioqt.pixmap('lock', color=self.iconColor())
            self.ui.createButton.setEnabled(True)
            self.ui.createButton.setIcon(pixmap)
        else:
            pixmap = studioqt.pixmap('add', color=self.iconColor())
            self.ui.createButton.setEnabled(True)
            self.ui.createButton.setIcon(pixmap)
            self.ui.createButton.show()

    def kwargs(self):
        """
        :rtype: dict
        """
        return self.library().kwargs()

    def window(self):
        """
        :rtype: QtGui.QWidget
        """
        return self

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
        try:
            self._renameSelectedRecord()
        except Exception as msg:
            self.criticalDialog(msg)
            raise

    def _renameSelectedRecord(self):
        """
        :rtype: None
        """
        record = self.recordsWidget().selectedItem()
        if not record:
            raise Exception('Please select a record')
        result = record.showRenameDialog(parent=self)
        if result:
            self.reloadRecords()
            self.selectRecords([record])

    def renameSelectedFolder(self):
        try:
            self.ui.foldersWidget.showRenameDialog(parent=self)
        except Exception as msg:
            self.criticalDialog(msg)
            raise

    def selectRecordsFromPaths(self, paths):
        records = self.recordsWidget().itemsFromPaths(paths)
        self.selectRecords(records)

    def selectRecords(self, records):
        self.recordsWidget().selectItems(records)
        self.onRecordSelectionChanged()

    def selectFolders(self, folders):
        self.ui.foldersWidget.selectFolders(folders)

    def clearSelection(self):
        self.ui.foldersWidget.clearSelection()

    def selectedRecords(self):
        return self.ui.recordsWidget.selectedItems()

    def selectedFolder(self):
        """
        :rtype: studiolibrary.Folder
        """
        folders = self.selectedFolders()
        if folders:
            return folders[0]

    def selectedFolders(self):
        return self.ui.foldersWidget.selectedFolders()

    def plugins(self):
        """
        :rtype: list[studiolibrary.Plugin]
        """
        return self.library().loadedPlugins()

    def plugin(self, name):
        """
        :type name: str
        :rtype: studiolibrary.Plugin
        """
        return self.library().loadedPlugins().get(name, None)

    def loadPlugin(self, name):
        self.library().loadPlugin(name)

    def loadPlugins(self):
        self.library().loadPlugins()

    def clearRecords(self):
        self.recordsWidget().clear()

    def listRecords(self, sort = studiolibrary.SortOption.Ordered):
        """
        :rtype: list[studiolibrary.Record]
        """
        results = []
        folders = self.foldersWidget().selectedFolders()
        for folder in folders:
            path = folder.path()
            records = self.library().listRecords(path)
            if records:
                records = self.library().sortRecords(records, order=folder.order(), sort=studiolibrary.SortOption.Ordered)
                results.extend(records)

        return results

    def reloadRecords(self):
        """
        :rtype: None
        """
        logger.debug("Loading records for library '%s'" % self.library().name())
        elapsedTime = time.time()
        selectedRecords = self.selectedRecords()
        self.recordsWidget().clear()
        records = self.listRecords()
        self.recordsWidget().addItems(records)
        if selectedRecords:
            self.selectRecords(selectedRecords)
        if self.selectedRecords() != selectedRecords:
            self.onRecordSelectionChanged()
        self.recordsWidget().refreshFilter()
        elapsedTime = time.time() - elapsedTime
        self.setLoadedMessage(elapsedTime)
        logger.debug('Loaded records')

    @staticmethod
    def help():
        """
        :rtype: None
        """
        studiolibrary.package().openHelp()

    def deleteSelectedRecords(self):
        """
        :rtype: None
        """
        items = self.recordsWidget().selectedItems()
        if items:
            msg = 'Are you sure you want to delete the selected record/s {0}'
            msg = msg.format(str([ r.name() for r in items ]))
            result = self.window().questionDialog(msg)
            if result == QtGui.QMessageBox.Yes:
                try:
                    for record in items:
                        record.delete()

                except Exception as msg:
                    self.setError(msg)
                finally:
                    self.reloadRecords()

    def deleteSelectedFolders(self):
        """
        :rtype: None
        """
        self.foldersWidget().showDeleteDialog()

    def setDebugMode(self, value):
        """
        :type value: bool
        """
        self._isDebug = value
        if value:
            self.library().setLoggerLevel(logging.DEBUG)
        else:
            self.library().setLoggerLevel(logging.INFO)

    def isDebug(self):
        """
        :rtype: bool
        """
        return self._isDebug

    def showCreateFolderDialog(self):
        """
        :rtype: None
        """
        try:
            self.ui.foldersWidget.createFolder(parent=self)
        except Exception as msg:
            self.setError(msg)
            raise
