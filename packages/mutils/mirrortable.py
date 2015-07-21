#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\mirrortable.py
"""
#!/usr/bin/python
# -*- coding: latin-1 -*-
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
   # objects of its contributors may be used to endorse or promote products
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
# mirrortable.py
import mutils

# Example 1:
# Create mirror table from objects
mt = mutils.MirrorTable.createFromObjects(objects, "_l_", "_r_", MirrorPlane.YZ)

# Example 2:
# Create mirror table from selected objects
objects = maya.cmds.ls(selection=True)
mt = mutils.MirrorTable.createFromObjects(objects, "_l_", "_r_", MirrorPlane.YZ)

# Example 3:
# Save to file
path = "/tmp/test.mt"
mt.save(path)

# Example 4:
# Load from file
path = "/tmp/test.mt"
mt = mutils.MirrorTable.createFromPath(path)

# load to objects from file
mt.load()

# load to selected objects
objects = maya.cmds.ls(selection=True) or []
mt.load(objects=objects)

# loat to namespaces
mt.load(namespaces=["character1", "character2"])

# load to specified objects
mt.load(objects=["Character1:Hand_L", "Character1:Finger_L"])
mt.leftToRight()
mt.rightToLeft()
"""
import re
import mutils
log = mutils.logger
try:
    import maya.cmds
except ImportError as e:
    print e

__all__ = ['MirrorTable', 'MirrorPlane', 'MirrorOption']
RE_LEFT_SIDE = 'Lf|lf_|_lf|_l_|_L|L_|left|Left'
RE_RIGHT_SIDE = 'Rt|rt_|_rt|_r_|_R|R_|right|Right'

class MirrorPlane:
    YZ = [-1, 1, 1]
    XZ = [1, -1, 1]
    XY = [1, 1, -1]


class MirrorOption:
    Swap = 0
    RightToLeft = 1
    LeftToRight = 2


