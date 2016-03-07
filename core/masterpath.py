#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\core\masterpath.py
import os
import re
import shutil
import logging
from . import utils
from . import basepath
from . import metafile
__all__ = ['MasterPath', 'Version']
logger = logging.getLogger(__name__)

class VersionError(Exception):
    """
    """
    pass


class Version(basepath.BasePath):
    VERSION_PATTERN = '[.][0-9]+'

    def __init__(self, *args, **kwargs):
        """
        :type path: str
        :type read: bool
        """
        super(Version, self).__init__(*args, **kwargs)
        self._version = None
        self._versionPattern = self.VERSION_PATTERN
        self._masterPath = None

    def setMasterPath(self, masterPath):
        """
        :type masterPath: MasterPath
        :rtype: None
        """
        self._masterPath = masterPath

    def masterPath(self):
        """
        :rtype: MasterPath
        """
        return self._masterPath

    def setVersionPattern(self, versionPattern):
        """
        :type versionPattern:
        :rtype: None
        """
        self._versionPattern = versionPattern

    def versionPattern(self):
        """
        :rtype: str
        """
        return self._versionPattern

    def version(self):
        """
        :rtype: int
        """
        if self._version is None:
            pattern = re.compile(self.versionPattern())
            v = pattern.search(self.path())
            if v:
                self._version = v.group(0)[1:]
            else:
                VersionError('Cannot find version in path %s' % self.path())
        return self._version

    def restore(self):
        """
        :rtype: None
        """
        if not self.masterPath():
            VersionError('Cannot restore a version without a master. Please set the master path.')
        logger.debug('Restoring %s => %s' % (self.path(), self.masterPath().path()))
        if self.masterPath().exists():
            self.masterPath().createVersion(move=True)
        shutil.copytree(self.path(), self.masterPath().path())


class MasterPath(basepath.BasePath):
    META_PATH = '<PATH>/.studioLibrary/metafile.dict'
    VERSION_PATH = '<DIRNAME>/.studioLibrary/<NAME><EXTENSION>/<NAME><VERSION><EXTENSION>'
    VERSION_CONTROL_ENABLED = True

    def __init__(self, path):
        """
        :type path: str
        """
        basepath.BasePath.__init__(self, path)
        self._metaFile = None
        self._isVersionControlEnabled = self.VERSION_CONTROL_ENABLED

    def setVersionControlEnabled(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self._isVersionControlEnabled = value

    def isVersioControlEnabled(self):
        """
        :rtype: bool
        """
        return self._isVersionControlEnabled

    def resolvePath(self, path):
        """
        :rtype: str
        """
        dirname, name, extension = utils.splitPath(self.path())
        path = path.replace('<EXTENSION>', self.extension())
        path = path.replace('<DIRNAME>', self.dirname())
        path = path.replace('<NAME>', name)
        path = path.replace('<PATH>', self.path())
        return path

    def versionPath(self, version):
        """
        :type version: str | int
        :rtype: str
        """
        path = self.VERSION_PATH
        path = path.replace('<VERSION>', '.' + str(version))
        return self.resolvePath(path)

    def versionDirname(self):
        """
        :rtype: str
        """
        return os.path.dirname(self.versionPath('0001'))

    def metaPath(self):
        """
        :rtype: str
        """
        path = self.META_PATH
        return self.resolvePath(path)

    def metaFile(self):
        """
        :rtype: metafile.MetaFile
        """
        path = self.metaPath()
        if self._metaFile:
            if self._metaFile.path() != path:
                self._metaFile.setPath(path)
        else:
            self._metaFile = metafile.MetaFile(path, read=True)
        return self._metaFile

    def delete(self):
        """
        :rtype: None
        """
        self.retire()

    def retire(self):
        """
        :rtype: None
        """
        if self.exists() and not self.isVersioControlEnabled():
            raise VersionError('Version control has been disabled.')
        self.createVersion(move=True)

    def createVersion(self, move = False):
        """
        :type move: bool
        """
        if self.exists() and not self.isVersioControlEnabled():
            raise VersionError('Version control has been disabled.')
        self.metaFile().updateNonEditables()
        nextVersion = self.nextVersion()
        logger.debug('Retiring %s => %s' % (self.path(), nextVersion.path()))
        if nextVersion:
            dirname = os.path.dirname(nextVersion.path())
            if not os.path.exists(dirname):
                logger.debug("Making directory '%s'" % dirname)
                os.makedirs(dirname)
        if move:
            shutil.move(self.path(), nextVersion.path())
        else:
            shutil.copytree(self.path(), nextVersion.path())
        logger.debug('Retired %s => %s' % (self.path(), nextVersion.path()))

    def versions(self):
        """
        :rtype: list[Version]
        """
        results = []
        dirname = self.versionDirname()
        if os.path.exists(dirname):
            for name in sorted(os.listdir(dirname)):
                version = Version(dirname + '/' + name)
                if version.version():
                    version.setMasterPath(self)
                    results.append(version)

        return results

    def latestVersion(self):
        """
        :rtype: Version
        """
        versions = self.versions()
        if versions:
            return self.versions()[-1]

    def nextVersion(self):
        """
        :rtype: Version
        """
        latest = 1
        latestVersion = self.latestVersion()
        if latestVersion:
            latest = int(latestVersion.version())
            latest += 1
        n = str(latest).zfill(4)
        return Version(self.versionPath(version=n))

    def restoreLatestVersion(self):
        """
        :rtype: None
        """
        version = self.latestVersion()
        if version:
            version.restore()
        else:
            raise VersionError("No version found to restore. '%s'" % self.versionDirname())
