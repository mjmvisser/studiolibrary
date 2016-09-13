#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary\gui\previewwidget.py
from studioqt import QtWidgets
import studioqt
__all__ = ['PreviewWidget']

class PreviewWidget(QtWidgets.QWidget):

    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)
        studioqt.loadUi(self)

    def window(self):
        return self.parent().window()