class MirrorTable(mutils.SelectionSet):

    @classmethod
    @mutils.restoreSelection
    def createFromObjects(cls, objects, left = None, right = None, mirrorPlane = MirrorPlane.YZ):
        """
        @type objects: list[str]
        """
        m = cls()
        m.setMetadata('left', left)
        m.setMetadata('right', right)
        m.setMetadata('mirrorPlane', mirrorPlane)
        for obj in objects:
            m.add(obj)

        return m

    def left(self):
        """
        @rtype: str | None
        """
        return self.metadata().get('left')

    def right(self):
        """
        @rtype: str | None
        """
        return self.metadata().get('right')

    def mirrorPlane(self):
        """
        @rtype: str | None
        """
        return self.metadata().get('mirrorPlane')

    def mirrorAxis(self, name):
        """
        @rtype: list[int]
        """
        return self.objects()[name]['mirrorAxis']

    def leftCount(self, objects = None):
        """
        @type objects: list[str]
        @rtype: int
        """
        if objects is None:
            objects = self.objects()
        return len([ obj for obj in objects if self.isLeftSide(obj) ])

    def rightCount(self, objects = None):
        """
        @type objects: list[str]
        @rtype: int
        """
        if objects is None:
            objects = self.objects()
        return len([ obj for obj in objects if self.isRightSide(obj) ])

    def createObjectData(self, name):
        """
        @type name:
        @rtype:
        """
        result = {'mirrorAxis': self.calculateMirrorAxis(name)}
        return result

    @staticmethod
    def findLeftSide(objects):
        """
        @type objects: str
        @rtype: str
        """
        return MirrorTable.findSide(objects, RE_LEFT_SIDE)

    @staticmethod
    def findRightSide(objects):
        """
        @type objects: str
        @rtype: str
        """
        return MirrorTable.findSide(objects, RE_RIGHT_SIDE)

    @staticmethod
    def findSide(objects, reSearch):
        """
        @type objects: str
        @type reSearch: str
        @rtype: str
        """
        reSearch = re.compile(reSearch)
        for obj in objects:
            right = reSearch.search(obj)
            if right:
                return right.group()

        return ''

    def matchObjects(self, objects = None, namespaces = None, selection = False, callback = None):
        """
        @param objects:
        @param namespaces:
        @param selection:
        @param callback:
        @return:
        """
        srcObjects = self.objects().keys()
        matches = mutils.matchObjects(srcObjects=srcObjects, dstObjects=objects, dstNamespaces=namespaces, selection=selection)
        results = {}
        for srcNode, dstNode in matches:
            dstObj = dstNode.name()
            mirrorAxis = self.mirrorAxis(srcNode.name())
            callback(srcNode.name(), dstObj, mirrorAxis)

        return results

    def rightToLeft(self):
        """
        """
        self.load(option=MirrorOption.RightToLeft)

    def leftToRight(self):
        """
        """
        self.load(option=MirrorOption.LeftToRight)

    @mutils.timing
    @mutils.unifyUndo
    @mutils.showWaitCursor
    @mutils.restoreSelection
    def load(self, objects = None, namespaces = None, option = MirrorOption.Swap, animation = True, time = None):
        """
        @param objects: list[str]
        @param namespaces: list[str]
        @param option: mirrorOptions
        """
        srcObjects = self.objects().keys()
        matches = mutils.matchObjects(srcObjects=srcObjects, dstObjects=objects, dstNamespaces=namespaces)
        foundObject = False
        results = {}
        for srcNode, dstNode in matches:
            dstObj = dstNode.name()
            dstObj2 = self.mirrorObject(dstObj) or dstObj
            if dstObj2 not in results:
                mirrorAxis = self.mirrorAxis(srcNode.name())
                results[dstObj] = dstObj2
                dstObjExists = maya.cmds.objExists(dstObj)
                dstObj2Exists = maya.cmds.objExists(dstObj2)
                if dstObjExists and dstObj2Exists:
                    foundObject = True
                    if animation:
                        self.transferAnimation(dstObj, dstObj2, mirrorAxis=mirrorAxis, option=option, time=time)
                    else:
                        self.transferStatic(dstObj, dstObj2, mirrorAxis=mirrorAxis, option=option)
                else:
                    if not dstObjExists:
                        log.debug('Cannot find destination object %s' % dstObj)
                    if not dstObj2Exists:
                        log.debug('Cannot find mirrored destination object %s' % dstObj2)

        if not foundObject:
            raise mutils.NoMatchFoundError('No objects match when loading data')

    def transferStatic(self, srcObj, dstObj, mirrorAxis = None, attrs = None, option = MirrorOption.Swap):
        """
        @param srcObj:
        @param dstObj:
        @param mirrorAxis:
        @param attrs:
        @param option:
        """
        srcValue = None
        dstValue = None
        srcValid = self.isValidMirror(srcObj, option)
        dstValid = self.isValidMirror(dstObj, option)
        if attrs is None:
            attrs = maya.cmds.listAttr(srcObj, keyable=True) or []
        for attr in attrs:
            dstAttr = dstObj + '.' + attr
            srcAttr = srcObj + '.' + attr
            if maya.cmds.objExists(dstAttr):
                if dstValid:
                    srcValue = maya.cmds.getAttr(srcAttr)
                if srcValid:
                    dstValue = maya.cmds.getAttr(dstAttr)
                if dstValid:
                    self.setAttr(dstObj, attr, srcValue, mirrorAxis=mirrorAxis)
                if srcValid:
                    self.setAttr(srcObj, attr, dstValue, mirrorAxis=mirrorAxis)
            else:
                log.debug('Cannot find destination attribute %s' % dstAttr)

    def setAttr(self, name, attr, value, mirrorAxis = None):
        """
        @param name:
        @param attr:
        @param value:
        @param mirrorAxis:
        """
        if mirrorAxis is not None:
            value = self.formatValue(attr, value, mirrorAxis)
        try:
            maya.cmds.setAttr(name + '.' + attr, value)
        except RuntimeError as e:
            log.debug('Cannot mirror static attribute %s.%s' % (name, attr))

    def transferAnimation(self, srcObj, dstObj, mirrorAxis = None, option = MirrorOption.Swap, time = None):
        """
        @param srcObj:
        @param dstObj:
        @param mirrorAxis:
        """
        srcValid = self.isValidMirror(srcObj, option)
        dstValid = self.isValidMirror(dstObj, option)
        tmpObj, = maya.cmds.duplicate(srcObj, name='DELETE_ME', parentOnly=True)
        try:
            if dstValid:
                self._transferAnimation(srcObj, tmpObj, time=time)
            if srcValid:
                self._transferAnimation(dstObj, srcObj, mirrorAxis=mirrorAxis, time=time)
            if dstValid:
                self._transferAnimation(tmpObj, dstObj, mirrorAxis=mirrorAxis, time=time)
        finally:
            maya.cmds.delete(tmpObj)

    def _transferAnimation(self, srcObj, dstObj, attrs = None, mirrorAxis = None, time = None):
        """
        @param srcObj:
        @param dstObj:
        @param attrs:
        @param mirrorAxis:
        """
        maya.cmds.cutKey(dstObj, time=time or ())
        if maya.cmds.copyKey(srcObj, time=time or ()):
            if not time:
                maya.cmds.pasteKey(dstObj, option='replaceCompletely')
            else:
                maya.cmds.pasteKey(dstObj, time=time, option='replace')
        if attrs is None:
            attrs = maya.cmds.listAttr(srcObj, keyable=True) or []
        for attr in attrs:
            srcAttribute = mutils.Attribute(srcObj, attr)
            dstAttribute = mutils.Attribute(dstObj, attr)
            if dstAttribute.exists():
                if dstAttribute.isConnected():
                    if self.isAttrMirrored(attr, mirrorAxis):
                        maya.cmds.scaleKey(dstAttribute.name(), valueScale=-1, attribute=attr)
                else:
                    value = srcAttribute.value()
                    self.setAttr(dstObj, attr, value, mirrorAxis)

    def isValidMirror(self, obj, option):
        """
        @param obj: str
        @param option: MirrorOption
        @rtype: bool
        """
        if option == MirrorOption.Swap:
            return True
        elif option == MirrorOption.RightToLeft and self.isLeftSide(obj):
            return False
        elif option == MirrorOption.LeftToRight and self.isRightSide(obj):
            return False
        else:
            return True

    @staticmethod
    def animCurve(obj, attr):
        """
        @param obj:
        @param attr:
        @return:
        """
        connections = maya.cmds.listConnections(obj + '.' + attr, d=False, s=True)
        if connections:
            return connections[0]

    @staticmethod
    def scaleKey(obj, attr):
        """
        @param obj:
        @param attr:
        """
        curve = MirrorTable.animCurve(obj, attr)
        if curve:
            maya.cmds.selectKey(curve)
            maya.cmds.scaleKey(iub=False, ts=1, fs=1, vs=-1, vp=0, animation='keys')

    @staticmethod
    def isAttrMirrored(attr, mirrorAxis):
        """
        @type attr: str
        @type mirrorAxis: list[int]
        @rtype: float
        """
        if mirrorAxis == [-1, 1, 1]:
            if attr == 'translateX' or attr == 'rotateY' or attr == 'rotateZ':
                return True
        elif mirrorAxis == [1, -1, 1]:
            if attr == 'translateY' or attr == 'rotateX' or attr == 'rotateZ':
                return True
        elif mirrorAxis == [1, 1, -1]:
            if attr == 'translateZ' or attr == 'rotateX' or attr == 'rotateY':
                return True
        elif mirrorAxis == [-1, -1, -1]:
            if attr == 'translateX' or attr == 'translateY' or attr == 'translateZ':
                return True
        return False

    @staticmethod
    def formatValue(attr, value, mirrorAxis):
        """
        @type attr: str
        @type value: float
        @type mirrorAxis: list[int]
        @rtype: float
        """
        if MirrorTable.isAttrMirrored(attr, mirrorAxis):
            return value * -1
        return value

    def isLeftSide(self, obj):
        """
        @type obj: str
        @rtype: bool
        """
        left = self.left()
        if left:
            if len(left) == 1:
                return self.replaceSingleSide(obj, left, 'X') != obj
            return left in obj
        return False

    def isRightSide(self, obj):
        """
        @type obj: str
        @rtype: bool
        """
        right = self.right()
        if right:
            if len(right) == 1:
                return self.replaceSingleSide(obj, right, 'X') != obj
            return right in obj
        return False

    def replaceSingleSide(self, srcObj, search, replace):
        """
        @type srcObj:
        @type search:
        @type replace:
        @rtype: str
        """
        dstObj = srcObj
        if ':' in srcObj:
            dstObj = srcObj.replace(':' + search, ':' + replace)
            if srcObj != dstObj:
                return dstObj
        if '|' in srcObj:
            dstObj = srcObj.replace('|' + search, '|' + replace)
        if srcObj.startswith(search):
            dstObj = replace + srcObj[1:]
        if srcObj != dstObj:
            return dstObj
        if '|' in srcObj:
            dstObj = srcObj.replace(search + '|', replace + '|')
        if dstObj.endswith(search):
            dstObj = dstObj[:-1] + replace
        if srcObj != dstObj:
            return dstObj
        return dstObj

    def mirrorObject(self, srcObj):
        """
        @type srcObj: str
        @rtype: str
        """
        left = self.left()
        right = self.right()
        if len(left) == 1 and len(right) == 1:
            dstObj = self.replaceSingleSide(srcObj, left, right)
            if dstObj != srcObj:
                return dstObj
            dstObj = self.replaceSingleSide(srcObj, right, left)
            if dstObj != srcObj:
                return dstObj
        dstObj = srcObj.replace(self.left(), self.right())
        if dstObj == srcObj:
            dstObj = srcObj.replace(self.right(), self.left())
        if dstObj != srcObj:
            return dstObj

    def calculateMirrorAxis(self, srcObj):
        """
        @type srcObj: str 
        @rtype: list[int]
        """
        result = [1, 1, 1]
        dstObj = self.mirrorObject(srcObj) or srcObj
        mirrorPlane = self.mirrorPlane()
        if dstObj == srcObj or not maya.cmds.objExists(dstObj):
            result = MirrorTable._calculateMirrorAxis(srcObj, mirrorPlane)
        else:
            result[0] = MirrorTable.isAxisMirrored(srcObj, dstObj, [1, 0, 0], mirrorPlane)
            result[1] = MirrorTable.isAxisMirrored(srcObj, dstObj, [0, 1, 0], mirrorPlane)
            result[2] = MirrorTable.isAxisMirrored(srcObj, dstObj, [0, 0, 1], mirrorPlane)
        return result

    @staticmethod
    def maxIndex(l):
        """
        Finds the largest number in a list
        @type l: list[]
        @rtype: int
        """
        m = 0
        index = 0
        for i in l:
            v = abs(float(i))
            if v > m:
                m = v
                index = l.index(i)

        return index

    @staticmethod
    def axisWorldPosition(obj, t):
        """
        @type obj: str
        @type t: list[int]
        @rtype: list[float]
        """
        transform1 = maya.cmds.createNode('transform', name='transform1')
        try:
            transform1, = maya.cmds.parent(transform1, obj, r=True)
            maya.cmds.setAttr((transform1 + '.t'), *t)
            maya.cmds.setAttr(transform1 + '.r', 0, 0, 0)
            maya.cmds.setAttr(transform1 + '.s', 1, 1, 1)
            return maya.cmds.xform(transform1, q=True, ws=True, piv=True)
        finally:
            maya.cmds.delete(transform1)

    @staticmethod
    def isAxisMirrored(srcObj, dstObj, t, mirrorPlane):
        """
        @param srcObj: str
        @param dstObj: str
        @param t: list[int] Translate
        @param mirrorPlane: list[int]
        @rtype: int
        """
        old1 = maya.cmds.xform(srcObj, q=True, ws=True, piv=True)
        old2 = maya.cmds.xform(dstObj, q=True, ws=True, piv=True)
        new1 = MirrorTable.axisWorldPosition(srcObj, t)
        new2 = MirrorTable.axisWorldPosition(dstObj, t)
        mp = mirrorPlane
        v1 = (mp[0] * (new1[0] - old1[0]), mp[1] * (new1[1] - old1[1]), mp[2] * (new1[2] - old1[2]))
        v2 = (new2[0] - old2[0], new2[1] - old2[1], new2[2] - old2[2])
        d = sum((p * q for p, q in zip(v1, v2)))
        if d >= 0.0:
            return 1
        return -1

    @staticmethod
    def _calculateMirrorAxis(obj, mirrorPlane):
        """
        @param obj: str
        @rtype: list[int]
        """
        result = [1, 1, 1]
        transform0 = maya.cmds.createNode('transform', name='transform0')
        try:
            transform0, = maya.cmds.parent(transform0, obj, r=True)
            transform0, = maya.cmds.parent(transform0, w=True)
            maya.cmds.setAttr(transform0 + '.t', 0, 0, 0)
            t1 = MirrorTable.axisWorldPosition(transform0, [1, 0, 0])
            t2 = MirrorTable.axisWorldPosition(transform0, [0, 1, 0])
            t3 = MirrorTable.axisWorldPosition(transform0, [0, 0, 1])
            t1 = ('%.3f' % t1[0], '%.3f' % t1[1], '%.3f' % t1[2])
            t2 = ('%.3f' % t2[0], '%.3f' % t2[1], '%.3f' % t2[2])
            t3 = ('%.3f' % t3[0], '%.3f' % t3[1], '%.3f' % t3[2])
            if mirrorPlane == MirrorPlane.YZ:
                x = [t1[0], t2[0], t3[0]]
                i = MirrorTable.maxIndex(x)
                result[i] = -1
            if mirrorPlane == MirrorPlane.XZ:
                y = [t1[1], t2[1], t3[1]]
                i = MirrorTable.maxIndex(y)
                result[i] = -1
            if mirrorPlane == MirrorPlane.XY:
                z = [t1[2], t2[2], t3[2]]
                i = MirrorTable.maxIndex(z)
                result[i] = -1
        finally:
            maya.cmds.delete(transform0)

        return result
