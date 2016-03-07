#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\gui\statuswidget.py
from PySide import QtGui
from PySide import QtCore
import studioqt
import studiolibrary
DISPLAY_TIME = 6000

class StatusWidget(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        studioqt.loadUi(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setObjectName('statusWidget')
        self.setFixedHeight(19)
        self.setMinimumWidth(5)
        self._timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self._timer, QtCore.SIGNAL('timeout()'), self.clear)

    def setError(self, text, msec = DISPLAY_TIME):
        icon = studiolibrary.resource().icon('error')
        self.ui.button.setIcon(icon)
        self.ui.message.setStyleSheet('color: rgb(222, 0, 0);')
        self.setText(text, msec)

    def setWarning(self, text, msec = DISPLAY_TIME):
        icon = studiolibrary.resource().icon('warning')
        self.ui.button.setIcon(icon)
        self.ui.message.setStyleSheet('color: rgb(222, 180, 0);')
        self.setText(text, msec)

    def setInfo(self, text, msec = DISPLAY_TIME):
        icon = studiolibrary.resource().icon('info')
        self.ui.button.setIcon(icon)
        self.ui.message.setStyleSheet('')
        self.setText(text, msec)

    def setText(self, text, msec = DISPLAY_TIME):
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
        icon = studiolibrary.resource().icon('blank')
        self.ui.button.setIcon(icon)
