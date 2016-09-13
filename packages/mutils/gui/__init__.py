#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/mutils\gui\__init__.py
import maya.OpenMayaUI as omui
from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets
try:
    from shiboken import wrapInstance
except Exception:
    from shiboken2 import wrapInstance

from .modelpanelwidget import ModelPanelWidget
from .capturedialog import *

def mayaWindow():
    """
    :rtype: QMainWindow
    """
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPtr), QtWidgets.QMainWindow)
