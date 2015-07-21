#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary\folder.py
"""
"""
import re
import os
import shutil
import studiolibrary
try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore

__all__ = ['Folder']

class Folder(studiolibrary.MetaFile):

    def __init__(self, path, parent = None, read = True):
        studiolibrary.MetaFile.__init__(self, path, read=read)
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
        studiolibrary.MetaFile.setPath(self, path)

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
        @rtype : MainWindow
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
            return studiolibrary.image('folder')
        return icon

    def pixmap(self):
        if not self.iconVisibility():
            return studiolibrary.pixmap('')
        if not self._pixmap:
            icon = self.icon()
            color = self.color()
            if icon == studiolibrary.image('folder') and not color:
                color = QtGui.QColor(250, 250, 250, 200)
            self._pixmap = studiolibrary.pixmap(icon, color=color)
        return self._pixmap

    def openLocation(self):
        path = self.dirname()
        if studiolibrary.isLinux():
            os.system('konqueror "%s"&' % path)
        elif studiolibrary.isWindows():
            os.startfile('%s' % path)
        elif studiolibrary.isMac():
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
        dirname, basename, extension = studiolibrary.splitPath(self.versionDirname())
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
        settingsMenu.setIcon(studiolibrary.icon('settings14'))
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

    def records(self, sort = studiolibrary.SortOption.Ordered, deleted = False, parent = None):
        folder = self
        records = []
        dirname = folder.dirname()
        if parent:
            plugins = parent.window().plugins().values()
        else:
            plugins = studiolibrary.loadedPlugins().values()
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

    def sort(self, records, sort = studiolibrary.SortOption.Ordered):
        result = []
        _records = {}
        for record in records:
            if sort == studiolibrary.SortOption.Ordered:
                _records.setdefault(record.name(), record)
            elif sort == studiolibrary.SortOption.Modified:
                _records.setdefault(record.mtime() + str(id(record)), record)

        if sort == studiolibrary.SortOption.Ordered:
            order = self.order()
            for name in order:
                if name in _records:
                    result.append(_records[name])

            for name in _records:
                if name not in order and name in _records:
                    result.append(_records[name])

        elif sort == studiolibrary.SortOption.Modified:
            order = sorted(_records.keys())
            order.reverse()
            for mtime in order:
                result.append(_records[mtime])

        else:
            result = records
        return result
