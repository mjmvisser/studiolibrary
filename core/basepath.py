#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary\core\basepath.py
import os
import shutil
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
        self._path = ''
        path = path or ''
        path = path.replace('\\', '/')
        if path:
            self.setPath(path)

    def resolvePath(self, path, labels = None):
        """
        :type path: str
        :type labels: dict
        
        :rtype: str
        """
        dirname, name, extension = utils.splitPath(self.path())
        labels_ = {'name': name,
         'path': self.path(),
         'dirname': self.dirname(),
         'extension': self.extension()}
        if labels:
            labels_.update(labels)
        return path.format(**labels_)

    def openLocation(self):
        """
        :rtype: None
        """
        path = self.path()
        utils.openLocation(path)

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
        if self.isFile():
            os.remove(self.path())
        else:
            os.removedirs(self.path())

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
        return os.path.getmtime(self.path())

    def ctime(self):
        """
        :rtype: float
        """
        return os.path.getctime(self.path())

    def mkdir(self):
        """
        :rtype: None
        """
        dirname = self.dirname()
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def move(self, dst):
        """
        :type dst: str
        :rtype: None
        """
        src = self.path()
        if self.isFolder():
            dst = dst + '/' + self.name()
            dst = utils.generateUniquePath(dst)
        shutil.move(src, dst)
        self.setPath(dst)

    def copy(self, dst):
        """
        :type dst: str
        :rtype: None
        """
        src = self.path()
        if self.isFile():
            shutil.copy(src, dst)
        else:
            shutil.copytree(src, dst)
        self.setPath(dst)

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
