#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\core\basepath.py
import os
import logging
from . import utils
__all__ = ['PathNotFoundError', 'PathRenameError', 'BasePath']
logger = logging.getLogger(__name__)

class PathRenameError(IOError):
    """
    """
    pass


class PathNotFoundError(IOError):
    """
    """
    pass


class BasePath(object):

    def __init__(self, path):
        """
        :type path: str
        """
        path = path or ''
        path.replace('\\', '/')
        self._path = ''
        if path:
            self.setPath(path)

    def openLocation(self):
        """
        :rtype: None
        """
        path = self.path()
        utils.openLocation(path)

    def id(self):
        """
        :rtype: str
        """
        return self.path()

    def path(self):
        """
        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        :type path: str
        """
        self._path = path

    def exists(self):
        """
        :rtype: bool
        """
        return os.path.exists(self.path())

    def delete(self):
        """
        :rtype: None
        """
        if self.exists():
            os.remove(self.path())

    def extension(self):
        """
        :rtype: str
        """
        _, extension = os.path.splitext(self.path())
        return extension

    def dirname(self):
        """
        :rtype: str
        """
        return os.path.dirname(self.path())

    def isFile(self):
        """
        :rtype: bool
        """
        return os.path.isfile(self.path())

    def isFolder(self):
        """
        :rtype: bool
        """
        return os.path.isdir(self.path())

    def name(self):
        """
        :rtype: str
        """
        return os.path.basename(self.path())

    def size(self):
        """
        :rtype: float
        """
        key = 'size'
        result = self.get(key, None)
        if result is None:
            result = '%.2f' % (os.path.getsize(self.path()) / 1048576.0)
            self.set(key, result)
        return self.get(key, '')

    def mtime(self):
        """
        :rtype: float
        """
        key = 'mtime'
        result = self.get(key, None)
        if result is None:
            result = os.path.getmtime(self.path())
            self.set(key, result)
        return self.get(key, '')

    def ctime(self):
        """
        :rtype: float
        """
        key = 'ctime'
        result = self.get(key, None)
        if result is None:
            result = os.path.getctime(self.path())
            self.set(key, result)
        return self.get(key, '')

    def mkdir(self):
        """
        :rtype: None
        """
        if not os.path.exists(self.dirname()):
            os.makedirs(self.dirname())

    def rename(self, name, extension = None, force = False):
        """
        :type name: str
        :type force: bool
        :rtype: None
        """
        dst = name
        src = self.path()
        src = src.replace('\\', '/')
        dst = dst.replace('\\', '/')
        if '/' not in name:
            dst = self.dirname() + '/' + name
        if extension and extension not in name:
            dst += extension
        logger.debug('Renaming: %s => %s' % (src, dst))
        if src == dst and not force:
            raise PathRenameError('The source path and destination path are the same. %s' % src)
        if os.path.exists(dst) and not force:
            raise PathRenameError("Cannot save over an existing path '%s'" % dst)
        if not os.path.exists(self.dirname()):
            raise PathRenameError("The system cannot find the specified path '%s'." % self.dirname())
        if not os.path.exists(os.path.dirname(dst)) and force:
            os.mkdir(os.path.dirname(dst))
        if not os.path.exists(src):
            raise PathRenameError('The system cannot find the specified path %s' % src)
        os.rename(src, dst)
        self.setPath(dst)
        logger.debug('Renamed: %s => %s' % (src, dst))
