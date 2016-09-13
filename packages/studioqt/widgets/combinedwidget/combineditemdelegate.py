#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/studioqt\widgets\combinedwidget\combineditemdelegate.py
from studioqt import QtWidgets
from studioqt import QtCore
import studioqt

class CombinedItemDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self):
        """
        This class is used to display data for the items in a CombinedWidget.
        """
        QtWidgets.QStyledItemDelegate.__init__(self)
        self._combinedWidget = None

    def combinedWidget(self):
        """
        Return the CombinedWidget that contains the item delegate.
        
        :rtype: studioqt.CombinedWidget
        """
        return self._combinedWidget

    def setCombinedWidget(self, combinedWidget):
        """
        Set the CombinedWidget for the delegate.
        
        :type combinedWidget: studioqt.CombinedWidget
        :rtype: None
        """
        self._combinedWidget = combinedWidget

    def sizeHint(self, option, index):
        """
        Return the size for the given index.
        
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: QtCore.QSize
        """
        item = self.combinedWidget().itemFromIndex(index)
        return item.sizeHint()

    def paint(self, painter, option, index):
        """
        Paint performs low-level painting for the given model index.
        
        :type painter:  QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        item = self.combinedWidget().itemFromIndex(index)
        item.paint(painter, option, index)
