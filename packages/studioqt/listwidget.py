#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/studioqt\listwidget.py
import logging
from PySide import QtGui
from PySide import QtCore
import studioqt
__all__ = ['ItemWidget']
logger = logging.getLogger(__name__)

class ListWidget(QtGui.QListWidget):
    DEFAULT_SPACING = 2
    DEFAULT_PADDING = 6
    DEFAULT_VIEW_SIZE = 90
    DEFAULT_BATCH_SIZE = 500
    DEFAULT_LABEL_HEIGHT = 15
    DEFAULT_DRAG_THRESHOLD = 10
    DEFAULT_WHEEL_SCROLL_STEP = 2
    DEFAULT_ANNOTATION_WAIT = 1500
    DEFAULT_MINIMUM_LIST_SIZE = 20
    DEFAULT_MINIMUM_ICON_SIZE = 40
    DEFAULT_MESSAGE_CORNER_SIZE = 4
    DEFAULT_MESSAGE_TEXT_COLOR = QtGui.QColor(255, 255, 255)
    DEFAULT_MESSAGE_BACKGROUND_COLOR = QtGui.QColor(0, 0, 0)
    itemDropped = QtCore.Signal(object)
    itemDropping = QtCore.Signal(object)
    itemOrderChanged = QtCore.Signal()
    viewSizeChanged = QtCore.Signal(object)
    zoomAmountChanged = QtCore.Signal(object)
    onShowAnnotation = QtCore.Signal()
    onShowContextMenu = QtCore.Signal()
    onSelectionChanged = QtCore.Signal()

    def __init__(self, parent = None):
        """
        :type parent: QtGui.QWidget
        """
        QtGui.QListWidget.__init__(self, parent)
        self._dpi = 1
        self._drag = None
        self._filter = ''
        self._zoomIndex = None
        self._buttonDown = None
        self._contextMenu = None
        self._dragAccepted = True
        self._currentItem = None
        self._previousItem = None
        self._signalsEnabled = True
        self._dragStartPos = None
        self._dragStartIndex = False
        self._isLocked = False
        self._isDropEnabled = True
        self._isItemTextVisible = True
        self._viewSize = QtCore.QSize(self.DEFAULT_VIEW_SIZE, self.DEFAULT_VIEW_SIZE)
        self._padding = self.DEFAULT_PADDING
        self._minimumListSize = self.DEFAULT_MINIMUM_LIST_SIZE
        self._minimumIconSize = self.DEFAULT_MINIMUM_ICON_SIZE
        self._messageText = ''
        self._messageAlpha = 255
        self._messageColor = self.DEFAULT_MESSAGE_TEXT_COLOR
        self._messageCornerSize = self.DEFAULT_MESSAGE_CORNER_SIZE
        self._messageBackgroundColor = self.DEFAULT_MESSAGE_BACKGROUND_COLOR
        self._textColor = QtGui.QColor(255, 255, 255)
        self._textSelectedColor = QtGui.QColor(255, 255, 255)
        self._backgroundColor = QtGui.QColor(255, 255, 255, 30)
        self._backgroundHoverColor = QtGui.QColor(255, 255, 255, 35)
        self._backgroundSelectedColor = QtGui.QColor(30, 150, 255)
        self._policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.setSizePolicy(self._policy)
        self.setSelectionRectVisible(True)
        self.setSelectionMode(QtGui.QListWidget.ExtendedSelection)
        self.setSpacing(self.DEFAULT_SPACING)
        self.setBatchSize(self.DEFAULT_BATCH_SIZE)
        self.setMinimumWidth(5)
        self.setMouseTracking(True)
        self.setViewMode(QtGui.QListWidget.IconMode)
        self.setResizeMode(QtGui.QListWidget.Adjust)
        self.setLayoutMode(QtGui.QListWidget.Batched)
        self.updateViewSize()
        delegate = studioqt.ListWidgetItemDelegate(self)
        self.setItemDelegate(delegate)
        self._messageDisplayTimer = QtCore.QTimer(self)
        self._messageDisplayTimer.timeout.connect(self.fadeOut)
        self._messageFadeOutTimer = QtCore.QTimer(self)
        self._messageFadeOutTimer.timeout.connect(self._fadeOut)
        self.itemClicked.connect(self._itemClicked)
        self.itemDoubleClicked.connect(self._itemDoubleClicked)
        self._showAnnotationTimer = QtCore.QTimer(self)
        self._showAnnotationTimer.setSingleShot(True)
        self._showAnnotationTimer.timeout.connect(self._showAnnotation)
        self._currentAnnotationItem = None

    def dpi(self):
        return self._dpi

    def setDpi(self, dpi):
        self._dpi = dpi

    def showAnnotation(self, item, wait = None):
        self.hideAnnotation()
        self._currentAnnotationItem = item
        if wait:
            self._showAnnotationTimer.start(wait)
        else:
            self.onShowAnnotation()

    def _showAnnotation(self):
        if self._currentAnnotationItem:
            self._currentAnnotationItem.showInfoWidget()
            self.onShowAnnotation.emit()

    def hideAnnotation(self):
        self._showAnnotationTimer.stop()
        if self._currentAnnotationItem:
            self._currentAnnotationItem.hideInfoWidget()
            self._currentAnnotationItem = None

    def _itemClicked(self, item):
        logger.debug('Record clicked: "%s"' % item.text())
        item.clicked()

    def _itemDoubleClicked(self, item):
        logger.debug('Record double clicked: "%s"' % item.text())
        item.doubleClicked()

    def refresh(self):
        """
        :rtype: None
        """
        self.setViewSize(self.viewSize())
        self.repaint()

    def isDragEnabled(self):
        """
        :rtype: bool
        """
        if self.isLocked():
            return False
        else:
            return self._isDropEnabled

    def itemsFromUrls(self, urls):
        """
        :type urls: list[QtCore.QUrl]
        :rtype: list[studioqt.ListWidgetItem]
        """
        items = []
        for url in urls:
            item = self.itemFromUrl(url)
            if item:
                items.append(item)

        return items

    def itemFromUrl(self, url):
        """
        :type url: QtCore.QUrl
        :rtype: studioqt.ListWidgetItem
        """
        return self.itemFromPath(url.path())

    def itemsFromPaths(self, paths):
        """
        :type paths: list[str]
        :rtype: list[studioqt.ListWidgetItem]
        """
        items = []
        for path in paths:
            item = self.itemFromPath(path)
            if item:
                items.append(item)

        return items

    def itemFromPath(self, path):
        """
        :type path: str
        :rtype: studioqt.ListWidgetItem
        """
        for item in self.items():
            path_ = item.url().path()
            if path_ and path_ == path:
                return item

    def setPadding(self, value):
        """
        :type value: int
        """
        if value % 2 == 0:
            self._padding = value
        else:
            self._padding = value + 1
        self.refresh()

    def padding(self):
        """
        :rtype: int
        """
        return self._padding

    def addItems(self, items):
        """
        :type items: list[studioqt.ListWidgetItem]
        """
        for item in items:
            self.addItem(item)

    def setItems(self, items):
        """
        :type items: list[studioqt.ListWidgetItem]
        """
        self.clear()
        self.addItems(items)

    def itemsHiddenCount(self):
        """
        :rtype: int
        """
        return len([ item for item in self.items() if item.isHidden() ])

    def refreshFilter(self):
        self.setFilter(self.filter())

    def filter(self):
        """
        :rtype: str
        """
        return self._filter

    def setFilter(self, filter):
        """
        :type filter: str
        """
        self._filter = filter
        for row, item in enumerate(self.items()):
            if filter in item.searchText():
                item.setHidden(False)
            else:
                item.setHidden(True)

        self.refresh()

    def selectedItem(self):
        """
        :rtype: list[studioqt.ListWigdetItem]
        """
        item = None
        items = self.selectedItems()
        if items:
            item = items[-1]
        return item

    def selectedUrls(self):
        """
        :rtype: list[QtCore.QUrl]
        """
        return [ item.url() for item in self.selectedItems() ]

    def selectedPaths(self):
        """
        :rtype: list[str]
        """
        return [ item.url().path() for item in self.selectedItems() ]

    def rowAt(self, pos):
        """
        :type pos: QtCore.QPoint
        :rtype: int
        """
        item = self.itemAt(pos)
        index = self.indexFromItem(item)
        return index.row()

    def itemAtRow(self, row):
        """
        :type row: int
        :rtype: studioqt.ListWidgetItem
        """
        try:
            return self.items()[row]
        except IndexError:
            return -1

    def items(self):
        """
        :rtype: list[studioqt.ListWidgetItem]
        """
        items = QtGui.QListWidget.findItems(self, '*', QtCore.Qt.MatchWildcard)
        return items

    def takeAllItems(self):
        """
        :rtype: list[studioqt.ListWidgetItem]
        """
        items = self.items()
        return self.takeItems(items)

    def takeItems(self, items):
        """
        :rtype: list[studioqt.ListWidgetItem]
        """
        result = []
        for item in items:
            index = self.indexFromItem(item)
            item = self.takeItem(index.row())
            if item:
                result.append(item)

        return result

    def rowsFromItems(self, items):
        """
        :items items: list[studioqt.ListWidgetItem]
        :rtype: list[int]
        """
        return [ self.rowFromItem(item) for item in items ]

    def rowFromItem(self, item):
        """
        :items items: studioqt.ListWidgetItem
        :rtype: int
        """
        return self.indexFromItem(item).row()

    def setLocked(self, value):
        """
        :type value: bool
        """
        self._isLocked = value

    def isLocked(self):
        """
        :rtype: bool
        """
        return self._isLocked

    def setTextColor(self, color):
        """
        :type color: QtGui.QtColor
        """
        self._textColor = color

    def setTextSelectedColor(self, color):
        """
        :type color: QtGui.QtColor
        """
        self._textSelectedColor = color

    def setBackgroundColor(self, color):
        """
        :type color: QtGui.QtColor
        """
        self._backgroundColor = color

    def setBackgroundSelectedColor(self, color):
        """
        :type color: QtGui.QtColor
        """
        self._backgroundSelectedColor = color

    def textColor(self):
        """
        :rtype: QtGui.QColor
        """
        return self._textColor

    def textSelectedColor(self):
        """
        :rtype: QtGui.QColor
        """
        return self._textSelectedColor

    def backgroundColor(self):
        """
        :rtype: QtGui.QColor
        """
        return self._backgroundColor

    def backgroundHoverColor(self):
        """
        :rtype: QtGui.QColor
        """
        return self._backgroundHoverColor

    def backgroundSelectedColor(self):
        """
        :rtype: QtGui.QColor
        """
        return self._backgroundSelectedColor

    def currentItem(self):
        """
        :rtype: studioqt.ListWidgetItem
        """
        return self._currentItem

    def previousItem(self):
        """
        :rtype: studioqt.ListWidgetItem
        """
        return self._previousItem

    def isListView(self):
        """
        :rtype: bool
        """
        return self.viewMode() == QtGui.QListWidget.ListMode

    def isIconView(self):
        """
        :rtype: bool
        """
        return self.viewMode() == QtGui.QListWidget.IconMode

    def toggleTextVisible(self):
        if self.isItemTextVisible():
            self.setItemTextVisible(False)
        else:
            self.setItemTextVisible(True)

    def isItemTextVisible(self):
        """
        :rtype: bool
        """
        if self.isIconView():
            return self._isItemTextVisible
        else:
            return True

    def itemTextHeight(self):
        """
        :rtype: int
        """
        if self.isIconView() and self.isItemTextVisible():
            return 18 * self.dpi()
        else:
            return 0

    def setItemTextVisible(self, value):
        """
        :type value: int
        :rtype:
        """
        self._isItemTextVisible = value
        self.refresh()

    def showContextMenu(self):
        """
        :rtype: None
        """
        self.onShowContextMenu.emit()

    def selectItems(self, items):
        """
        :type items: list[studioqt.ListWidgetItem]
        """
        self._signalsEnabled = False
        try:
            for item in items:
                try:
                    item.setSelected(True)
                except RuntimeError:
                    pass

        finally:
            self._signalsEnabled = True

        self.onSelectionChanged.emit()

    def selectPaths(self, paths):
        """
        :type paths: list[str]
        """
        items = self.itemsFromPaths(paths)
        self.selectItems(items)

    def selectionChanged(self, selected, deselected):
        """
        :type selected: QtGui.QItemSelection
        :type deselected: QtGui.QItemSelection
        """
        indexes1 = selected.indexes()
        selectedItems = self.itemsFromIndexes(indexes1)
        indexes2 = deselected.indexes()
        deselectedItems = self.itemsFromIndexes(indexes2)
        items = selectedItems + deselectedItems
        for item in items:
            item.itemSelectionChanged(selectedItems, deselectedItems)

        if self._signalsEnabled:
            self.onSelectionChanged.emit()

    def itemsFromIndexes(self, indexes):
        """
        :type indexes: list[QtGui.QModelIndex]
        :rtype: list[studiolibrary.QListWidgetItem]
        """
        items = []
        for index in indexes:
            items.append(self.itemFromIndex(index))

        return items

    def moveItems(self, row, items):
        """
        :type row: int
        :type items: list[ListWidgetItem]
        """
        item = self.itemAtRow(row)
        rows = self.rowsFromItems(items)
        if row != -1 and row in rows:
            logger.debug('Cannot insert items at same place!')
            return
        removedItems = self.takeItems(items) or items
        removedItems.reverse()
        if item and row != -1:
            row_ = self.rowFromItem(item)
            if row_ < row:
                row = row_ + 1
            else:
                row = row_
        else:
            row = len(self.items())
        for item in removedItems:
            self.insertItem(row, item)

        self.itemOrderChanged.emit()

    def setSortBy(self, sortOrder = None):
        pass

    def sortByMenu(self, parent = None):
        """
        :type parent: QtGui.QWidget
        :rtype: QtGui.QMenu
        """
        menu = QtGui.QMenu(parent)
        menu.setTitle('Sort by')
        action = QtGui.QAction('Name', menu)
        action.setCheckable(True)
        action.triggered[bool].connect(self.setSortBy)
        menu.addAction(action)
        action = QtGui.QAction('Modified', menu)
        action.setCheckable(True)
        action.triggered[bool].connect(self.setSortBy)
        menu.addAction(action)
        action = QtGui.QAction('Modified', menu)
        action.setCheckable(True)
        action.triggered[bool].connect(self.setSortBy)
        menu.addAction(action)
        return menu

    def settingsMenu(self, parent = None):
        """
        Return the settings menu for changing the list widget.
        
        :rtype: QtGui.QMenu
        """
        parent = parent or self
        menu = QtGui.QMenu('View', parent)
        action = QtGui.QAction('Show labels', menu)
        action.setCheckable(True)
        action.setChecked(self.isItemTextVisible())
        action.triggered[bool].connect(self.setItemTextVisible)
        menu.addAction(action)
        menu.addSeparator()
        action = studioqt.SliderAction('Size', menu)
        action.slider().setMinimum(10)
        action.slider().setMaximum(200)
        action.slider().setValue(self.zoomAmount())
        action.slider().valueChanged.connect(self.setZoomAmount)
        menu.addAction(action)
        action = studioqt.SliderAction('Border', menu)
        action.slider().setMinimum(0)
        action.slider().setMaximum(20)
        action.slider().setValue(self.padding())
        action.slider().valueChanged.connect(self.setPadding)
        menu.addAction(action)
        action = studioqt.SliderAction('Spacing', menu)
        action.slider().setMinimum(0)
        action.slider().setMaximum(25)
        action.slider().setValue(self.spacing())
        action.slider().valueChanged.connect(self.setSpacing)
        menu.addAction(action)
        menu.addSeparator()
        sortByMenu = self.sortByMenu(parent=menu)
        menu.addMenu(sortByMenu)
        return menu

    def showSettingsMenu(self):
        """
        :rtype: QtGui.QAction
        """
        menu = self.settingsMenu()
        point = QtGui.QCursor.pos()
        return menu.exec_(point)

    def settings(self):
        """
        :rtype: dict
        """
        settings = {}
        viewSize = self.viewSize()
        settings['padding'] = self.padding()
        settings['spacing'] = self.spacing()
        settings['viewSizeWidth'] = viewSize.width()
        settings['selectedPaths'] = self.selectedPaths()
        settings['isItemTextVisible'] = self.isItemTextVisible()
        return settings

    def setSettings(self, settings):
        """
        :type settings: dict
        """
        settings = settings or {}
        padding = settings.get('padding', self.padding())
        self.setPadding(padding)
        spacing = settings.get('spacing', self.spacing())
        self.setSpacing(spacing)
        selectedPaths = settings.get('selectedPaths', [])
        if selectedPaths:
            self.selectPaths(selectedPaths)
        viewSize = settings.get('viewSizeWidth', self.viewSize().width())
        self.setViewSize(QtCore.QSize(viewSize, viewSize))
        textVisible = settings.get('isItemTextVisible', self.isItemTextVisible())
        self.setItemTextVisible(textVisible)

    def itemHoverEvent(self, item, event):
        """
        :type item: recordswidgetitem.ListWidgetItem
        :event event: QtCore.QEvent
        """
        item.mouseMoveEvent(event)

    def itemEnterEvent(self, item, event):
        """
        :type item: recordswidgetitem.ListWidgetItem
        :event event: QtCore.QEvent
        """
        self.showAnnotation(item, self.DEFAULT_ANNOTATION_WAIT)
        item.mouseEnterEvent(event)

    def itemLeaveEvent(self, item, event):
        """
        :type item: recordswidgetitem.ListWidgetItem
        :event event: QtCore.QEvent
        """
        self.hideAnnotation()
        item.mouseLeaveEvent(event)

    def leaveEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideAnnotation()
        if self._previousItem:
            self.itemLeaveEvent(self._previousItem, event)
        self._previousItem = None
        QtGui.QListWidget.leaveEvent(self, event)

    def keyPressEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideAnnotation()
        if event.key() == QtCore.Qt.Key_Control:
            self._zoomIndex = None
            self._zoomAmount = None
        for item in self.selectedItems():
            item.keyPressEvent(event)

    def mousePressEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideAnnotation()
        self._buttonDown = event.button()
        item = self.itemAt(event.pos())
        QtGui.QListWidget.mousePressEvent(self, event)
        if not item:
            self.clearSelection()
            self._currentItem = None
        else:
            self.itemMousePressEvent(item, event)
        if event.button() == QtCore.Qt.RightButton:
            self.showContextMenu()

    def itemMousePressEvent(self, item, event):
        """
        :type item: studioqt.ListWidgetItem
        :type event: QtCore.QEvent
        :rtype: None
        """
        self._currentItem = item
        if event.button() == QtCore.Qt.LeftButton:
            self.endDrag()
            self._dragStartPos = event.pos()
            self._dragStartIndex = self.indexAt(event.pos())
        elif event.button() == QtCore.Qt.RightButton:
            self.endDrag()
            if item is not None:
                item.mousePressEvent(event)
            self._currentItem = None
        item.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideAnnotation()
        item = self.itemAt(event.pos())
        event._item = item
        self._buttonDown = None
        if self._currentItem:
            self._currentItem.mouseReleaseEvent(event)
            self._currentItem = None
        else:
            QtGui.QListWidget.mouseReleaseEvent(self, event)
        self.endDrag()
        self.repaint()

    def mouseMoveEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        item = self.itemAt(event.pos())
        if self._currentItem:
            self._currentItem.mouseMoveEvent(event)
        else:
            self.updateItemEvent(event)
        if item and not self._drag and self._dragStartIndex and self._dragStartIndex.isValid():
            event._item = self._currentItem
            self.startDrag(event)
        else:
            QtGui.QListWidget.mouseMoveEvent(self, event)
        if self._buttonDown:
            self.repaint()

    def updateItemEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        item = self.itemAt(event.pos())
        if item:
            if id(self._previousItem) != id(item):
                self._dragStartIndex = None
                if self._previousItem:
                    self.itemLeaveEvent(self._previousItem, event)
                self.itemEnterEvent(item, event)
            self.itemHoverEvent(item, event)
        elif self._previousItem:
            self.itemLeaveEvent(self._previousItem, event)
        self._previousItem = item

    def setViewSize(self, value):
        """
        :type value: int
        :rtype: None
        """
        value = value.width()
        self._zoomAmount = value
        if value < self.minimumListSize():
            value = self.minimumListSize()
        if value > self.minimumIconSize():
            self.setViewMode(QtGui.QListWidget.IconMode)
        else:
            self.setViewMode(QtGui.QListWidget.ListMode)
        size = QtCore.QSize(value, value + self.itemTextHeight())
        self.setIconSize(size)
        self.scrollToSelected()
        self.setAcceptDrops(True)
        self.setSpacing(self.spacing())
        self._viewSize = size
        self.viewSizeChanged.emit(size)

    def viewSize(self):
        """
        :rtype: int
        """
        return self._viewSize

    def updateViewSize(self):
        """
        """
        self.setViewSize(self.viewSize())

    def wheelScrollStep(self):
        """
        :rtype: int
        """
        return self.DEFAULT_WHEEL_SCROLL_STEP

    def zoomAmount(self):
        """
        :rtype: int
        """
        return self.viewSize().width()

    def minimumIconSize(self):
        """
        :rtype: int
        """
        return self._minimumIconSize * self.dpi()

    def minimumListSize(self):
        """
        :rtype: int
        """
        return self._minimumListSize * self.dpi()

    def setZoomAmount(self, value):
        """
        :type value: int
        """
        self.setViewSize(QtCore.QSize(value, value))
        msg = 'Size: {0}%'.format(value)
        self.showMessage(msg, repaint=False)
        self.zoomAmountChanged.emit(value)

    def scrollToSelected(self):
        """
        """
        indexes = self.selectedIndexes()
        if indexes:
            index = indexes[0]
            self.scrollTo(index, QtGui.QAbstractItemView.EnsureVisible)

    def wheelEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideAnnotation()
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier or modifiers == QtCore.Qt.AltModifier:
            numDegrees = event.delta() / 8
            numSteps = numDegrees / 15
            delta = numSteps * self.wheelScrollStep()
            value = self.viewSize().width() + delta
            self.setZoomAmount(value)
            event.accept()
        else:
            QtGui.QListWidget.wheelEvent(self, event)
        self.updateItemEvent(event)

    def fadeOut(self):
        """
        """
        self._messageFadeOutTimer.start(1)

    def _fadeOut(self):
        """
        """
        alpha = self.messageAlpha()
        if alpha > 0:
            alpha -= 2
            self.setMessageAlpha(alpha)
            self.repaintMessage()
        else:
            self._messageFadeOutTimer.stop()
            self._messageDisplayTimer.stop()

    def showMessage(self, text, repaint = True):
        """
        :type text: str
        :type repaint: bool
        :rtype: None
        """
        self._messageText = text
        self._messageAlpha = 255
        self._messageDisplayTimer.stop()
        self._messageDisplayTimer.start(500)
        if repaint:
            self.repaintMessage()

    def messageAlpha(self):
        """
        :rtype: float
        """
        return float(self._messageAlpha)

    def setMessageAlpha(self, value):
        """
        :type value: float
        :rtype: None
        """
        self._messageAlpha = value

    def messageFont(self):
        """
        :rtype: QtGui.QFont
        """
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(18)
        return font

    def messageText(self):
        """
        :rtype: str
        """
        return self._messageText

    def messageRect(self, margin = 40):
        """
        :rtype: QtCore.QRect
        """
        dpi = self.dpi()
        font = self.messageFont()
        text = self.messageText()
        margin = margin * self.dpi()
        m = QtGui.QFontMetrics(font)
        size = self.size()
        w = size.width()
        h = size.height()
        textWidth = m.width(text) * dpi
        x = w / 2 - textWidth / 2
        y = h / 2
        x -= margin / 2
        w = textWidth + margin / 2
        return QtCore.QRect(x, y, w, 90 * dpi)

    def messageCornerSize(self):
        """
        :rtype: int
        """
        return self._messageCornerSize

    def repaintMessage(self):
        """
        :rtype: None
        """
        rect = self.messageRect(margin=100)
        self.repaint(rect)

    def paintEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        QtGui.QListWidget.paintEvent(self, event)
        if self.messageText() and self.messageAlpha() > 0:
            painter = QtGui.QPainter(self.viewport())
            messageRect = self.messageRect()
            ratio = float(messageRect.width()) / float(messageRect.height())
            yRnd = ratio * messageRect.width() / 100 * self.messageCornerSize()
            xRnd = ratio * messageRect.height() / 100 * self.messageCornerSize()
            color = QtGui.QColor(self._messageBackgroundColor)
            color.setAlpha(self.messageAlpha() / 2)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(color)
            painter.setRenderHints(QtGui.QPainter.Antialiasing)
            painter.drawRoundRect(messageRect.x(), messageRect.y(), messageRect.width(), messageRect.height(), xRnd, yRnd)
            font = self.messageFont()
            color = QtGui.QColor(self._messageColor)
            color.setAlpha(self.messageAlpha())
            painter.setPen(color)
            painter.setFont(font)
            painter.drawText(messageRect, QtCore.Qt.AlignCenter, self._messageText)

    def dragThreshold(self):
        """
        :rtype: int
        """
        return self.DEFAULT_DRAG_THRESHOLD

    def mimeData(self, items):
        """
        :type items: list[studioqt.ListWidgetItem]
        :rtype: QtCore.QMimeData
        """
        mimeData = QtCore.QMimeData()
        urls = []
        for item in items:
            urls.append(item.url())

        mimeData.setUrls(urls)
        return mimeData

    def dragEnterEvent(self, event):
        """
        :event event: QtCore.QEvent
        """
        if event.mimeData().hasUrls() and self.isDragEnabled():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        :event event: QtCore.QEvent
        """
        if event.mimeData().hasUrls() and self.isDragEnabled():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        :type event: QtCore.QEvent
        """
        mimeData = event.mimeData()
        if mimeData.hasUrls() and self.isDragEnabled():
            event.accept()
            self.itemDropping.emit(event)
            items = self.itemsFromUrls(mimeData.urls())
            if items:
                row = self.rowAt(event.pos())
                self.moveItems(row, items)
                self.selectItems(items)
            self.itemDropped.emit(event)

    def dragPixmap(self, item):
        """
        :type item: recordwidgetitem.RecordWidgetItem
        :rtype: QtGui.QPixmap
        """
        pixmap = QtGui.QPixmap()
        items = self.selectedItems()
        rect = self.visualRect(self.indexFromItem(item))
        pixmap = pixmap.grabWidget(self, rect)
        if len(items) > 1:
            cWidth = 35
            cPadding = 5
            cText = str(len(items))
            cX = pixmap.rect().center().x() - float(cWidth / 2)
            cY = pixmap.rect().top() + cPadding
            cRect = QtCore.QRect(cX, cY, cWidth, cWidth)
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(self.backgroundSelectedColor())
            painter.drawEllipse(cRect.center(), float(cWidth / 2), float(cWidth / 2))
            font = QtGui.QFont('Serif', 12, QtGui.QFont.Light)
            painter.setFont(font)
            painter.setPen(self.textSelectedColor())
            painter.drawText(cRect, QtCore.Qt.AlignCenter, str(cText))
        return pixmap

    def startDrag(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if not self.isDragEnabled():
            logger.debug('Dragging has been disabled!')
            return
        point = self._dragStartPos - event.pos()
        dt = self.dragThreshold()
        if point.x() > dt or point.y() > dt or point.x() < -dt or point.y() < -dt:
            item = event._item
            pixmap = self.dragPixmap(item)
            hotSpot = QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2)
            items = self.selectedItems()
            mimeData = self.mimeData(items)
            self._drag = QtGui.QDrag(self)
            self._drag.setPixmap(pixmap)
            self._drag.setHotSpot(hotSpot)
            self._drag.setMimeData(mimeData)
            self._drag.start(QtCore.Qt.MoveAction)

    def endDrag(self):
        """
        :rtype: None
        """
        logger.debug('End Drag')
        self._buttonDown = None
        self._dragStartIndex = None
        if self._drag:
            del self._drag
            self._drag = None
