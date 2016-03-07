#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/mutils\snapshot.py
import os
import logging
import mutils
try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()

__all__ = ['snapshot', 'playblast', 'SnapshotError']
logger = logging.getLogger(__name__)

class SnapshotError(Exception):
    """Base class for exceptions in this module."""
    pass


def snapshot(path, start = None, end = None, width = 250, height = 250, step = 1, camera = None, modelPanel = None):
    """
    :type path: str
    :type start: int
    :type end: int
    :type width: int
    :type height: int
    :type step: int
    :rtype: str
    """
    if start is None:
        start = maya.cmds.currentTime(query=True)
    if end is None:
        end = start
    end = int(end)
    start = int(start)
    frame = [ i for i in range(start, end + 1, step) ]
    snapshotPanel = 'snapshotPanel'
    snapshotWindow = 'snapshotCamera'
    currentPanel = modelPanel or mutils.currentModelPanel()
    camera = camera or maya.cmds.modelEditor(currentPanel, query=True, camera=True)
    if maya.cmds.window(snapshotWindow, exists=True):
        maya.cmds.deleteUI(snapshotWindow)
    if maya.cmds.modelPanel(snapshotPanel, query=True, exists=True):
        maya.cmds.deleteUI(snapshotPanel, panel=True)
    snapshotWindow = maya.cmds.window(snapshotWindow, title=snapshotWindow, sizeable=False, minimizeButton=False, maximizeButton=False)
    maya.cmds.columnLayout('columnLayout')
    maya.cmds.paneLayout(width=width + 25, height=height + 25)
    snapshotPanel = maya.cmds.modelPanel(snapshotPanel, menuBarVisible=False, camera=camera)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, allObjects=False)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, grid=False)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, dynamics=False)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, activeOnly=False)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, manipulators=False)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, headsUpDisplay=False)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, selectionHiliteDisplay=False)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, polymeshes=True)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, nurbsSurfaces=True)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, subdivSurfaces=True)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, displayTextures=True)
    maya.cmds.modelEditor(snapshotPanel, camera=camera, edit=True, displayAppearance='smoothShaded')
    displayLights = maya.cmds.modelEditor(currentPanel, query=True, displayLights=True)
    maya.cmds.modelEditor(snapshotPanel, edit=True, displayLights=displayLights)
    maya.cmds.setParent('columnLayout')
    maya.cmds.button(label='Take Snapshot', width=width)
    rendererName = maya.cmds.modelEditor(currentPanel, query=True, rendererName=True)
    maya.cmds.modelEditor(snapshotPanel, edit=True, rendererName=rendererName)
    maya.cmds.window(snapshotWindow, edit=True, width=width, height=height + 25)
    maya.cmds.showWindow(snapshotWindow)
    try:
        path = playblast(path, snapshotPanel, start=start, end=end, frame=frame, width=width, height=height)
    finally:
        cmd = '\nimport maya.cmds;\nif maya.cmds.window("{window}", exists=True):\n    maya.cmds.deleteUI("{window}", window=True)\n'
        cmd = cmd.format(window=snapshotWindow)
        maya.cmds.evalDeferred(cmd)

    return path


def playblast(path, modelPanel, start, end, frame, width, height):
    """
    :type path: str
    :type modelPanel: str
    :type start: int
    :type end: int
    :type width: int
    :type height: int
    :type frame: list[int]
    :rtype: str
    """
    logger.info("Playblasting '%s'" % path)
    if start == end and os.path.exists(path):
        os.remove(path)
    maya.cmds.setFocus(modelPanel or mutils.currentModelPanel())
    name, compression = os.path.splitext(path)
    path = path.replace(compression, '')
    compression = compression.replace('.', '')
    path = maya.cmds.playblast(format='image', viewer=False, percent=100, startTime=start, endTime=end, quality=100, offScreen=mutils.isLinux(), forceOverwrite=True, width=width, height=height, showOrnaments=False, compression=compression, filename=path, frame=frame)
    if not path:
        raise SnapshotError('Playblast was canceled')
    src = path.replace('####', str(int(0)).rjust(4, '0'))
    if start == end:
        dst = src.replace('.0000.', '.')
        logger.info("Renaming '%s' => '%s" % (src, dst))
        os.rename(src, dst)
        src = dst
    logger.info("Playblasted '%s'" % src)
    return src
