#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\shaderassign.py
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
import os
import mutils
log = mutils.logger
try:
    import maya.mel
    import maya.cmds
except ImportError as e:
    print e

def exportShaders(path):
    """
    @type path: str
    @rtype: ShaderAssign
    """
    shaderAssign = ShaderAssign()
    shaderAssign.export(path)
    return shaderAssign


def importShaders(path, namespace = ''):
    """
    @type path: str
    @rtype: ShaderAssign
    """
    shaderAssign = ShaderAssign()
    shaderAssign.load(path, namespace)
    return shaderAssign


class ShaderAssign:
    NAME = 'shaderAssign'

    def name(self):
        """
        @rtype: str
        """
        return ShaderAssign.NAME

    def disconnectInitialShadingGroup(self):
        """
        """
        for connection in maya.cmds.listConnections('initialShadingGroup.dagSetMembers', p=True, s=True, d=False):
            maya.cmds.disconnectAttr(connection, 'initialShadingGroup.dagSetMembers', na=True)

    def connectInitialShadingGroup(self):
        """
        # Connect any shapes that don't have a shader to the initial shading group.
        """
        shapes = maya.cmds.ls(type='mesh')
        for shape in shapes:
            connections = maya.cmds.listConnections(shape, type='shadingEngine') or []
            if not connections:
                log.info('Connecting "%s" to the initial shading group.' % shape)
                maya.cmds.connectAttr(shape + '.instObjGroups', 'initialShadingGroup.dagSetMembers', na=True)

    def create(self):
        """
        """
        name = self.name()
        self.delete()
        maya.cmds.createNode('transform', name=name)
        maya.cmds.addAttr(name, ln='notes', dt='string')
        shadingEngines = maya.cmds.ls(type='shadingEngine')
        cmd = 'global proc connectShaderAssign(string $namespace1, string $namespace2) {\n'
        shapes = maya.cmds.ls(type='mesh')
        for shape in shapes:
            connections = maya.cmds.listConnections(shape + '.instObjGroups', p=True) or []
            if not connections:
                cmd += 'catch(`disconnectAttr -na ($namespace1 + "' + shape + '.instObjGroups") ("initialShadingGroup.dagSetMembers")`);\n'

        for shaderEngine in shadingEngines:
            if shaderEngine.startswith('initial'):
                continue
            assigned = maya.cmds.sets(shaderEngine, query=True) or []
            assigned = list(set(assigned))
            for connection in assigned:
                cmd += 'catch(`sets -e -fe ($namespace1 + "' + shaderEngine + '") ($namespace2 + "' + connection + '")`);\n'

        place3dTextures = maya.cmds.ls(type='place3dTexture')
        for place3dTexture in place3dTextures:
            tempString = maya.cmds.listConnections(place3dTexture + '.worldInverseMatrix', plugs=True)
            cmd += 'catch(`connectAttr ($namespace2 + "' + place3dTexture + '.worldInverseMatrix") ($namespace1 + "' + tempString[0] + '")`);\n'

        cmd += '}\n'
        maya.cmds.setAttr(name + '.notes', cmd, type='string')

    def cmd(self):
        """
        @rtype: str
        """
        return maya.cmds.getAttr(self.name() + '.notes')

    def assign(self, namespace1 = '', namespace2 = ''):
        """
        @type namespace1: str
        @type namespace2: str
        """
        maya.mel.eval(self.cmd())
        maya.mel.eval('connectShaderAssign("%s", "%s");' % (namespace1, namespace2))

    def delete(self):
        """
        """
        if maya.cmds.objExists(self.name()):
            maya.cmds.delete(self.name())

    def export(self, path):
        """
        @type path: str
        """
        log.info('Exporting shaders to path: %s' % path)
        self.create()
        maya.mel.eval('MLdeleteUnused;')
        shadingNodes = maya.cmds.lsThroughFilter('DefaultAllShadingNodesFilter', na=True)
        maya.cmds.select(clear=True)
        for shadingNode in shadingNodes:
            objectType = maya.cmds.objectType(shadingNode)
            if objectType == 'camera' or objectType.endswith('*Light'):
                continue
            maya.cmds.select(shadingNode, add=True, ne=True)

        maya.cmds.select('shaderAssign', add=True)
        if os.path.exists(path):
            os.remove(path)
        maya.cmds.file(path, op='v=0;p=17', type='mayaAscii', es=True)
        self.delete()

    def load(self, path, namespace = ''):
        """
        @type path: str
        """
        log.info('Loading shaders from path: %s' % path)
        maya.cmds.file(path, i=True)
        self.assign('', namespace)
        self.connectInitialShadingGroup()
        self.delete()
