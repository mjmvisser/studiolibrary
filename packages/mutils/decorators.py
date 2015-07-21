#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\decorators.py
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
__author__ = 'kurt.rathjen'
import time
import mutils
log = mutils.logger
try:
    import maya.cmds
except ImportError as e:
    import traceback
    traceback.print_exc()

def timing(fn):
    """
    Decorator!
    @type fn: func
    @rtype:
    """

    def wrapped(*args, **kwargs):
        time1 = time.time()
        ret = fn(*args, **kwargs)
        time2 = time.time()
        log.debug('%s function took %0.5f sec' % (fn.func_name, time2 - time1))
        return ret

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
