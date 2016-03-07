#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\__init__.py
import os
import sys
__version__ = '1.12.1'
__encoding__ = sys.getfilesystemencoding()
_package = None
_resource = None
_analytics = None
_scriptJob = None
PATH = unicode(os.path.abspath(__file__), __encoding__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
PACKAGES_DIRNAME = DIRNAME + '/packages'
RESOURCE_DIRNAME = DIRNAME + '/gui/resource'
PACKAGE_HELP_URL = 'http://www.studiolibrary.com'
PACKAGE_JSON_URL = 'http://dl.dropbox.com/u/28655980/studiolibrary/studiolibrary.json'
CHECK_FOR_UPDATES_ENABLED = True

def setup(path):
    """
    :type path: str
    :rtype: None
    """
    if os.path.exists(path) and path not in sys.path:
        print "Adding '{path}' to the sys.path".format(path=path)
        sys.path.append(path)


setup(PACKAGES_DIRNAME)
import studioqt
from studiolibrary.main import main
from studiolibrary.core.utils import *
from studiolibrary.core.tempdir import TempDir
from studiolibrary.core.package import Package
from studiolibrary.core.basepath import BasePath
from studiolibrary.core.metafile import MetaFile
from studiolibrary.core.settings import Settings
from studiolibrary.core.shortuuid import ShortUUID
from studiolibrary.core.analytics import Analytics
from studiolibrary.core.masterpath import MasterPath
from studiolibrary.core.baseplugin import BasePlugin
from studiolibrary.core.pluginmanager import PluginManager
from studiolibrary.api.folder import Folder
from studiolibrary.api.record import Record
from studiolibrary.api.plugin import Plugin
from studiolibrary.api.library import Library
from studiolibrary.gui import *
from studiolibrary.gui.statuswidget import StatusWidget
from studiolibrary.gui.folderswidget import FoldersWidget
from studiolibrary.gui.mayadockwidgetmixin import MayaDockWidgetMixin
from studiolibrary.gui.librarywidget import LibraryWidget
from studiolibrary.gui.librariesmenu import LibrariesMenu
from studiolibrary.gui.settingsdialog import SettingsDialog
from studiolibrary.gui.newfolderdialog import NewFolderDialog
from studiolibrary.gui.imagesequencetimer import ImageSequenceTimer
from studiolibrary.gui.imagesequencetimer import ImageSequenceWidget

def enableMayaClosedEvent():
    """
    :rtype: None
    """
    global _scriptJob
    if isMaya():
        import maya.cmds
        if not _scriptJob:
            _scriptJob = maya.cmds.scriptJob(event=['quitApplication', 'import studiolibrary;studiolibrary.mayaClosedEvent()'])


def mayaClosedEvent():
    """
    :rtype: None
    """
    for window in windows():
        window.saveSettings()


def resource():
    """
    :rtype: studioqt.Resource
    """
    global _resource
    if not _resource:
        _resource = studioqt.Resource(dirname=RESOURCE_DIRNAME)
    return _resource


def package():
    """
    :rtype: package.Package
    """
    global _package
    if not _package:
        _package = Package()
    _package.setJsonUrl(PACKAGE_JSON_URL)
    _package.setHelpUrl(PACKAGE_HELP_URL)
    _package.setVersion(__version__)
    return _package


def version():
    """
    :rtype: str
    """
    return package().version()


def analytics():
    """
    :rtype: analytics.Analytics
    """
    global _analytics
    if not _analytics:
        _analytics = Analytics(tid=Analytics.DEFAULT_ID, name='StudioLibrary', version=package().version())
    _analytics.setEnabled(Analytics.ENABLED)
    return _analytics


def windows():
    """
    :rtype: list[MainWindow]
    """
    return Library.windows()


def library(name = None):
    """
    :type name: str
    :rtype: studiolibrary.Library
    """
    return Library.fromName(name)


def libraries():
    """
    :rtype: list[studiolibrary.Library]
    """
    return Library.libraries()


def loadFromCommand():
    """
    """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-p', '--plugins', dest='plugins', help='', metavar='PLUGINS', default='None')
    parser.add_option('-r', '--root', dest='root', help='', metavar='ROOT')
    parser.add_option('-n', '--name', dest='name', help='', metavar='NAME')
    parser.add_option('-v', '--version', dest='version', help='', metavar='VERSION')
    options, args = parser.parse_args()
    name = options.name
    plugins = eval(options.plugins)
    main(name=name, plugins=plugins)


def about():
    """
    Return a small description about the Studio Library.
    
    :rtype str
    """
    msg = '\n-------------------------------\nStudio Library is a free python script for managing poses and animation in Maya.\nComments, suggestions and bug reports are welcome.\n\nVersion: {version}\nPackage: {package}\n\nwww.studiolibrary.com\nkurt.rathjen@gmail.com\n--------------------------------\n'
    msg = msg.format(version=package().version(), package=PATH)
    return msg


from studiolibrary import config
if __name__ == '__main__':
    loadFromCommand()
else:
    print about()
