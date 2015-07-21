#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary\settings.py
"""
"""
import os
import studiolibrary
__all__ = ['Settings']

class Settings(studiolibrary.MetaFile):

    def __init__(self, scope, name, parent = None):
        self._path = None
        self._name = name
        self._scope = scope
        studiolibrary.MetaFile.__init__(self, '')

    def save(self):
        studiolibrary.MetaFile.save(self)

    def path(self):
        if not self._path:
            self._path = os.path.join(studiolibrary.SETTINGS_DIRNAME, 'studiolibrary', '.settings', self._scope, self._name + '.dict')
        return self._path
