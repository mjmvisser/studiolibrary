#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\reference.py
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
__author__ = 'krathjen'
import os
import mutils
log = mutils.logger
isMaya = False
try:
    import maya.mel
    import maya.cmds
    isMaya = True
except ImportError as e:
    print e

class Reference:

    def __init__(self, node = None):
        """
        @param node: str
        """
        self._node = node
        self._filename1 = None
        self._filename2 = None
        self._namespace = None
        self.setNode(node)

    def setNode(self, node):
        """
        @param node: str
        """
        self._node = node
        self._filename1 = maya.cmds.referenceQuery(self.node(), filename=True)
        self._filename2 = maya.cmds.referenceQuery(self.node(), filename=True, withoutCopyNumber=True)
        try:
            self._namespace = maya.cmds.referenceQuery(self.node(), namespace=True).replace(':', '')
        except RuntimeError as e:
            log.warning(e)

    def load(self):
        """
        Load the reference if its not loaded
        """
        if not self.isLoaded():
            maya.cmds.file(self.filename(), loadReference=self.node())
            self.setNode(self.node())

    def unload(self):
        if self.isLoaded():
            maya.cmds.file(self.filename(), unloadReference=self.node())

    def isLoaded(self):
        """
        @rtype: bool
        """
        return maya.cmds.referenceQuery(self.node(), isLoaded=True)

    def node(self):
        """
        @return: str
        """
        return self._node

    def filename(self, withoutCopyNumber = False):
        """
        @param withoutCopyNumber: bool
        @rtype: str
        """
        if withoutCopyNumber:
            return self._filename2
        return self._filename1

    def namespace(self):
        """
        @rtype: str
        """
        return self._namespace

    def replace(self, path):
        """
        @type path: str
        """
        if os.path.exists(path):
            if path != self.filename(withoutCopyNumber=True):
                maya.cmds.file(path, loadReference=self.node(), type='mayaAscii', options='v=0;')
        else:
            log.warning('Reference path does not exists: %s' % path)

    def metadata(self):
        """
        @rtype: dict[]
        """
        return {self.namespace(): {'filename': self.filename()}}

    @classmethod
    def ls(cls, objects, selection = False):
        """
        @type selection: str
        @rtype: list[Reference]
        """
        names = []
        results = []
        if objects:
            for name in maya.cmds.ls(objects):
                if maya.cmds.referenceQuery(name, isNodeReferenced=True):
                    names.append(maya.cmds.referenceQuery(name, referenceNode=True))

        else:
            names = maya.cmds.ls(type='reference')
        for name in names or []:
            if not name.startswith('sharedReferenceNode') and not maya.cmds.referenceQuery(name, isNodeReferenced=True):
                try:
                    results.append(cls(name))
                except RuntimeError as e:
                    log.warning('Skipping', name, e)

        return results
