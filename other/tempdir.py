#Embedded file name: /automount/sun-01/home/mvisser/workspace/studiolibrary/other/tempdir.py
"""
"""
import os
import shutil
import getpass
import tempfile
__all__ = ['TempDir']

class TempDir:

    def __init__(self, *args, **kwargs):
        """
        @type subDirs: list[str]
        """
        self._path = os.path.join(tempfile.gettempdir(), 'studiolibrary', getpass.getuser().lower(), *args)
        if kwargs.get('clean', False):
            self.clean()
        if kwargs.get('makedirs', True):
            self.makedirs()

    def path(self):
        """
        @rtype: str
        """
        return self._path

    def clean(self):
        """
        """
        if os.path.exists(self.path()):
            shutil.rmtree(self.path())

    def makedirs(self):
        """
        """
        if not os.path.exists(self.path()):
            os.makedirs(self.path())
