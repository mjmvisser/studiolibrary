#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary\__init__.py
"""
Released subject to the BSD License
Please visit http://www.voidspace.org.uk/python/license.shtml

Contact: kurt.rathjen@gmail.com
Comments, suggestions and bug reports are welcome.
Copyright (c) 2015, Kurt Rathjen, All rights reserved.

It is a very non-restrictive license but it comes with the usual disclaimer.
This is free software: test it, break it, just don't blame me if it eats your
data! Of course if it does, let me know and I'll fix the problem so that it
doesn't happen to anyone else.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
   # * Redistributions of source code must retain the above copyright
   #   notice, this list of conditions and the following disclaimer.
   # * Redistributions in binary form must reproduce the above copyright
   # notice, this list of conditions and the following disclaimer in the
   # documentation and/or other materials provided with the distribution.
   # * Neither the name of Kurt Rathjen nor the
   # names of its contributors may be used to endorse or promote products
   # derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY KURT RATHJEN ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL KURT RATHJEN BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""
import re
import os
import sys
from other.utils import *
from other.tempdir import *
from other.metafile import *
from other.analytics import *
from other.eventhook import *
__version__ = '1.6.14'
__windows = {}
__scriptJob = None
__application = None

def dirname():
    """
    @rtype: str
    """
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(unicode(os.path.abspath(__file__), encoding)).replace('\\', '/')


DEFAULT_PLUGINS = ['studiolibraryplugins.lockplugin',
 'studiolibraryplugins.poseplugin',
 'studiolibraryplugins.animationplugin',
 'studiolibraryplugins.mirrortableplugin',
 'studiolibraryplugins.selectionsetplugin']
QT_DIRNAME = ''
PACKAGES_DIRNAME = dirname() + '/packages'
SETTINGS_DIRNAME = os.getenv('APPDATA') or os.getenv('HOME')
DOWNLOAD_INFO_URL = 'http://dl.dropbox.com/u/28655980/studiolibrary/studiolibrary.txt'
addSysPath(PACKAGES_DIRNAME)
_isPySide = False
try:
    from PySide import QtGui
    from PySide import QtCore
    _isPySide = True
except ImportError:
    try:
        from PyQt4 import QtGui
        from PyQt4 import QtCore
    except ImportError:
        _mayaVersion = '2012x64'
        if isMaya():
            import maya.cmds
            _mayaVersion = maya.cmds.about(version=True)
            if '2011' in _mayaVersion:
                _mayaVersion = '2011x64'
            elif '2012' in _mayaVersion:
                _mayaVersion = '2012x64'
            elif '2013' in _mayaVersion:
                _mayaVersion = '2013x64'
        QT_DIRNAME = PACKAGES_DIRNAME + '/' + _mayaVersion
        addSysPath(QT_DIRNAME)
        try:
            from PySide import QtGui
            from PySide import QtCore
            _isPySide = True
        except ImportError:
            try:
                from PyQt4 import QtGui
                from PyQt4 import QtCore
            except ImportError:
                try:
                    import maya.cmds
                    msg = '\nTraceback:\nCannot find PyQt for:\nMaya Version: %s\nPyQt Path: %s\nStudio Library Path: %s\n            ' % (maya.cmds.about(version=True), QT_DIRNAME, os.path.dirname(__file__))
                    print msg
                    raise
                except:
                    raise

def isPySide():
    return _isPySide


from settings import *
from folder import *
from record import *
from plugin import *
from gui import *

def main(name = None, show = True, **kwargs):
    """
    @type name: str
    @type show: bool
    @type kwargs: dict[]
    @rtype: @raise Exception:
    """
    import studiolibrary
    if not name:
        name = 'Default'
    add = kwargs.get('add', None)
    plugins = kwargs.get('plugins', list())
    root = kwargs.get('root', None)
    if root:
        if '\\' in root:
            raise Exception("Please use '/' instead of '\\'. Invalid token found in root path '%s'!" % root)
        if not os.path.exists(root):
            raise Exception("Cannot find the root folder path '%s'!" % root)
    if add or not plugins:
        _plugins = []
        _plugins.extend(DEFAULT_PLUGINS)
        if add:
            _plugins.extend(plugins)
    else:
        _plugins = plugins
    kwargs['plugins'] = _plugins
    if not isMaya():
        studiolibrary.__application = QtGui.QApplication(sys.argv)
    else:
        import maya.cmds
        if not studiolibrary.__scriptJob:
            studiolibrary.__scriptJob = maya.cmds.scriptJob(event=['quitApplication', 'import studiolibrary;\nfor window in studiolibrary.mainWindows().values():\n\twindow.saveSettings()'])
    if not root:
        root = LibrarySettings(name).get('kwargs', None).get('root', None)
        if not root and show:
            root = showWelcomeDialog()
            kwargs['root'] = root
    if name not in studiolibrary.mainWindows():
        w = studiolibrary.MainWindow(name=name, **kwargs)
        studiolibrary.mainWindows().setdefault(name, w)
    else:
        w = studiolibrary.mainWindows()[name]
        w.loadLibrary(name, kwargs)
        w.close()
    if show:
        w.showNormal()
        w.raiseWindow()
    if not studiolibrary.isMaya():
        sys.exit(studiolibrary.__application.exec_())
    return studiolibrary.mainWindows().get(name, None)


def version():
    """
    @rtype: str
    """
    return __version__


_analytics = Analytics(tid='UA-50172384-1', name='StudioLibrary', version=version())

def analytics():
    """
    @rtype: analytics.Analytics
    """
    return _analytics


def setDebug(enable):
    """
    @type enable: bool
    @raise:
    """
    try:
        import mutils
        mutils.setDebug(enable)
    except ImportError as e:
        print e


def stableVersion():
    """
    @rtype: str
    @raise:
    """
    try:
        data = downloadUrl(DOWNLOAD_INFO_URL)
        if data:
            if data.startswith('{'):
                data = eval(data.strip(), {})
                return data.get('version', version())
    except:
        raise


def isUpdateAvailable():
    """
    @rtype: bool | None
    """
    version = stableVersion()
    reNumbers = re.compile('[0-9]+')
    if version:
        major1, miner1, patch1 = [ int(reNumbers.search(value).group(0)) for value in __version__.split('.') ]
        major2, miner2, patch2 = [ int(reNumbers.search(value).group(0)) for value in version.split('.') ]
        if major1 < major2:
            return True
        if major1 <= major2 and miner1 < miner2:
            return True
        if major1 <= major2 and miner1 <= miner2 and patch1 < patch2:
            return True


def showWelcomeDialog():
    """
    """
    import studiolibrary
    dialog = studiolibrary.WelcomeDialog(studiolibrary.mayaWindow())
    dialog.ui.heading.setText('Welcome')
    dialog.ui.content.setText('Before you get started please choose a root folder for storing the data. A network folder is recommended for sharing within a studio.')
    dialog.exec_()
    path = dialog.path()
    if not os.path.exists(path):
        raise Exception('Cannot find the root folder path \'%s\'.             To set the root folder please use studiolibrary.main(root="C:/path")' % path)
    return path


def application():
    """
    @rtype: QtCore.QApplication
    """
    import studiolibrary
    return studiolibrary.__application


def mainWindows():
    """
    @rtype: list[MainWindow]
    """
    import studiolibrary
    return studiolibrary.__windows


def removeWindow(name):
    """
    @type name: str
    """
    import studiolibrary
    del studiolibrary.mainWindows()[name]


def libraries():
    """
    @rtype: list[str]
    """
    results = []
    path = os.path.join(SETTINGS_DIRNAME, 'studiolibrary', '.settings', 'Library')
    if os.path.exists(path):
        for d in os.listdir(path):
            results.append(d.replace('.dict', ''))

    return results


def image(name, extension = 'png'):
    """
    @type name: str
    @type name: extension: str
    @rtype: str
    """
    return dirname() + '/ui/images/' + name + '.' + extension


def pixmap(path, color = None):
    """
    @type path: str
    @type color: QtGui.QColor
    @rtype: QtGui.QPixmap
    """
    if not os.path.exists(path):
        path = image(path)
    if color:
        alpha = QtGui.QPixmap(path)
        pixmap = QtGui.QPixmap(alpha.size())
        pixmap.fill(color)
        pixmap.setAlphaChannel(alpha.alphaChannel())
        return pixmap
    return QtGui.QPixmap(path)


def icon(path, color = None, ignoreOverride = False):
    """
    @type path: str
    @type color: QtGui.QColor
    @type ignoreOverride: bool
    @rtype: QtGui.QIcon
    """
    icon = QtGui.QIcon(pixmap(path, color=color))
    if not ignoreOverride:
        p = pixmap(path, color=QtGui.QColor(222, 222, 222, 155))
        icon.addPixmap(p, QtGui.QIcon.Disabled, QtGui.QIcon.On)
        p = pixmap(path, color=QtGui.QColor(222, 222, 222, 155))
        icon.addPixmap(p, QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        p = pixmap(path, color=QtGui.QColor(0, 0, 0, 245))
        icon.addPixmap(p, QtGui.QIcon.Active, QtGui.QIcon.On)
        p = pixmap(path, color=QtGui.QColor(0, 0, 0, 245))
        icon.addPixmap(p, QtGui.QIcon.Active, QtGui.QIcon.Off)
        p = pixmap(path, color=QtGui.QColor(0, 0, 0, 245))
        icon.addPixmap(p, QtGui.QIcon.Selected, QtGui.QIcon.On)
        p = pixmap(path, color=QtGui.QColor(0, 0, 0, 245))
        icon.addPixmap(p, QtGui.QIcon.Selected, QtGui.QIcon.Off)
    return icon


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
    import studiolibrary
    studiolibrary.main(name=name, plugins=plugins)


if __name__ == '__main__':
    loadFromCommand()
else:
    print '\n-------------------------------\nStudio Library is a free python script for managing poses and animation in Maya.\nComments, suggestions and bug reports are welcome.\n\nVersion: %s\n\nwww.studiolibrary.com\nkurt.rathjen@gmail.com\n--------------------------------\n' % version()
