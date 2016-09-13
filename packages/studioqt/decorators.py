#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/studioqt\decorators.py
from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

def showWaitCursor(fn):

    def wrapped(*args, **kwargs):
        cursor = QtGui.QCursor(QtCore.Qt.WaitCursor)
        QtWidgets.QApplication.setOverrideCursor(cursor)
        try:
            return fn(*args, **kwargs)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped
