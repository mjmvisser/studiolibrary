#Embedded file name: C:/Users/hovel/Dropbox/packages/studioLibrary/1.5.8/build27/studioLibrary\plugins\lockPlugin.py
"""
# Released subject to the BSD License
# Please visit http://www.voidspace.org.uk/python/license.shtml
#
# Copyright (c) 2014, Kurt Rathjen
# All rights reserved.
# Comments, suggestions and bug reports are welcome.
#
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
# THIS SOFTWARE IS PROVIDED BY KURT RATHJEN  ''AS IS'' AND ANY
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
import studioLibrary

class Plugin(studioLibrary.Plugin):

    def __init__(self, *args):
        """
        @type args: 
        """
        studioLibrary.Plugin.__init__(self, *args)
        self.setName('lock')
        self.setIcon(self.dirname() + '/images/lock.png')
        self._superusers = self.window().kwargs().get('superusers', [])
        self._lockFolder = re.compile(self.window().kwargs().get('lockFolder', ''))
        self._unlockFolder = re.compile(self.window().kwargs().get('unlockFolder', ''))

    def load(self):
        """
        """
        self.updateLock()

    def folderSelectionChanged(self, itemSelection1, itemSelection2):
        """
        @type itemSelection1: 
        @type itemSelection2: 
        """
        self.updateLock()

    def updateLock(self):
        """
        @rtype: None
        """
        if studioLibrary.user() in self._superusers or []:
            self.window().setLocked(False)
            return
        if self._lockFolder.match('') and self._unlockFolder.match(''):
            if self._superusers:
                self.window().setLocked(True)
            else:
                self.window().setLocked(False)
            return
        folders = self.window().selectedFolders()
        if not self._lockFolder.match(''):
            for folder in folders or []:
                if self._lockFolder.search(folder.dirname()):
                    self.window().setLocked(True)
                    return

            self.window().setLocked(False)
        if not self._unlockFolder.match(''):
            for folder in folders or []:
                if self._unlockFolder.search(folder.dirname()):
                    self.window().setLocked(False)
                    return

            self.window().setLocked(True)


if __name__ == '__main__':
    import studioLibrary
    superusers = ['kurt.rathjen']
    plugins = ['examplePlugin']
    studioLibrary.main(superusers=superusers, plugins=plugins, add=True)
