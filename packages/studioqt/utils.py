#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/studioqt\utils.py
import os
import sys
import inspect
import logging
import contextlib
from PySide import QtGui
from PySide import QtCore
from PySide import QtUiTools
__all__ = ['app',
 'loadUi',
 'isPySide',
 'isAltModifier',
 'isControlModifier']
logger = logging.getLogger(__name__)

@contextlib.contextmanager
def app():
    """
    
    .. code-block:: python
        import studioqt
    
        with studioqt():
            widget = QWidget(None)
            widget.show()
    
    :rtype: None
    """
    app_ = None
    isAppRunning = bool(QtGui.QApplication.instance())
    if not isAppRunning:
        app_ = QtGui.QApplication(sys.argv)
    yield
    if not isAppRunning:
        sys.exit(app_.exec_())


def isPySide():
    """
    :rtype: bool
    """
    return True


def uiPath(cls):
    """
    :type cls: type
    :rtype: str
    """
    name = cls.__name__
    path = inspect.getfile(cls)
    dirname = os.path.dirname(path)
    path = dirname + '/resource/ui/' + name + '.ui'
    return path


def loadUi(widget, path = None):
    """
    .. code-block:: python
        import studioqt
    
        class Widget(QtGui.QWidget):
            def __init__(self)
                super(Widget, self).__init__()
                studioqt.loadUi(self)
    
        with studioqt.app():
            widget = Widget()
            widget.show()
    
    :type widget: QWidget or QDialog
    :type path: str
    :rtype: None
    """
    if not path:
        path = uiPath(widget.__class__)
    loadUiPySide(widget, path)


def loadUiPySide(widget, path = None):
    """
    :type widget: QtGui.QWidget
    :type path: str
    :rtype: None
    """
    loader = QtUiTools.QUiLoader()
    loader.setWorkingDirectory(os.path.dirname(path))
    f = QtCore.QFile(path)
    f.open(QtCore.QFile.ReadOnly)
    widget.ui = loader.load(path, widget)
    f.close()
    layout = QtGui.QVBoxLayout()
    layout.setObjectName('uiLayout')
    layout.addWidget(widget.ui)
    widget.setLayout(layout)
    layout.setContentsMargins(0, 0, 0, 0)
    widget.setMinimumWidth(widget.ui.minimumWidth())
    widget.setMinimumHeight(widget.ui.minimumHeight())
    widget.setMaximumWidth(widget.ui.maximumWidth())
    widget.setMaximumHeight(widget.ui.maximumHeight())


def mayaWindow():
    """
    :rtype: QtCore.QObject
    """
    instance = None
    try:
        import maya.OpenMayaUI as mui
        import sip
        ptr = mui.MQtUtil.mainWindow()
        instance = sip.wrapinstance(long(ptr), QtCore.QObject)
    except Exception:
        logger.debug('Warning: Cannot find a maya window.')

    return instance


def isAltModifier():
    """
    
    :rtype: bool
    """
    modifiers = QtGui.QApplication.keyboardModifiers()
    return modifiers == QtCore.Qt.AltModifier


def isControlModifier():
    """
    :rtype: bool
    """
    modifiers = QtGui.QApplication.keyboardModifiers()
    return modifiers == QtCore.Qt.ControlModifier
