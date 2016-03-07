#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\core\utils.py
import re
import os
import platform
import subprocess
RE_VALIDATE_PATH = re.compile('^[\\\\.:/\\sA-Za-z0-9_-]*$')
RE_VALIDATE_STRING = re.compile('^[\\sA-Za-z0-9_-]+$')

class StudioLibraryError(Exception):
    """Base exception for any studio library errors."""
    pass


class ValidatePathError(StudioLibraryError):
    """Raised when a path has invalid characters."""
    pass


class ValidateStringError(StudioLibraryError):
    """Raised when a string has invalid characters."""
    pass


class Direction:
    Up = 'up'
    Down = 'down'


class SortOption:
    Name = 'name'
    Ordered = 'ordered'
    Modified = 'modified'


def system():
    """
    :rtype: str
    """
    return platform.system().lower()


def validatePath(path):
    """
    :type path: str
    :raise ValidatePathError
    """
    if not RE_VALIDATE_PATH.match(path):
        msg = 'Invalid characters in path "{0}"! Please only use letters, numbers and forward slashes.'
        msg = msg.format(path)
        raise ValidatePathError(msg)


def validateString(text):
    """
    :type text: str
    :raise ValidateStringError
    """
    if not RE_VALIDATE_STRING.match(text):
        msg = 'Invalid string "{0}"! Please only use letters and numbers'
        msg = msg.format(str(text))
        raise ValidateStringError(msg)


def generateUniqueName(name, names, attempts = 1000):
    """
    :type name: str
    :type names: list[str]
    :type attempts: int
    :rtype: str
    """
    for i in range(1, attempts):
        result = name + str(i)
        if result not in names:
            return result

    msg = "Cannot generate unique name '{0}'".format(name)
    raise StudioLibraryError(msg)


def openLocation(path):
    """
    :type path: str
    :rtype: None
    """
    if isLinux():
        os.system('konqueror "%s"&' % path)
    elif isWindows():
        os.startfile('%s' % path)
    elif isMac():
        subprocess.call(['open', '-R', path])


def isMaya():
    """
    :rtype: bool
    """
    try:
        import maya.cmds
        maya.cmds.about(batch=True)
        return True
    except ImportError:
        return False


def isMac():
    """
    :rtype: bool
    """
    return system().startswith('mac') or system().startswith('os') or system().startswith('darwin')


def isWindows():
    """
    :rtype: bool
    """
    return system().startswith('win')


def isLinux():
    """
    :rtype: bool
    """
    return system().startswith('lin')


def user():
    """
    :rtype: str
    """
    import getpass
    return getpass.getuser().lower()


def copyPath(srcPath, dstPath):
    """
    :type srcPath: str
    :type dstPath: str
    :rtype: None
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
    :type path: str
    :rtype: list[str]
    """
    path = path.replace('\\', '/')
    filename, extension = os.path.splitext(path)
    return (os.path.dirname(filename), os.path.basename(filename), extension)


def listToString(data):
    """
    :type data: list[]
    :rtype: str
    """
    data = str(data).replace('[', '').replace(']', '')
    data = data.replace("'", '').replace('"', '')
    return data


def stringToList(data):
    """
    :type data: str
    :rtype: list[]
    """
    data = '["' + str(data) + '"]'
    data = data.replace(' ', '')
    data = data.replace(',', '","')
    return eval(data)


def walk(path, separator = '/', direction = Direction.Down):
    """
    :type path: str
    :type separator: str
    :type direction: Direction
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


def listPaths(path):
    """
    :type path: str
    :rtype: list[str]
    """
    results = []
    for name in os.listdir(path):
        value = path + '/' + name
        results.append(value)

    return results


def findPaths(dirname, search, direction = Direction.Up):
    """
    :type dirname: str
    :type search: str
    :type direction: Direction
    :rtype: dict[str]
    """
    results = []
    for path in walk(dirname, direction=direction):
        for filename in os.listdir(path):
            if search is None or search in filename:
                value = path + '/' + filename
                results.append(value)

    return results


def downloadUrl(url, destination = None):
    """
    :type url: str
    :type destination: str
    :rtype : str
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
        except Exception:
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
    :type t: str
    :rtype: str
    """
    return timeDiff(t)


def timeDiff(t = False):
    """
    :type t: str
    :rtype: str
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
