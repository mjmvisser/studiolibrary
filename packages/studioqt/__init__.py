#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/studioqt\__init__.py
import os
from studioqt.utils import *
from studioqt.color import Color
from studioqt.pixmap import Pixmap
from studioqt.resource import Resource
from studioqt.stylesheet import StyleSheet
from studioqt.listwidget import ListWidget
from studioqt.listwidgetitem import ListWidgetItem
from studioqt.listwidgetitemdelegate import ListWidgetItemDelegate
from studioqt.action.slideraction import SliderAction
PATH = os.path.abspath(__file__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
PACKAGES_DIRNAME = DIRNAME + '/packages'
RESOURCE_DIRNAME = DIRNAME + '/resource'
_resource = None

def resource():
    """
    :rtype: studioqt.Resource
    """
    global _resource
    if not _resource:
        _resource = Resource(dirname=RESOURCE_DIRNAME)
    return _resource


def icon(*args, **kwargs):
    """
    :type name: str
    :type extension: str
    :rtype: QtGui.QIcon
    """
    return resource().icon(*args, **kwargs)


def pixmap(*args, **kwargs):
    """
    :type name: str
    :type extension: str
    :rtype: QtGui.QPixmap
    """
    return resource().pixmap(*args, **kwargs)
