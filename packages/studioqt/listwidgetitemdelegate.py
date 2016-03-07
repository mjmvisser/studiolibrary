#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/studioqt\listwidgetitemdelegate.py
import logging
from PySide import QtGui
__all__ = ['ListWidgetItemDelegate']
logger = logging.getLogger(__name__)

class ListWidgetItemDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, parent):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self._widget = parent

    def sizeHint(self, option, index):
        item = self._widget.itemFromIndex(index)
        return item.sizeHint()

    def paint(self, painter, option, index):
        if index.column() == 0:
            item = self._widget.itemFromIndex(index)
            return item.paint(painter, option, index)
        else:
            return QtGui.QStyledItemDelegate.paint(self, painter, option, index)
