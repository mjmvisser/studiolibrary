#Embedded file name: C:/Users/hovel/Dropbox/packages/studioLibrary/1.5.8/build27/studioLibrary\__init__.py
"""
Released subject to the BSD License
Please visit http://www.voidspace.org.uk/python/license.shtml

Contact: kurt.rathjen@gmail.com
Comments, suggestions and bug reports are welcome.
Copyright (c) 2014, Kurt Rathjen, All rights reserved.

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
import time
import shutil
import urllib2
import getpass
import platform
import traceback
__version__ = '1.5.8'
__system__ = platform.system().lower()
__windows = {}
__application = None
__plugins = {}
__scriptJob = None
Name = 'name'
Ordered = 'ordered'
Modified = 'modified'
DEFAULT_PLUGINS = ['posePlugin',
 'animationPlugin',
 'mirrorTablePlugin',
 'selectionSetPlugin']
SETTINGS_DIRNAME = os.getenv('APPDATA') or os.getenv('HOME')

def version():
    return __version__


def dirname():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(unicode(os.path.abspath(__file__), encoding)).replace('\\', '/')


def setDebug(enable):
    import mutils
    mutils.setDebug(enable)


packages = dirname() + '/site-packages/'
if os.path.exists(packages) and packages not in sys.path:
    print "Adding '%s' to the sys.path" % packages
    sys.path.append(packages)
try:
    import mutils
except ImportError as msg:
    print msg

def user():
    import getpass
    return getpass.getuser().lower()


def stringToList(text):
    text = text.replace(' ', '')
    text = "['" + text.replace(',', "','") + "']"
    text = eval(text)
    return list(text)


def listToString(text):
    replace = re.compile("[u'|'|\\[|\\]]")
    text = replace.sub('', str(text))
    return str(text)


def isVersionDirname():
    return '/studioLibrary/versions/' in dirname()


def defaultDirname():
    path = dirname()
    if isVersionDirname():
        return os.path.dirname(os.path.dirname(os.path.dirname(path)))
    return path


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


def isPySide():
    return _isPySide


def getTempDir():
    """
    :rtype : str
    """
    return tempDir(make=False, clean=False)


def makeTempDir(subdir = ''):
    """
    :rtype : str
    """
    return tempDir(make=True, clean=False, subdir=subdir)


def cleanTempDir(subdir = ''):
    """
    :rtype : str
    """
    return tempDir(make=False, clean=True, subdir=subdir)


def tempDir(make = True, clean = False, subdir = ''):
    """
    :rtype : str
    """
    import tempfile
    path = os.path.join(tempfile.gettempdir(), 'studioLibrary', user(), subdir)
    if os.path.exists(path) and clean:
        import shutil
        shutil.rmtree(path)
    if not os.path.exists(path) and make:
        os.makedirs(path)
    return path


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
        mayaVersion = '2012x64'
        if mutils.isMaya():
            import maya.cmds
            mayaVersion = maya.cmds.about(version=True)
            if '2011' in mayaVersion:
                mayaVersion = '2011x64'
            elif '2012' in mayaVersion:
                mayaVersion = '2012x64'
            elif '2013' in mayaVersion:
                mayaVersion = '2013x64'
        packages = dirname() + '/site-packages/' + mayaVersion
        if os.path.exists(packages) and packages not in sys.path:
            print "Adding '%s' to the sys.path" % packages
            sys.path.append(packages)
        try:
            from PySide import QtGui
            from PySide import QtCore
            _isPySide = True
        except ImportError:
            try:
                from PyQt4 import QtGui
                from PyQt4 import QtCore
            except:
                try:
                    import maya.cmds
                    msg = '\nTraceback:\n\n    Cannot find PyQt for:\n    Maya Version: %s\n    PyQt Path: %s\n    Studio Library Path: %s\n            ' % (maya.cmds.about(version=True), packages, os.path.dirname(__file__))
                    print msg
                    raise
                except:
                    raise

def stableVersion():
    try:
        data = downloadUrl('http://dl.dropbox.com/u/28655980/studioLibrary/studioLibrary.txt')
        if data:
            if data.startswith('{'):
                data = eval(data.strip(), {})
                return data.get('version', version())
    except:
        raise


def downloadUrl(url, destination = None):
    try:
        if destination:
            try:
                f = open(destination, 'w')
                f.close()
            except:
                print 'studioLibrary: The current user does not have permission for the directory %s' % destination
                return

        try:
            import urllib2
            f = urllib2.urlopen(url, None, 2.0)
        except:
            return

        data = f.read()
        if destination:
            f = open(destination, 'wb')
            f.write(data)
            f.close()
        return data
    except:
        raise


def versionsDirname():
    return defaultDirname() + '/versions'


def versionPath(version):
    return versionsDirname() + '/' + version


def isUpdateAvailable():
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
    import studioLibrary
    dialog = studioLibrary.WelcomeDialog(studioLibrary.mayaWindow())
    dialog.ui.heading.setText('Welcome')
    dialog.ui.content.setText('Before you get started please choose a root folder for storing the data. A network folder is recommended for sharing within a studio.')
    dialog.exec_()
    path = dialog.path()
    if not os.path.exists(path):
        raise Exception('Cannot find the root folder path \'%s\'.             To set the root folder please use studioLibrary.main(root="C:/path")' % path)
    return path


class Analytics():

    def __init__(self, name = 'StudioLibrary', version = version()):
        self.name = name
        self.version = version

    def logEvent(self, name, value):
        try:
            url = self._url + '&t=event&ec=' + name + '&ea=' + value
            #self.send(url)
        except Exception:
            pass

    def logScreen(self, name):
        try:
            url = self._url + '&t=appview&cd=' + name
            #self.send(url)
        except Exception:
            pass

    @property
    def cid(self):
        return getpass.getuser() + '-' + platform.node()

    @property
    def _url(self):
        url = 'http://www.google-analytics.com/collect?v=1&ul=en-us&a=448166238&_u=.sB&_v=ma1b3&qt=2500&z=185&tid=UA-50172384-1'
        return url + '&an=' + self.name + '&cid=' + self.cid + '&av=' + self.version

    @staticmethod
    def send(url):
        import threading
        t = threading.Thread(target=Analytics._send, args=(url,))
        t.start()

    @staticmethod
    def _send(url):
        try:
            url = url.replace(' ', '')
            f = urllib2.urlopen(url, None, 1.0)
        except Exception as e:
            pass


def main(name = None, show=True, **kwargs):
    import mutils
    import studioLibrary
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
    _plugins.append('lockPlugin')
    kwargs['plugins'] = _plugins
    if not mutils.isMaya():
        studioLibrary.__application = QtGui.QApplication(sys.argv)
    else:
        import maya.cmds
        if not studioLibrary.__scriptJob:
            studioLibrary.__scriptJob = maya.cmds.scriptJob(event=['quitApplication', 'import studioLibrary;\nfor window in studioLibrary.mainWindows().values():\n\twindow.saveSettings()'])
    if not root:
        root = LibrarySettings(name).get('kwargs', None).get('root', None)
        if not root and show:
            root = showWelcomeDialog()
            kwargs['root'] = root
    if name not in studioLibrary.mainWindows():
        w = studioLibrary.MainWindow(name=name, **kwargs)
        studioLibrary.mainWindows().setdefault(name, w)
    elif show:
        w = studioLibrary.mainWindows()[name]
        w.loadLibrary(name, kwargs)
        w.close()
    if show:
        w.showNormal()
        w.raiseWindow()
    if not mutils.isMaya():
        sys.exit(studioLibrary.__application.exec_())
    return studioLibrary.mainWindows().get(name, None)


def application():
    import studioLibrary
    return studioLibrary.__application


def mainWindows():
    import studioLibrary
    return studioLibrary.__windows


def removeWindow(name):
    import studioLibrary
    del studioLibrary.mainWindows()[name]


def mayaWindow():
    try:
        import maya.OpenMayaUI as mui
        import sip
        ptr = mui.MQtUtil.mainWindow()
        return sip.wrapinstance(long(ptr), QtCore.QObject)
    except:
        pass


def isMac():
    return __system__.startswith('mac') or __system__.startswith('os') or __system__.startswith('darwin')


def isWindows():
    return __system__.startswith('win')


def isLinux():
    return __system__.startswith('lin')


def copyPath(source, destination):
    import shutil
    if not os.path.exists(source):
        raise IOError("Path doesn't exists '%s'" % source)
    if os.path.isfile(source):
        shutil.copyfile(source, destination)
    elif os.path.isdir(source):
        shutil.copytree(source, destination)
    import stat
    ctime = os.stat(source)[stat.ST_CTIME]
    mtime = os.stat(source)[stat.ST_MTIME]
    os.utime(destination, (ctime, mtime))


def walklevel(dirname, level = 5):
    dirname = dirname.rstrip(os.path.sep)
    assert os.path.isdir(dirname)
    num_sep = dirname.count(os.path.sep)
    for root, dirs, files in os.walk(dirname):
        yield (root, dirs, files)
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def find(dirname, pattern = None, deleted = False):
    result = []
    pattern = re.compile(pattern)
    for d, dirs, files in walklevel(dirname):
        d = d.replace('\\', '/')
        if not pattern or pattern.search(d):
            result.append(d)
        for filename in files:
            path = d + '/' + filename
            if not deleted and '.deleted' in path:
                continue
            if not pattern or pattern.search(path):
                result.append(path)

    return result


def folders():
    return [ Folder(path) for path in find('folder.txt') ]


def splitPath(path):
    path = path.replace('\\', '/')
    filename, extension = os.path.splitext(path)
    return (os.path.dirname(filename), os.path.basename(filename), extension)


def image(name, extension = 'png'):
    return dirname() + '/ui/images/' + name + '.' + extension


def pixmap(path, color = None):
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


def timeAgo(t):
    return timeDiff(t)


def timeDiff(t = False):
    if isinstance(t, str):
        t = int(t.split('.')[0])
    from datetime import datetime
    now = datetime.now()
    if type(t) is int:
        diff = now - datetime.fromtimestamp(t)
    elif isinstance(t, datetime):
        diff = now - t
    else:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days
    if day_diff < 0:
        return ''
    if day_diff == 0:
        if second_diff < 10:
            return 'just now'
        if second_diff < 60:
            return str(second_diff) + ' seconds ago'
        if second_diff < 120:
            return 'a minute ago'
        if second_diff < 3600:
            return str(second_diff / 60) + ' minutes ago'
        if second_diff < 7200:
            return 'an hour ago'
        if second_diff < 86400:
            return str(second_diff / 3600) + ' hours ago'
    if day_diff == 1:
        return 'Yesterday'
    if day_diff < 7:
        return str(day_diff) + ' days ago'
    if day_diff < 31:
        v = day_diff / 7
        if v == 1:
            return str(v) + ' week ago'
        return str(day_diff / 7) + ' weeks ago'
    if day_diff < 365:
        v = day_diff / 30
        if v == 1:
            return str(v) + ' month ago'
        return str(v) + ' months ago'
    v = day_diff / 365
    if v == 1:
        return str(v) + ' year ago'
    return str(v) + ' years ago'


def plugin(name):
    import studioLibrary
    return studioLibrary.__plugins.get(name, None)


def loadedPlugins():
    import studioLibrary
    return studioLibrary.__plugins


def importModule(path):
    import imp
    import studioLibrary
    dirname, basename, extension = splitPath(path)
    if basename in dir(studioLibrary):
        return eval('studioLibrary.' + basename)
    else:
        if not os.path.exists(path):
            path = path.replace('.py', '.pyc')
        module = imp.load_source('studioLibrary.' + basename, path)
        return module


def loadPlugins(plugins, parent = None):
    for path in plugins:
        loadPlugin(path, parent)


def loadPlugin(path, parent = None):
    import studioLibrary
    path = path.replace('\\', '/')
    import imp
    name = path
    if '/' not in path:
        path = studioLibrary.dirname() + '/plugins/%s.py' % path
    if os.path.exists(path):
        dirname, basename, extension = splitPath(path)
        module = imp.load_source(basename, path)
    else:
        try:
            exec 'import studioLibrary.plugins.' + name
            module = eval('studioLibrary.plugins.' + name)
        except:
            exec 'import ' + name
            module = eval(name)

    plugin = module.Plugin(parent)
    if not parent:
        studioLibrary.__plugins.setdefault(plugin.name(), plugin)
    plugin.setPath(path)
    plugin.load()
    studioLibrary.__plugins.setdefault(plugin.name(), plugin)
    return plugin


def unloadPlugin(plugin):
    import studioLibrary
    plugin.unload()
    if plugin.name() in studioLibrary.__plugins:
        del studioLibrary.__plugins[plugin.name()]


def read(path):
    results = {}
    f = open(path, 'r')
    data = f.read().strip()
    f.close()
    try:
        data = eval(data, {})
        results.update(data)
    except Exception as e:
        results = {}
        print "Cannot evaluate meta file '%s'." % path
        import traceback
        traceback.print_exc()
        results['errors'] = traceback.format_exc() + str(e)

    return results


class DictFile(dict):

    def __init__(self, path, read = True, **kwargs):
        super(DictFile, self).__init__(**kwargs)
        self.setPath(str(path))
        if read and os.path.exists(self.path()):
            self.read()

    def prettyPrint(self):
        print '------ %s ------' % self.name()
        import json
        print json.dumps(self, indent=2)
        print '----------------\n'

    def delete(self):
        if self.exists():
            os.remove(self.path())

    def mkdir(self):
        dirname = os.path.dirname(self.path())
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def errors(self):
        return self.get('errors', '')

    def exists(self):
        if os.path.exists(self.path()):
            return True
        return False

    def description(self):
        return self.get('description', '')

    def setDescription(self, value):
        self.set('description', value)

    def set(self, key, value):
        self[key] = value

    def setOwner(self, value):
        self.set('owner', value)

    def owner(self):
        return self.get('owner', '')

    def mtime(self):
        return self.get('mtime', None)

    def setMtime(self, value):
        self.set('mtime', value)

    def setCtime(self, value):
        self.set('ctime', value)

    def ctime(self):
        """
        
        :rtype : str
        """
        return self.get('ctime', None)

    def setPath(self, path):
        self['_path'] = path
        self._path = path.replace('\\', '/')

    def path(self):
        return self._path

    def dirname(self):
        return os.path.dirname(self.path())

    def name(self):
        return os.path.basename(self.path())

    def read(self):
        data = read(self.path())
        self.update(data)
        return self

    def save(self):
        t = str(time.time()).split('.')[0]
        if not self.ctime():
            self.setCtime(t)
        self.setMtime(t)
        if not self.owner():
            self.setOwner(user())
        dirname = os.path.dirname(self.path())
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        data = dict()
        data['errors'] = ['An error has occurred when evaluating string: %s' % str(self)]
        try:
            data = eval(str(self), {})
            if 'errors' in data:
                del data['errors']
            path = None
            if '_path' in data:
                path = self['_path']
                del self['_path']
            f = open(self.path(), 'w')
            f.write(str(self))
            f.close()
            if path:
                self['_path'] = path
        except:
            import traceback
            data['errors'].append(traceback.format_exc())
            raise Exception('Cannot save! Invalid data found in dict.')


def libraries():
    results = []
    path = os.path.join(SETTINGS_DIRNAME, 'studioLibrary', '.settings', 'Library')
    if os.path.exists(path):
        for dirname in os.listdir(path):
            results.append(dirname.replace('.dict', ''))

    return results


class Settings(DictFile):

    def __init__(self, scope, name, parent = None):
        self._name = name
        self._scope = scope
        DictFile.__init__(self, '')

    def save(self):
        DictFile.save(self)

    def path(self):
        if not self._path:
            self._path = os.path.join(SETTINGS_DIRNAME, 'studioLibrary', '.settings', self._scope, self._name + '.dict')
        return self._path


class PluginSettings(Settings):

    def __init__(self, name):
        Settings.__init__(self, 'Plugins', name)


class Folder(DictFile):

    def __init__(self, path, parent = None, read = True):
        DictFile.__init__(self, path, read=read)
        self._pixmap = None
        self._parent = None
        self.setParent(parent)

    def reset(self):
        if 'bold' in self:
            del self['bold']
        if 'color' in self:
            del self['color']
        if 'icon' in self:
            del self['icon']
        if 'iconVisibility' in self:
            del self['iconVisibility']
        self.save()

    def changeIcon(self):
        path = str(QtGui.QFileDialog.getOpenFileName(self.parent(), 'Select an image', '', '*.png'))
        path = path.replace('\\', '/')
        if path:
            self.setIcon(path)

    def setColor(self, color):
        if isinstance(color, QtGui.QColor):
            color = 'rgb(%d, %d, %d, %d)' % color.getRgb()
        self.set('color', color)
        self.save()

    def color(self):
        color = self.get('color', None)
        if color:
            r, g, b, a = eval(color.replace('rgb', ''), {})
            return QtGui.QColor(r, g, b, a)
        else:
            return

    def deletable(self):
        return self.get('deletable', True)

    def renameable(self):
        return self.get('renameable', True)

    def setIconVisibility(self, value):
        self.set('iconVisibility', value)
        self.save()

    def iconVisibility(self):
        return self.get('iconVisibility', True)

    def setPath(self, path):
        if not path.endswith('.dict'):
            path += '/.studioLibrary/folder.dict'
        DictFile.setPath(self, path)

    def setBold(self, value, save = True):
        self.set('bold', value)
        if save:
            self.save()

    def bold(self):
        return self.get('bold', False)

    def dirname(self):
        return os.path.dirname(os.path.dirname(self.path()))

    def name(self):
        return os.path.basename(self.dirname())

    def window(self):
        """
        
        :rtype : MainWindow
        """
        if self.parent():
            return self.parent().window()

    def setParent(self, parent):
        self._parent = parent

    def parent(self):
        return self._parent

    def setPixmap(self, pixmap):
        self._pixmap = pixmap

    def setIcon(self, icon):
        self.set('icon', icon)
        self.save()

    def icon(self):
        icon = self.get('icon', None)
        if not icon:
            return image('folder')
        return icon

    def pixmap(self):
        if not self.iconVisibility():
            return pixmap('')
        if not self._pixmap:
            icon = self.icon()
            color = self.color()
            if icon == image('folder') and not color:
                color = QtGui.QColor(250, 250, 250, 200)
            self._pixmap = pixmap(icon, color=color)
        return self._pixmap

    def openLocation(self):
        path = self.dirname()
        if isLinux():
            os.system('konqueror "%s"&' % path)
        elif isWindows():
            os.startfile('%s' % path)
        elif isMac():
            import subprocess
            subprocess.call(['open', '-R', path])

    def delete(self):
        if not self.deletable():
            raise Exception('Item is not deletable!')
        nextVersion = self.versionPath(self.nextVersion())
        if nextVersion and not os.path.exists(os.path.dirname(nextVersion)):
            os.makedirs(os.path.dirname(nextVersion))
        os.rename(self.dirname(), nextVersion)

    def createNewVersion(self):
        nextVersion = self.nextVersion()
        if not os.path.exists(os.path.dirname(nextVersion)):
            os.mkdir(os.path.dirname(nextVersion))
        shutil.copytree(self.dirname(), nextVersion)

    def retire(self):
        self.delete()

    def versions(self, path = False):
        dirname = os.path.dirname(self.dirname()) + '/.studioLibrary/' + self.name()
        if os.path.exists(dirname):
            if path:
                return [ dirname + '/' + name for name in sorted(os.listdir(dirname)) ]
            else:
                match = re.compile('[.][0-9]+')
                versions = []
                for name in sorted(os.listdir(dirname)):
                    v = match.search(name)
                    if v:
                        versions.append(int(v.group(0)[1:]))

                return versions
        else:
            return []

    def lastVersion(self, path = False):
        versions = self.versions(path=path)
        if versions:
            return str(self.versions()[-1]).zfill(4)
        return '0000'

    def versionDirname(self):
        return os.path.dirname(self.dirname()) + '/.studioLibrary/' + self.name() + '/' + self.name()

    def versionPath(self, version):
        dirname, basename, extension = splitPath(self.versionDirname())
        return dirname + '/' + basename + '.' + str(version) + extension

    def nextVersion(self):
        latest = int(self.lastVersion())
        latest += 1
        return str(latest).zfill(4)

    def restore(self):
        name = '.'.join(self.name().split('.')[:-2])
        self.rename(name, save=False)

    def rename(self, path, save = True, force = False):
        if not self.renameable():
            raise Exception('Item is not renameable!')
        path = path.replace('\\', '/')
        if '/' not in path:
            path = os.path.dirname(self.dirname()) + '/' + path
        if os.path.exists(path):
            raise Exception('Cannot save over an existing record.')
        if not os.path.exists(self.dirname()):
            raise Exception("The system cannot find the path specified '%s'." % self.dirname())
        if not os.path.exists(os.path.dirname(path)) and force:
            os.mkdir(os.path.dirname(path))
        if not os.path.exists(os.path.dirname(path)):
            raise Exception("The system cannot find the path specified '%s'." % path)
        try:
            os.rename(self.dirname(), path)
            self.setPath(path)
            if save:
                self.save()
        except:
            if self.window():
                self.window().setError('An error has occurred while renaming! Please check the traceback for more details.')
            raise

    def isDeleted(self):
        if self.name().endswith('.deleted'):
            return True
        return False

    def setOrder(self, names):
        dirname = self.dirname() + '/.studioLibrary'
        path = dirname + '/order.list'
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        f = open(path, 'w')
        f.write(str(names))
        f.close()

    def order(self):
        path = self.dirname() + '/.studioLibrary/order.list'
        if os.path.exists(path):
            f = open(path, 'r')
            data = f.read()
            f.close()
            if data.strip():
                return eval(data, {})
        return []

    def contextMenu(self, menu, folders):
        if self.window().isLocked():
            return
        menu.addMenu(self.window().ui.newMenu)
        if len(folders) == 1:
            menu.addMenu(self.window().ui.editFolderMenu)
        separator = QtGui.QAction('Separator1', menu)
        separator.setSeparator(True)
        menu.addAction(separator)
        settingsMenu = QtGui.QMenu(self.parent())
        settingsMenu.setIcon(icon('settings14'))
        settingsMenu.setTitle('Settings')
        action = QtGui.QAction('Show icon', settingsMenu)
        action.setCheckable(True)
        action.setChecked(self.iconVisibility())
        action.connect(action, QtCore.SIGNAL('triggered(bool)'), lambda v, self = self: self.setIconVisibility(v))
        settingsMenu.addAction(action)
        action = QtGui.QAction('Show bold', settingsMenu)
        action.setCheckable(True)
        action.setChecked(self.bold())
        action.connect(action, QtCore.SIGNAL('triggered(bool)'), lambda v, self = self: self.setBold(v))
        settingsMenu.addAction(action)
        separator = QtGui.QAction('Separator2', settingsMenu)
        separator.setSeparator(True)
        settingsMenu.addAction(separator)
        action = QtGui.QAction('Change icon', settingsMenu)
        action.triggered.connect(lambda : self.changeIcon())
        settingsMenu.addAction(action)
        action = QtGui.QAction('Change color', settingsMenu)
        action.triggered.connect(lambda : self.changeColor())
        settingsMenu.addAction(action)
        separator = QtGui.QAction('Separator3', settingsMenu)
        separator.setSeparator(True)
        settingsMenu.addAction(separator)
        action = QtGui.QAction('Reset settings', settingsMenu)
        action.triggered.connect(lambda : self.reset())
        settingsMenu.addAction(action)
        menu.addMenu(settingsMenu)

    def changeColor(self):
        color = self.color()
        d = QtGui.QColorDialog(self.parent())
        d.currentColorChanged.connect(lambda v, self = self: self.setColor(v))
        d.open()
        if d.exec_():
            self.setColor(d.selectedColor())
        else:
            self.setColor(color)

    def records(self, sort = Ordered, deleted = False, parent = None):
        folder = self
        records = []
        dirname = folder.dirname()
        if parent:
            plugins = parent.window().plugins().values()
        else:
            plugins = loadedPlugins().values()
        for plugin in plugins:
            records.extend(plugin.records(folder, parent=parent))

        for name in sorted(os.listdir(dirname)):
            path = dirname + '/' + name
            for plugin in plugins:
                if plugin.match(path):
                    record = plugin.record(self, name=name, plugin=plugin, parent=parent)
                    records.append(record)
                    break

        return self.sort(records, sort=sort)

    def sort(self, records, sort = Ordered):
        result = []
        _records = {}
        for record in records:
            if sort == Ordered:
                _records.setdefault(record.name(), record)
            elif sort == Modified:
                _records.setdefault(record.mtime() + str(id(record)), record)

        if sort == Ordered:
            order = self.order()
            for name in order:
                if name in _records:
                    result.append(_records[name])

            for name in _records:
                if name not in order and name in _records:
                    result.append(_records[name])

        elif sort == Modified:
            order = sorted(_records.keys())
            order.reverse()
            for mtime in order:
                result.append(_records[mtime])

        else:
            result = records
        return result


class Record(Folder):

    def __init__(self, folder = None, name = None, plugin = None, parent = None, data = None):
        self._rect = None
        self._index = None
        self._pixmap = None
        self._margin = 4
        self._plugin = None
        if data:
            self.setParent(parent)
            self.setPlugin(plugin)
            self.setName(name)
            self.setFolder(folder)
            Folder.__init__(self, self.path(), parent, read=False)
            self.update(data)
        else:
            self.setParent(parent)
            self.setPlugin(plugin)
            self.setName(name)
            self.setFolder(folder)
            Folder.__init__(self, self.path(), parent)

    def rename(self, path, save = True, force = False):
        path = path.replace('\\', '/')
        dirname, basename, extension = splitPath(path)
        if extension != self.plugin().extension():
            path += self.plugin().extension()
        Folder.rename(self, path, save, force)

    def setName(self, name):
        self._name = name

    def name(self):
        plugin = self.plugin()
        name = self._name
        if plugin and name:
            extension = plugin.extension()
            if name and extension not in name:
                return name + extension
        return name or ''

    def setFolder(self, folder):
        self._folder = folder

    def setPath(self, path):
        if not path.endswith('.dict') and os.path.isdir(path):
            self.setName(os.path.basename(path))
            self.setFolder(Folder(os.path.dirname(path)))
            path = self.path()
        Folder.setPath(self, path)

    def path(self):
        if self.name():
            return self.folder().dirname() + '/' + self.name() + '/.studioLibrary/record.dict'
        else:
            return ''

    def folder(self):
        return self._folder

    def setPlugin(self, plugin):
        self._plugin = plugin

    def plugin(self):
        """
        
        :rtype : Plugin
        """
        return self._plugin

    def icon(self):
        if self.errors():
            return image('pluginError')
        icon_ = self.get('icon', '') or 'thumbnail.jpg'
        icon_ = icon_.replace('DIRNAME', self.dirname())
        if '/' not in icon_:
            icon2 = self.dirname() + '/' + icon_
            return icon2
        return icon_

    def setContextMenu(self, menu):
        self.window().setContextMenu(menu)

    def pixmap(self):
        if not self.iconVisibility():
            return pixmap('')
        if not self._pixmap:
            icon = self.icon()
            if os.path.exists(icon):
                self._pixmap = pixmap(icon)
            else:
                self._pixmap = pixmap(image('thumbnail'))
        return self._pixmap

    def save(self, content = None, icon = None, version = True):
        if not content:
            content = []
        if not self.name():
            raise Exception('Cannot save record! Please set a name for the record.')
        if not self.plugin():
            raise Exception('Cannot save record! Please set a plugin for the record.')
        window = self.window()
        if window:
            folders = window.selectedFolders()
            if len(folders) != 1:
                raise Exception('Please select ONE folder.')
            self.setFolder(folders[0])
        if self.exists():
            result = window.questionDialog("The chosen name '%s' already exists!\n Would you like to create a new version?" % self.name(), 'New version')
            if result == QtGui.QMessageBox.Yes:
                self.retire()
            else:
                raise Exception("Cannot save record because record already exists! '%s'" % self.name())
        Folder.save(self)
        if icon:
            shutil.move(icon, self.icon())
        for path in content or []:
            basename = os.path.basename(path)
            destination = self.dirname() + '/' + basename
            shutil.move(path, destination)

        self.reloadRecords()
        analytics = Analytics()
        analytics.logEvent('Create', self.plugin().name())
        if window:
            selected = window.selectedRecords()
            if not selected and window.filter():
                msg = 'Successfully created! \nHowever it could not be selected \nbecause a search filter is active!'
                window.informationDialog(msg)

    def delete(self):
        Folder.delete(self)
        self.reloadRecords()

    def reloadRecords(self):
        if self.window():
            if self.window().ui.previewWidget:
                self.window().ui.previewWidget.close()
            self.window().reloadRecords()
            self.window().selectRecords([self])

    def mousePressEvent(self, event):
        self.clicked()
        self.plugin().hideInfoWidget()
        return QtGui.QListView.mousePressEvent(event._parent, event)

    def mouseReleaseEvent(self, event):
        if event._record:
            QtGui.QListView.mouseReleaseEvent(event._parent, event)

    def mouseMoveEvent(self, event):
        self.plugin().infoWindow().move(event.globalX() + 15, event.globalY() + 20)

    def mouseEnterEvent(self, event):
        self.plugin().showInfoWidget(self, wait=1500)

    def mouseLeaveEvent(self, event):
        self.plugin().hideInfoWidget()

    def keyPressEvent(self, event):
        self.plugin().hideInfoWidget()

    def keyReleaseEvent(self, event):
        self.plugin().hideInfoWidget()

    def repaint(self):
        if self.index():
            self.parent().update(self.index())

    def index(self):
        return self._index

    def clicked(self):
        self.plugin().showPreviewWidget(None, self)

    def doubleClicked(self):
        pass

    def selectionChanged(self, *args, **kwargs):
        pass

    def contextMenu(self, menu, records):
        if not self.window().isLocked():
            menu.addMenu(self.window().ui.newMenu)
            menu.addMenu(self.window().ui.editRecordMenu)
        menu.addSeparator()
        menu.addMenu(self.window().ui.sortMenu)
        menu.addMenu(self.window().ui.settingsMenu)

    def indexData(self, parent, index, role):
        """
        This method is abstract and can be re-implemented in any sub-class.
        """
        name = self.name()
        if role == QtCore.Qt.DecorationRole:
            return parent.iconSize()
        if role == QtCore.Qt.DisplayRole:
            if '.deleted' in name:
                name = name.split('.')
                name = '.'.join(name[:-2])
            if self.parent().isShowLabels() or self.window().viewMode() != QtGui.QListView.IconMode:
                return ' ' + name
            else:
                return ''

    def setRect(self, rect):
        self._rect = rect

    def setMargin(self, margin):
        self._margin = margin

    def rect(self):
        spacing = self.parent().spacing()
        padding = self._margin
        r = self._rect
        if r:
            iconMode = self.window().viewMode() == QtGui.QListView.IconMode
            if iconMode:
                if self.parent().isShowLabels():
                    margin = 13
                else:
                    margin = 0
                rect = QtCore.QRect(r.x() + spacing + padding, r.y() + spacing + padding, r.width() - (spacing + padding * 2) + 1, r.height() - (spacing + (margin + padding * 2 - 1)))
            else:
                rect = QtCore.QRect(r.x() + spacing + 2, r.y() + spacing + 2, r.height() - spacing - 2, r.height() - spacing - 3)
            return rect

    def visualRect(self):
        spacing = self.parent().spacing()
        r = self._rect
        if r:
            return QtCore.QRect(r.x() + spacing, r.y() + spacing, r.width() - spacing, r.height() - spacing)
        return self.rect()

    def paint(self, painter, option):
        painter.save()
        rect = self.rect()
        if rect:
            _isActive = False
            if option.state & QtGui.QStyle.State_Selected:
                _isActive = True
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            if _isActive:
                color = self.window().QColor()
                painter.setBrush(QtGui.QBrush(color))
            else:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 20)))
            painter.drawRect(self.visualRect())
            isListView = self.window().ui.recordsWidget.viewMode() == QtGui.QListView.ListMode
            if self.window().isShowLabels() or isListView:
                textRect = self.visualRect()
                textRect.setHeight(textRect.height() - 1)
                textRect.setLeft(textRect.left() + 2)
                textRect.setWidth(textRect.width() - 4)
                font = QtGui.QFont()
                metrics = QtGui.QFontMetrics(font)
                if isListView:
                    textRect.setLeft(textRect.left() + 25)
                if _isActive:
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
                else:
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 200)))
                if metrics.width(self.name()) < textRect.width() and not isListView:
                    painter.drawText(textRect, QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, self.name())
                else:
                    painter.drawText(textRect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom, self.name())
            pixmap = self.pixmap()
            if isinstance(pixmap, QtGui.QPixmap):
                rect = QtCore.QRect(rect.x() - 1, rect.y() - 1, rect.width() + 1, rect.height() + 1)
                painter.drawPixmap(rect, pixmap)
            if not isListView:
                pixmap = self.plugin().pixmap()
                if isinstance(pixmap, QtGui.QPixmap):
                    painter.setOpacity(0.5)
                    rect = QtCore.QRect(rect.x(), rect.y(), 13, 13)
                    painter.drawPixmap(rect, pixmap)
        painter.restore()


class TracebackWidget(QtGui.QWidget):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        import studioLibrary
        studioLibrary.loadUi(self)

    def setTraceback(self, text):
        self.ui.label.setText(text)


class Plugin(QtCore.QObject):

    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        self._loaded = False
        self._icon = ''
        self._name = None
        self._action = None
        self._pixmap = None
        self._extension = None
        self._record = Record
        self._settings = None
        self._currentRecord = None
        self._infoWidget = None
        self._editWidget = None
        self._createWidget = None
        self._previewWidget = None
        self._tracebackWidget = None
        self._infoTimer = QtCore.QTimer(self)
        self._infoTimer.setSingleShot(True)
        self.connect(self._infoTimer, QtCore.SIGNAL('timeout()'), self._showInfoWidget)

    def folderSelectionChanged(self, folder1, folder2):
        pass

    def recordSelectionChanged(self, record1, record2):
        pass

    def recordContextMenu(self, menu, records):
        for record in records:
            if isinstance(record, self._record):
                record.contextMenu(menu, records)

    def infoWindow(self):
        return self.window().ui.infoFrame

    def setInfoWidget(self, widget):
        self._infoWidget = widget

    def infoWidget(self, parent, record):
        if self._infoWidget:
            return self.loadWidget(self._infoWidget, parent, record)

    def hideInfoWidget(self):
        if self._infoWidget:
            self._infoTimer.stop()
            self._currentRecord = None
            self.parent().ui.infoFrame.hide()

    def showInfoWidget(self, record, wait = None):
        if self._infoWidget:
            self._currentRecord = record
            if wait:
                self._infoTimer.start(wait)
            else:
                self._showInfoWidget()

    def _showInfoWidget(self):
        record = self._currentRecord
        parent = self.infoWindow().ui.mainFrame
        self.deleteChildren(parent)
        widget = self.infoWidget(parent, record)
        if widget:
            width = 190
            height = 80
            if isPySide():
                self.infoWindow().setFixedWidth(width)
                self.infoWindow().setFixedHeight(height)
            else:
                widget.parent().setFixedWidth(width)
                widget.parent().setFixedHeight(height)
            self.infoWindow().show()

    def setCreateWidget(self, widget):
        self._createWidget = widget

    def createWidget(self, parent, record):
        return self.loadWidget(self._createWidget, parent, record)

    def showCreateWidget(self, record = None):
        import studioLibrary
        folders = self.window().selectedFolders()
        if not folders:
            self.window().setError('Please create or select a folder to add to.')
        elif len(folders) > 1:
            self.window().setError('Too many folders selected! Please select only one folder to add to.')
        else:
            folder, = folders
            if not record:
                record = self.record(folder, parent=self.window().ui.recordsWidget)
                record.setPlugin(self)
            _w = self.createWidget(None, record)
            self.window().setCreateWidget(_w)

    def setEditWidget(self, widget):
        self._editWidget = widget

    def editWidget(self, parent, record):
        return self.loadWidget(self._editWidget, parent, record)

    def showEditWidget(self, parent, record):
        if self._previewWidget:
            if self.window().ui.previewWidget:
                self.window().ui.previewWidget.close()
            widget = self.editWidget(parent, record)
            self.window().setPreviewWidget(widget)

    def setPreviewWidget(self, widget):
        self._previewWidget = widget

    def previewWidget(self, parent, record):
        return self.loadWidget(self._previewWidget, parent, record)

    def showPreviewWidget(self, parent, record):
        if self._previewWidget:
            if self.window().ui.previewWidget:
                self.window().ui.previewWidget.close()
            widget = self.previewWidget(parent, record)
            self.window().setPreviewWidget(widget)

    @staticmethod
    def loadWidget(widget, parent, record):
        w = None
        try:
            if record.errors():
                w = TracebackWidget(None)
                w.setTraceback(record.errors())
            elif widget:
                w = widget(None, record)
        except:
            import traceback
            msg = traceback.format_exc()
            w = TracebackWidget(None)
            w.setTraceback(msg)
            traceback.print_exc()

        if w and parent:
            parent.layout().addWidget(w)
        return w

    @staticmethod
    def deleteWidget(widget):
        widget.hide()
        widget.close()
        widget.destroy()
        del widget

    def deleteChildren(self, widget):
        for i in range(widget.layout().count()):
            child = widget.layout().itemAt(i).widget()
            widget.layout().removeWidget(child)
            self.deleteWidget(child)

    def tracebackWidget(self, parent):
        if not self._tracebackWidget:
            self._tracebackWidget = TracebackWidget(parent)
        return self._tracebackWidget

    def match(self, path):
        if path.endswith(self.extension()):
            return True
        return False

    def pixmap(self):
        if not self._pixmap:
            icon = self.icon()
            if os.path.exists(str(icon)):
                self._pixmap = QtGui.QPixmap(icon)
        return self._pixmap

    def setExtension(self, extension):
        if not extension.startswith('.'):
            extension = '.' + extension
        self._extension = extension

    def extension(self):
        """
        
        :rtype : str
        """
        if not self._extension:
            return '.' + self.name().lower()
        return self._extension

    def setRecord(self, record):
        self._record = record

    def record(self, *args, **kwargs):
        return self._record(*args, **kwargs)

    def dirname(self):
        import inspect
        return os.path.dirname(inspect.getfile(self.__class__))

    def settings(self):
        if not self._settings:
            self._settings = Settings('Plugins', self.name())
        return self._settings

    def setName(self, name):
        self._name = name

    def name(self):
        return self._name

    def records(self, folder, parent):
        return list()

    def setPath(self, path):
        self._path = path

    def path(self):
        return self._path

    def setIcon(self, icon):
        self._icon = icon

    def icon(self):
        return self._icon

    def isLoaded(self):
        return self._loaded

    def window(self):
        if self.parent():
            return self.parent().window()

    def load(self):
        if self.window():
            self._action = QtGui.QAction(icon(self.icon()), self.name(), self.window().ui.newMenu)
            self.window().connect(self._action, QtCore.SIGNAL('triggered(bool)'), self.showCreateWidget)
            self.window().ui.newMenu.addAction(self._action)

    def unload(self):
        if self.window() and self._action:
            self.window().ui.newMenu.removeAction(self._action)


def record(path, window):
    plugins = window.plugins().values()
    for plugin in plugins:
        if plugin.match(path):
            name = os.path.basename(path)
            folder = Folder(os.path.dirname(path))
            return plugin.record(folder=folder, name=name, plugin=plugin, parent=window)


try:
    from studioLibrary.gui import *
    from studioLibrary.plugins import *
except ImportError:
    sys.path.append(os.path.dirname(dirname()))
    from studioLibrary.gui import *
    from studioLibrary.plugins import *

if __name__ == '__main__':
    try:
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option('-p', '--plugins', dest='plugins', help='', metavar='PLUGINS')
        parser.add_option('-r', '--root', dest='root', help='', metavar='ROOT')
        parser.add_option('-n', '--name', dest='name', help='', metavar='NAME')
        parser.add_option('-v', '--version', dest='version', help='', metavar='VERSION')
        options, args = parser.parse_args()
        name = options.name
        print options.plugins
        plugins = eval(options.plugins)
    except:
        name = None
        plugins = None
        raise

    import studioLibrary
    studioLibrary.main(name=name, plugins=plugins)
else:
    print '\n-------------------------------\nStudio Library is a free python script for managing poses and animation in Maya.\nComments, suggestions and bug reports are welcome.\n\nVersion: %s\n\nwww.studiolibrary.com\nkurt.rathjen@gmail.com\n--------------------------------\n' % version()
