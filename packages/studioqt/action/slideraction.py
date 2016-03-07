#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/studioqt\action\slideraction.py
from PySide import QtGui
from PySide import QtCore

class SliderAction(QtGui.QWidgetAction):

    def __init__(self, label = '', parent = None, dpi = 1):
        """
        :type parent: QtGui.QMenu
        """
        QtGui.QWidgetAction.__init__(self, parent)
        self.setObjectName('customAction')
        self._frame = QtGui.QFrame(parent)
        self._label = QtGui.QLabel(label, self._frame)
        self._label.setObjectName('sliderActionLabel')
        self._label.setMinimumWidth(85)
        self._slider = QtGui.QSlider(QtCore.Qt.Horizontal, self._frame)

    def frame(self):
        return self._frame

    def label(self):
        return self._label

    def slider(self):
        return self._slider

    def createWidget(self, parent):
        """
        :type parent: QtGui.QMenu
        """
        actionWidget = self.frame()
        actionWidget.setObjectName('sliderActionWidget')
        actionLayout = QtGui.QHBoxLayout(actionWidget)
        actionLayout.setSpacing(0)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(self.label())
        actionLayout.addWidget(self.slider())
        actionWidget.setLayout(actionLayout)
        return actionWidget
