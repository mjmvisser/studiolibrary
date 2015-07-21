#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\animation.py
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
# animation.py
import mutils

# Example 1:
# Create animation from objects
a = mutils.Animation.createFromObjects(objects)

# Example 2:
# Create from selected objects
objects = maya.cmds.ls(selection=True)
a = mutils.Animation.createFromObjects(objects)

# Example 3:
# Save to file
path = "/tmp/test.anim"
a.save(path)

# Example 4:
# Load from file
path = "/tmp/test.anim"
a = mutils.Animation.createFromPath(path)

# load to objects from file
a.load()

# load to selected objects
objects = maya.cmds.ls(selection=True)
a.load(objects=objects)

# load to namespaces
a.load(namespaces=["character1", "character2"])

# load to specified objects
a.load(objects=["Character1:Hand_L", "Character1:Finger_L"])
"""
import os
import mutils
log = mutils.logger
try:
    import maya.cmds
except Exception as e:
    import traceback
    print traceback.format_exc()

__author__ = 'krathjen'
EXTRACT_DIR = '/tmp/mutils/AnimationTransferData'
MIN_TIME_LIMIT = -10000
MAX_TIME_LIMIT = 100000
MAYA_FILE_TYPE = 'mayaAscii'

class Option:
    Insert = 'insert'
    Replace = 'replace'
    ReplaceAll = 'replace all'
    ReplaceCompletely = 'replaceCompletely'

    def __init__(self):
        pass


class AnimationTransferError(Exception):
    """Base class for exceptions in this module."""
    pass


def insertSourceKeyframe(curves, time):
    """
    @type curves: list[str]
    @type time: (int, int)
    """
    startTime, endTime = time
    for curve in curves:
        insertStaticKeyframe(curve, time)

    firstFrame = maya.cmds.findKeyframe(curves, time=(startTime, startTime), which='first')
    lastFrame = maya.cmds.findKeyframe(curves, time=(endTime, endTime), which='last')
    if firstFrame < startTime < lastFrame:
        maya.cmds.setKeyframe(curves, insert=True, time=(startTime, startTime))
    if firstFrame < endTime < lastFrame:
        maya.cmds.setKeyframe(curves, insert=True, time=(endTime, endTime))


def insertStaticKeyframe(curve, time):
    """
    @type curve: str
    @type time: (int, int)
    """
    startTime, endTime = time
    lastFrame = maya.cmds.findKeyframe(curve, which='last')
    firstFrame = maya.cmds.findKeyframe(curve, which='first')
    if firstFrame == lastFrame:
        maya.cmds.setKeyframe(curve, insert=True, time=(startTime, endTime))
        maya.cmds.keyTangent(curve, time=(startTime, startTime), ott='step')
    if startTime < firstFrame:
        nextFrame = maya.cmds.findKeyframe(curve, time=(startTime, startTime), which='next')
        if startTime < nextFrame < endTime:
            maya.cmds.setKeyframe(curve, insert=True, time=(startTime, nextFrame))
            maya.cmds.keyTangent(curve, time=(startTime, startTime), ott='step')
    if endTime > lastFrame:
        previousFrame = maya.cmds.findKeyframe(curve, time=(endTime, endTime), which='previous')
        if startTime < previousFrame < endTime:
            maya.cmds.setKeyframe(curve, insert=True, time=(previousFrame, endTime))
            maya.cmds.keyTangent(curve, time=(previousFrame, previousFrame), ott='step')


class Animation(mutils.Pose):
    IMPORT_NAMESPACE = 'REMOVE_IMPORT'

    def __init__(self):
        mutils.Pose.__init__(self)
        self.setMetadata('timeUnit', maya.cmds.currentUnit(q=True, time=True))
        self.setMetadata('linearUnit', maya.cmds.currentUnit(q=True, linear=True))
        self.setMetadata('angularUnit', maya.cmds.currentUnit(q=True, angle=True))

    @classmethod
    def createFromPath(cls, path):
        """
        @type path: str
        """
        t = cls()
        t._path = path
        if os.path.exists(t.poseJsonPath()):
            posePath = t.poseJsonPath()
        else:
            posePath = t.poseDictPath()
        log.debug('Reading: ' + posePath)
        data = cls.read(posePath)
        log.debug('Reading Done')
        t._data = data
        if posePath == t.poseDictPath():
            log.debug('Converting: ' + posePath)
            t.readMayaPath(t.mayaPath())
            log.debug('Converting Done')
        return t

    def readMayaPath(self, path):
        """
        @type path: str
        """
        if not os.path.exists(path):
            return
        f = open(path)
        lines = f.readlines()
        f.close()
        curve = None
        srcObjects = {}
        for i, line in enumerate(lines):
            if line.startswith('createNode animCurve'):
                curve = line.split('"')[1]
            elif curve and '.fullname' in line:
                try:
                    name, attr = line.split('"')[5].split('.')
                except IndexError as msg:
                    name, attr = lines[i + 1].split('"')[1].split('.')

                srcObjects.setdefault(name, {})
                srcObjects[name][attr] = curve
                curve = None

        matches = mutils.matchObjects(srcObjects=srcObjects.keys(), dstObjects=self.objects().keys())
        for srcNode, dstNode in matches:
            for attr in srcObjects[srcNode.name()]:
                self.setAttrCurve(dstNode.name(), attr, srcObjects[srcNode.name()][attr])

    def setAttrCurve(self, name, attr, curve):
        """
        @type name: str
        @type attr: str
        @type curve: str
        """
        self.objects()[name].setdefault('attrs', {})
        self.objects()[name]['attrs'].setdefault(attr, {})
        self.objects()[name]['attrs'][attr]['curve'] = curve

    def paths(self):
        """
        @rtype: list[str]
        """
        result = []
        if os.path.exists(self.mayaPath()):
            result.append(self.mayaPath())
        if os.path.exists(self.poseJsonPath()):
            result.append(self.poseJsonPath())
        return result

    def mayaPath(self):
        """
        @rtype: str
        """
        return os.path.join(self.path(), 'animation.ma')

    def poseJsonPath(self):
        """
        @rtype: str
        """
        return os.path.join(self.path(), 'pose.json')

    def poseDictPath(self):
        """
        @rtype: str
        """
        return os.path.join(self.path(), 'pose.dict')

    @mutils.unifyUndo
    @mutils.restoreSelection
    def open(self):
        """
        The reason we use importing and not referencing is because we need to modify
        the imported animation curves and modifying referenced animation curves is
        only supported in Maya 2014+
        """
        self.close()
        nodes = maya.cmds.file(self.mayaPath(), namespace=Animation.IMPORT_NAMESPACE, i=True, groupLocator=True, returnNewNodes=True)
        return nodes

    def close(self):
        """
        Clean up all imported nodes, as well as the namespace.
        Should be called in a finally block.
        """
        nodes = maya.cmds.ls(Animation.IMPORT_NAMESPACE + ':*') or []
        if nodes:
            maya.cmds.delete(nodes)
        if Animation.IMPORT_NAMESPACE in maya.cmds.namespaceInfo(ls=True) or []:
            maya.cmds.namespace(set=':')
            maya.cmds.namespace(rm=Animation.IMPORT_NAMESPACE)

    def cleanMayaFile(self, path):
        """
        Clean up all commands in the exported maya file that are not createNode.
        """
        f = open(path, 'r')
        lines = f.readlines()
        f.close()
        results = []
        for line in lines:
            if not line.startswith('select -ne'):
                results.append(line)
            else:
                results.append('// End')
                break

        f = open(path, 'w')
        f.writelines(results)
        f.close()

    def srcTime(self, source, curves):
        """
        @type curves: list[str]
        @type source: (int, int)
        @rtype: (int, int)
        """
        first = maya.cmds.findKeyframe(curves, which='first')
        last = maya.cmds.findKeyframe(curves, which='last')
        if not source:
            source = (first, last)
        else:
            sourceStart, sourceEnd = source
            if sourceStart < first:
                sourceStart = first
            if sourceEnd > last:
                sourceEnd = last
            source = (sourceStart, sourceEnd)
        return source

    def dstTime(self, source, start):
        """
        @param start:
        @param source:
        @return:
        """
        srcStartTime, srcEndTime = source
        duration = srcEndTime - srcStartTime
        if start is None:
            startTime = srcStartTime
        else:
            startTime = start
        endTime = startTime + duration
        if startTime == endTime:
            endTime = startTime + 1
        return (startTime, endTime)

    def attrCurve(self, name, attr, withNamespace = False):
        """
        @type name: str
        @type attr: str
        @rtype: str
        """
        curve = self.attr(name, attr).get('curve', None)
        if curve and withNamespace:
            curve = Animation.IMPORT_NAMESPACE + ':' + curve
        return curve

    @mutils.timing
    @mutils.unifyUndo
    @mutils.showWaitCursor
    @mutils.restoreSelection
    def save(self, path, time = None, compress = False, bakeConnected = True, sampleBy = 1):
        """
        @type time: (int, int)
        """
        objects = self.objects().keys()
        if not time:
            time = mutils.animationRange(objects)
        start, end = time
        gSelectedAnimLayers = maya.mel.eval('$a = $gSelectedAnimLayers;')
        if len(gSelectedAnimLayers) > 1:
            msg = 'More than one animation layer is selected! Please select only one animation layer for export!'
            raise AnimationTransferError(msg)
        if start is None or end is None:
            msg = 'Please specify a start and end frame!'
            raise AnimationTransferError(msg)
        if start >= end:
            msg = 'The start frame cannot be greater than or equal to the end frame!'
            raise AnimationTransferError(msg)
        if mutils.getDurationFromNodes(nodes=objects or []) <= 0:
            msg = 'No animation was found on the specified object/s! Please create a pose instead!'
            raise AnimationTransferError(msg)
        self.setMetadata('endFrame', end)
        self.setMetadata('startFrame', start)
        end += 1
        dstCurves = []
        validAnimCurves = []
        log.debug('Animation.save(path=%s, time=%s, compress=%s, bakeConnections=%s, sampleBy=%s)' % (path,
         str(time),
         str(compress),
         str(bakeConnected),
         str(sampleBy)))
        try:
            if bakeConnected:
                maya.cmds.undoInfo(openChunk=True)
                mutils.bakeConnected(objects, time=(start, end), sampleBy=sampleBy)
            for name in objects:
                if maya.cmds.copyKey(name, time=(start, end), includeUpperBound=False, option='keys'):
                    transform, = maya.cmds.duplicate(name, name='CURVE', parentOnly=True)
                    dstCurves.append(transform)
                    mutils.disconnectAll(transform)
                    maya.cmds.pasteKey(transform)
                    attrs = maya.cmds.listAttr(transform, unlocked=True, keyable=True) or []
                    attrs = list(set(attrs) - set(['translate', 'rotate', 'scale']))
                    for attr in attrs:
                        fullname = '%s.%s' % (transform, attr)
                        dstCurve, = maya.cmds.listConnections(fullname, destination=False) or [None]
                        if dstCurve:
                            dstCurve = maya.cmds.rename(dstCurve, 'CURVE')
                            srcCurve = mutils.animCurve('%s.%s' % (name, attr))
                            if srcCurve and 'animCurve' in maya.cmds.nodeType(srcCurve):
                                preInfinity = maya.cmds.getAttr(srcCurve + '.preInfinity')
                                postInfinity = maya.cmds.getAttr(srcCurve + '.postInfinity')
                                curveColor = maya.cmds.getAttr(srcCurve + '.curveColor')
                                useCurveColor = maya.cmds.getAttr(srcCurve + '.useCurveColor')
                                maya.cmds.setAttr(dstCurve + '.preInfinity', preInfinity)
                                maya.cmds.setAttr(dstCurve + '.postInfinity', postInfinity)
                                maya.cmds.setAttr((dstCurve + '.curveColor'), *curveColor[0])
                                maya.cmds.setAttr(dstCurve + '.useCurveColor', useCurveColor)
                            dstCurves.append(dstCurve)
                            if maya.cmds.keyframe(dstCurve, query=True, time=(start, end), keyframeCount=True):
                                self.setAttrCurve(name, attr, dstCurve)
                                maya.cmds.cutKey(dstCurve, time=(MIN_TIME_LIMIT, start - 1))
                                maya.cmds.cutKey(dstCurve, time=(end + 1, MAX_TIME_LIMIT))
                                validAnimCurves.append(dstCurve)

            mayaPath = os.path.join(path, 'animation.ma')
            posePath = os.path.join(path, 'pose.json')
            mutils.Pose.save(self, posePath)
            if validAnimCurves:
                maya.cmds.select(validAnimCurves)
                log.info('Saving animation: %s' % mayaPath)
                maya.cmds.file(mayaPath, force=True, options='v=0', type='mayaAscii', uiConfiguration=False, exportSelected=True)
                self.cleanMayaFile(mayaPath)
        finally:
            if bakeConnected:
                maya.cmds.undoInfo(closeChunk=True)
                maya.cmds.undo()
            elif dstCurves:
                maya.cmds.delete(dstCurves)

        self.setPath(path)

    @mutils.timing
    @mutils.showWaitCursor
    def load(self, objects = None, namespaces = None, start = None, sourceTime = None, attrs = None, currentTime = None, option = Option.ReplaceCompletely, connect = False, mirrorTable = None):
        """
        @type objects: list[str]
        @type namespaces: list[str]
        @type start: int
        @type sourceTime: (int, int)
        @type attrs: list[str]
        @type option: Option
        @type currentTime: bool
        """
        if option == Option.ReplaceAll:
            option = Option.ReplaceCompletely
        log.debug('Animation.load(objects=%s, option=%s, namespaces=%s, srcTime=%s, currentTime=%s)' % (len(objects),
         str(option),
         str(sourceTime),
         str(namespaces),
         str(currentTime)))
        if currentTime and start is None:
            start = maya.cmds.currentTime(query=True)
        try:
            srcCurves = self.open()
            srcObjects = self.objects().keys()
            srcTime = self.srcTime(sourceTime, srcCurves)
            dstTime = self.dstTime(srcTime, start)
            if mirrorTable:
                self.setMirrorTable(mirrorTable)
            maya.cmds.flushUndo()
            maya.cmds.undoInfo(openChunk=True)
            matches = mutils.matchObjects(srcObjects=srcObjects, dstObjects=objects, dstNamespaces=namespaces)
            if not matches:
                raise mutils.NoMatchFoundError('No objects match when loading data')
            if option != Option.ReplaceCompletely:
                insertSourceKeyframe(srcCurves, srcTime)
            for srcNode, dstNode in matches:
                dstNode.stripFirstPipe()
                for attr in self.attrs(srcNode.name()):
                    if attrs is not None and attr not in attrs:
                        continue
                    dstAttr = mutils.Attribute(dstNode.name(), attr)
                    srcCurve = self.attrCurve(srcNode.name(), attr, withNamespace=True)
                    if not dstAttr.exists():
                        log.debug('Skipping attribute: The destination attribute "%s.%s" does not exist!' % (dstAttr.name(), dstAttr.attr()))
                        continue
                    if srcCurve is None:
                        type_ = self.attrType(srcNode.name(), attr)
                        value = self.attrValue(srcNode.name(), attr)
                        srcAttr = mutils.Attribute(dstNode.name(), attr, type=type_, value=value)
                        self.setStaticKey(srcAttr, dstAttr, dstTime, option)
                    else:
                        self.setAnimationKey(srcCurve, dstAttr, time=dstTime, option=option, source=srcTime, connect=connect)

        finally:
            self.close()
            maya.cmds.undoInfo(closeChunk=True)

    def setStaticKey(self, srcAttr, dstAttr, time, option):
        """
        @type srcAttr: mutils.Attribute
        @type dstAttr: mutils.Attribute
        @type time: (int, int)
        """
        if option == Option.ReplaceCompletely:
            maya.cmds.cutKey(dstAttr.fullname())
            dstAttr.set(srcAttr.value(), key=False)
        elif dstAttr.isConnected():
            if option == Option.Replace:
                maya.cmds.cutKey(dstAttr.fullname(), time=time)
                dstAttr.insertStaticKeyframe(srcAttr.value(), time)
            elif option == Option.Insert:
                dstAttr.insertStaticKeyframe(srcAttr.value(), time)
        else:
            dstAttr.set(srcAttr.value(), key=False)

    def setAnimationKey(self, srcCurve, dstAttribute, time, option, source = None, connect = False):
        """
        @type srcCurve: str
        @type dstAttribute: mutils.Attribute
        @type connect: bool
        @type option: Option
        @type time: (int, int)
        @type source: (int, int)
        """
        startTime, endTime = time
        if dstAttribute.exists() and dstAttribute.isUnlocked():
            if option == Option.Replace:
                maya.cmds.cutKey(dstAttribute.fullname(), time=time)
            if maya.cmds.copyKey(srcCurve, time=source):
                try:
                    if option != Option.Replace:
                        time = (startTime, startTime)
                    maya.cmds.pasteKey(dstAttribute.fullname(), option=option, time=time, connect=connect)
                    if option == Option.ReplaceCompletely:
                        dstCurve = mutils.animCurve(dstAttribute.fullname())
                        if dstCurve:
                            curveColor = maya.cmds.getAttr(srcCurve + '.curveColor')
                            preInfinity = maya.cmds.getAttr(srcCurve + '.preInfinity')
                            postInfinity = maya.cmds.getAttr(srcCurve + '.postInfinity')
                            useCurveColor = maya.cmds.getAttr(srcCurve + '.useCurveColor')
                            maya.cmds.setAttr(dstCurve + '.preInfinity', preInfinity)
                            maya.cmds.setAttr(dstCurve + '.postInfinity', postInfinity)
                            maya.cmds.setAttr((dstCurve + '.curveColor'), *curveColor[0])
                            maya.cmds.setAttr(dstCurve + '.useCurveColor', useCurveColor)
                except RuntimeError as e:
                    log.error('Cannot set animation for destination %s' % dstAttribute.fullname())
