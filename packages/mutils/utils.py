#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/mutils\utils.py
import platform
import mutils
try:
    import maya.mel
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()

class MayaUtilsError(Exception):
    """Base class for exceptions in this module."""
    pass


class ObjectsError(MayaUtilsError):
    pass


class SelectionError(MayaUtilsError):
    pass


class NoMatchFoundError(MayaUtilsError):
    pass


class NoObjectFoundError(MayaUtilsError):
    pass


class MoreThanOneObjectFoundError(MayaUtilsError):
    pass


class ModelPanelNotInFocusError(MayaUtilsError):
    pass


def system():
    return platform.system().lower()


def isMac():
    return system().startswith('mac') or system().startswith('os') or system().startswith('darwin')


def isWindows():
    return system().lower().startswith('win')


def isLinux():
    return system().lower().startswith('lin')


def isMaya():
    """
    :rtype: bool
    """
    try:
        import maya.cmds
        maya.cmds.about(batch=True)
        return True
    except ImportError:
        return False


def ls(*args, **kwargs):
    """
    :rtype: list[Node]
    """
    return [ mutils.Node(name) for name in maya.cmds.ls(*args, **kwargs) or [] ]


def listAttr(node, **kwargs):
    """
    :type node: mutils.Node
    :type kwargs: dict
    :rtype: list[mutils.Attribute]
    """
    attrs = maya.cmds.listAttr(node.name(), **kwargs)
    return [ mutils.Attribute(node.name(), attr) for attr in attrs or [] ]


def currentRange():
    """
    :rtype: (int, int)
    """
    start, end = selectedRange()
    if end == start:
        start, end = animationRange()
        if start == end:
            start, end = playbackRange()
    return (start, end)


def selectedRange():
    """
    :rtype: (int, int)
    """
    result = maya.mel.eval('timeControl -q -range $gPlayBackSlider')
    start, end = result.replace('"', '').split(':')
    start, end = int(start), int(end)
    if end - start == 1:
        end = start
    return (start, end)


def playbackRange():
    """
    :rtype: (int, int)
    """
    start = maya.cmds.playbackOptions(query=True, min=True)
    end = maya.cmds.playbackOptions(query=True, max=True)
    return (start, end)


def connectedAttrs(objects):
    """
    """
    result = []
    if not objects:
        raise Exception('No objects specified')
    connections = maya.cmds.listConnections(objects, connections=True, p=True, d=False, s=True) or []
    for i in range(0, len(connections), 2):
        dstObj = connections[i]
        srcObj = connections[i + 1]
        nodeType = maya.cmds.nodeType(srcObj)
        if 'animCurve' not in nodeType:
            result.append(dstObj)

    return result


def currentModelPanel():
    """
    :rtype: str
    """
    currentPanel = maya.cmds.getPanel(withFocus=True)
    currentPanelType = maya.cmds.getPanel(typeOf=currentPanel)
    if currentPanelType not in ('modelPanel',):
        msg = 'Cannot find model panel with focus. Please select a model panel.'
        raise ModelPanelNotInFocusError(msg)
    return currentPanel


def bakeConnected(objects, time, sampleBy = 1):
    """
    """
    bakeAttrs = connectedAttrs(objects)
    if bakeAttrs:
        maya.cmds.bakeResults(bakeAttrs, time=time, shape=False, simulation=True, sampleBy=sampleBy, controlPoints=False, minimizeRotation=True, bakeOnOverrideLayer=False, preserveOutsideKeys=False, sparseAnimCurveBake=False, disableImplicitControl=True, removeBakedAttributeFromLayer=False)
    else:
        print 'cannot find connection to bake!'


def animationRange(objects = None):
    """
    :rtype : (int, int)
    """
    start = 0
    end = 0
    if not objects:
        objects = maya.cmds.ls(selection=True) or []
    if objects:
        start = int(maya.cmds.findKeyframe(objects, which='first'))
        end = int(maya.cmds.findKeyframe(objects, which='last'))
    return (start, end)


def disconnectAll(name):
    """
    :type name: str
    """
    for destination in maya.cmds.listConnections(name, plugs=True, source=False) or []:
        source, = maya.cmds.listConnections(destination, plugs=True)
        maya.cmds.disconnectAttr(source, destination)


def getSelectedObjects():
    """
    :rtype: list[str]
    :raise mutils.SelectionError:
    """
    selection = maya.cmds.ls(selection=True)
    if not selection:
        raise mutils.SelectionError('No objects selected!')
    return selection


def animCurve(fullname):
    """
    :type fullname:
    :rtype: None | str
    """
    result = None
    if maya.cmds.objExists(fullname):
        n = maya.cmds.listConnections(fullname, plugs=True, destination=False)
        if n and 'animCurve' in maya.cmds.nodeType(n):
            result = n
        elif n and 'character' in maya.cmds.nodeType(n):
            n = maya.cmds.listConnections(n, plugs=True, destination=False)
            if n and 'animCurve' in maya.cmds.nodeType(n):
                result = n
        if result:
            return result[0].split('.')[0]


def deleteUnknownNodes():
    """
    """
    nodes = maya.cmds.ls(type='unknown')
    if nodes:
        for node in nodes:
            if maya.cmds.objExists(node) and maya.cmds.referenceQuery(node, inr=True):
                maya.cmds.delete(node)


def getSelectedAttrs():
    """
    :rtype: list[str]
    """
    attributes = maya.cmds.channelBox('mainChannelBox', q=True, selectedMainAttributes=True)
    if attributes is not None:
        attributes = str(attributes)
        attributes = attributes.replace('tx', 'translateX')
        attributes = attributes.replace('ty', 'translateY')
        attributes = attributes.replace('tz', 'translateZ')
        attributes = attributes.replace('rx', 'rotateX')
        attributes = attributes.replace('ry', 'rotateY')
        attributes = attributes.replace('rz', 'rotateZ')
        attributes = eval(attributes)
    return attributes


def getNamespaceFromNames(objects):
    """
    :type objects: list[str]
    :rtype: list[str]
    """
    result = []
    for node in mutils.Node.get(objects):
        if node.namespace() not in result:
            result.append(node.namespace())

    return result


def getNamespaceFromObjects(objects):
    """
    :type objects: list[str]
    :rtype: list[str]
    """
    namespaces = [ mutils.Node(name).namespace() for name in objects ]
    return list(set(namespaces))


def getNamespaceFromSelection():
    """
    :rtype: list[str]
    """
    objects = maya.cmds.ls(selection=True)
    return getNamespaceFromObjects(objects)


def getDurationFromNodes(nodes):
    """
    :type nodes: list[str]
    :rtype: float
    """
    if nodes:
        s = maya.cmds.findKeyframe(nodes, which='first')
        l = maya.cmds.findKeyframe(nodes, which='last')
        if s == l:
            if maya.cmds.keyframe(nodes, query=True, keyframeCount=True) > 0:
                return 1
            else:
                return 0
        return l - s
    else:
        return 0


class ScriptJob(object):
    """
    self._scriptJob = mutils.ScriptJob(e=['SelectionChanged', self.selectionChanged])
    """

    def __init__(self, *args, **kwargs):
        self.id = maya.cmds.scriptJob(*args, **kwargs)

    def kill(self):
        if self.id:
            maya.cmds.scriptJob(kill=self.id, force=True)
            self.id = None

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        if t is not None:
            self.kill()
