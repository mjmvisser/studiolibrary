#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/mutils\decorators.py
import time
import logging
try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()

logger = logging.getLogger(__name__)
__all__ = ['timing',
 'unifyUndo',
 'disableUndo',
 'disableViews',
 'disableAutoKey',
 'showWaitCursor',
 'restoreSelection',
 'restoreCurrentTime']

def timing(fn):

    def wrapped(*args, **kwargs):
        time1 = time.time()
        ret = fn(*args, **kwargs)
        time2 = time.time()
        logger.debug('%s function took %0.5f sec' % (fn.func_name, time2 - time1))
        return ret

    return wrapped


def unifyUndo(fn):

    def wrapped(*args, **kwargs):
        maya.cmds.undoInfo(openChunk=True)
        try:
            return fn(*args, **kwargs)
        finally:
            maya.cmds.undoInfo(closeChunk=True)

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped


def disableUndo(fn):

    def wrapped(*args, **kwargs):
        initialUndoState = maya.cmds.undoInfo(q=True, state=True)
        maya.cmds.undoInfo(stateWithoutFlush=False)
        try:
            return fn(*args, **kwargs)
        finally:
            maya.cmds.undoInfo(stateWithoutFlush=initialUndoState)

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped


def disableAutoKey(fn):

    def wrapped(*args, **kwargs):
        initialState = maya.cmds.autoKeyframe(query=True, state=True)
        maya.cmds.autoKeyframe(edit=True, state=False)
        try:
            return fn(*args, **kwargs)
        finally:
            maya.cmds.autoKeyframe(edit=True, state=initialState)

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped


def restoreSelection(fn):

    def wrapped(*args, **kwargs):
        selection = maya.cmds.ls(selection=True) or []
        try:
            return fn(*args, **kwargs)
        finally:
            if selection:
                maya.cmds.select(selection)

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped


def restoreCurrentTime(fn):

    def wrapped(*args, **kwargs):
        initialTime = maya.cmds.currentTime(query=True)
        try:
            return fn(*args, **kwargs)
        finally:
            maya.cmds.currentTime(initialTime, edit=True)

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped


def showWaitCursor(fn):

    def wrapped(*args, **kwargs):
        maya.cmds.waitCursor(state=True)
        try:
            return fn(*args, **kwargs)
        finally:
            maya.cmds.waitCursor(state=False)

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped


def disableViews(fn):

    def wrapped(*args, **kwargs):
        modelPanels = maya.cmds.getPanel(vis=True)
        emptySelConn = maya.cmds.selectionConnection()
        for panel in modelPanels:
            if maya.cmds.getPanel(to=panel) == 'modelPanel':
                maya.cmds.isolateSelect(panel, state=True)
                maya.cmds.modelEditor(panel, e=True, mlc=emptySelConn)

        try:
            return fn(*args, **kwargs)
        finally:
            for panel in modelPanels:
                if maya.cmds.getPanel(to=panel) == 'modelPanel':
                    maya.cmds.isolateSelect(panel, state=False)

            maya.cmds.deleteUI(emptySelConn)

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped
