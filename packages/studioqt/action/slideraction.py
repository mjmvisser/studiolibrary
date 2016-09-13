#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/studioqt\action\slideraction.py
from studioqt import QtWidgets
from studioqt import QtCore

class SliderAction(QtWidgets.QWidgetAction):

    def __init__(self, label = '', parent = None, dpi = 1):
        """
        :type parent: QtWidgets.QMenu
        """
        QtWidgets.QWidgetAction.__init__(self, parent)
        self.setObjectName('customAction')
        self._frame = QtWidgets.QFrame(parent)
        self._label = QtWidgets.QLabel(label, self._frame)
        self._label.setObjectName('sliderActionLabel')
        self._label.setMinimumWidth(85)
        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self._frame)
        self.valueChanged = self._slider.valueChanged

    def frame(self):
        return self._frame

    def label(self):
        return self._label

    def slider(self):
        return self._slider

    def createWidget(self, parent):
        """
        :type parent: QtWidgets.QMenu
        """
        actionWidget = self.frame()
        actionWidget.setObjectName('sliderActionWidget')
        actionLayout = QtWidgets.QHBoxLayout(actionWidget)
        actionLayout.setSpacing(0)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(self.label())
        actionLayout.addWidget(self.slider())
        actionWidget.setLayout(actionLayout)
        return actionWidget
