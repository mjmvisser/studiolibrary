#Embedded file name: /automount/sun-01/home/mvisser/workspace/studiolibrary/other/utils.py
"""
"""
import os
import sys
import platform

class Direction:
    Up = 'up'
    Down = 'down'


class SortOption:
    Name = 'name'
    Ordered = 'ordered'
    Modified = 'modified'


def system():
    """
    @rtype: str
    """
    return platform.system().lower()


def addSysPath(path):
    """
    @type path: str
    """
    if os.path.exists(path) and path not in sys.path:
        print "Adding '%s' to the sys.path" % path
        sys.path.append(path)


def mayaWindow():
    """
    @rtype: QtCore.QObject
    """
    try:
        from PySide import QtGui
        from PySide import QtCore
    except ImportError:
        from PyQt4 import QtGui
        from PyQt4 import QtCore

    try:
        import maya.OpenMayaUI as mui
        import sip
        ptr = mui.MQtUtil.mainWindow()
        return sip.wrapinstance(long(ptr), QtCore.QObject)
    except:
        print 'Warning: Cannot find a maya window.'


def isMaya():
    """
    @rtype: bool
    """
    try:
        import maya.cmds
        maya.cmds.about(batch=True)
        return True
    except ImportError:
        return False


def isMac():
    """
    @rtype: bool
    """
    return system().startswith('mac') or system().startswith('os') or system().startswith('darwin')


def isWindows():
    """
    @rtype: bool
    """
    return system().startswith('win')


def isLinux():
    """
    @rtype: bool
    """
    return system().startswith('lin')


def user():
    """
    @rtype: str
    """
    import getpass
    return getpass.getuser().lower()


def copyPath(srcPath, dstPath):
    """
    @type srcPath: str
    @type dstPath: str
    @rtype: None
    """
    import stat
    import shutil
    if not os.path.exists(srcPath):
        raise IOError("Path doesn't exists '%s'" % srcPath)
    if os.path.isfile(srcPath):
        shutil.copyfile(srcPath, dstPath)
    elif os.path.isdir(srcPath):
        shutil.copytree(srcPath, dstPath)
    ctime = os.stat(srcPath)[stat.ST_CTIME]
    mtime = os.stat(srcPath)[stat.ST_MTIME]
    os.utime(dstPath, (ctime, mtime))


def splitPath(path):
    """
    @type path:
    @rtype:
    """
    path = path.replace('\\', '/')
    filename, extension = os.path.splitext(path)
    return (os.path.dirname(filename), os.path.basename(filename), extension)


def listToString(data):
    """
    @type data:
    @rtype:
    """
    data = str(data).replace('[', '').replace(']', '')
    data = data.replace("'", '').replace('"', '')
    return data


def stringToList(data):
    """
    @type data:
    @rtype:
    """
    data = '["' + str(data) + '"]'
    data = data.replace(' ', '')
    data = data.replace(',', '","')
    return eval(data)


def walk(path, separator = '/', direction = Direction.Down):
    """
    @param path: str
    @param separator: str
    """
    if os.path.isfile(path):
        path = os.path.dirname(path)
    if not path.endswith(separator):
        path += separator
    folders = path.split(separator)
    for i, folder in enumerate(folders):
        if direction == Direction.Up:
            result = separator.join(folders[:i * -1])
        elif direction == Direction.Down:
            result = separator.join(folders[:i - 1])
        if result and os.path.exists(result):
            yield result


def findPaths(dirname, extension, direction = Direction.Up):
    """
    @type dirname: str
    @rtype:  dict[str]
    """
    results = []
    for path in walk(dirname, direction=direction):
        for filename in [ filename for filename in os.listdir(path) if extension in filename ]:
            value = path + '/' + filename
            results.append(value)

    return results


def findRecords(dirname, extension, direction = Direction.Down):
    """
    @type dirname: str
    @rtype:  dict[str]
    """
    results = {}
    for path in findPaths(dirname, extension, direction=direction):
        folder = os.path.dirname(path)
        filename = os.path.basename(path)
        key = os.path.basename(folder) + ': ' + filename.replace(extension, '')
        value = path
        results[key] = value

    return results


def findRecordsFromSelectedFolders(window, extension, direction = Direction.Down):
    """
    @rtype: dict[str]
    """
    folders = window.selectedFolders()
    results = {}
    for folder in folders:
        results.update(findRecords(folder.dirname(), extension, direction=direction))

    return results


def downloadUrl(url, destination = None):
    """
    @type url: str
    @type destination: str
    @rtype : str
    """
    try:
        if destination:
            try:
                f = open(destination, 'w')
                f.close()
            except:
                print 'Studio Library: The current user does not have permission for the directory %s' % destination
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


def timeAgo(t):
    """
    @type t: str
    @rtype: str
    """
    return timeDiff(t)


def timeDiff(t = False):
    """
    @type t: str
    @rtype: str
    """
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


if __name__ == '__main__':
    for key, value in findRecords('C:/Users/hovel/Dropbox/libraries/demo/Malcolm/Face', '.pose').items():
        print key, value
