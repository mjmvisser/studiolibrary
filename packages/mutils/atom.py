#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\atom.py
"""

import atom
atom.Atom.exportAtom("/tmp/test.atom", range=[1,25])
atom.Atom.importAtom("/tmp/test.atom")

WARNING: MUST LOAD PLUGIN BEFORE USING
"""
__author__ = 'krathjen'
import maya.cmds

class ImportOption:
    Insert = 'insert'
    ScaleInsert = 'scaleInsert'


class TargetTime:
    FromFile = 3
    TimeSlider = 2


def restoreSelection(fn):
    """
    """

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


class Atom:

    @staticmethod
    @restoreSelection
    def exportAtom(path, time, constraint = False):
        """
        @type path: str
        @type time: list[int]
        @type constraint: bool
        """
        start, end = time
        constraint = int(constraint)
        options = '\n        precision=8;\n        statics=1;\n        baked=1;\n        sdk=0;\n        constraint=%s;\n        animLayers=0;\n        selected=selectedOnly;\n        whichRange=1;\n        range=%s:%s;\n        hierarchy=none;\n        controlPoints=0;\n        useChannelBox=1;\n        options=keys;\n        copyKeyCmd=-animation objects -option keys -hierarchy none -controlPoints 0 "\n        ' % (constraint, start, end)
        maya.cmds.file(path, es=True, force=True, options=options, typ='atomExport')

    @staticmethod
    @restoreSelection
    def importAtom(path, namespace = '', search = None, replace = None, targetTime = TargetTime.FromFile):
        """
        time=1:10;
        template=character;;
        selected=template;
        
        @type path: str
        @type search: str
        @type replace: str
        @type namespace: str
        @type targetTime: TargetTime
        """
        search = search or ''
        replace = replace or ''
        options = '\n        ;;targetTime=%s;\n        option=scaleInsert;\n        match=hierarchy;;\n        selected=selectedOnly;\n        search=%s;\n        replace=%s;\n        prefix=;\n        suffix=;\n        mapFile=/tmp/;"\n        ' % (targetTime, search, replace)
        maya.cmds.file(path, i=True, renameAll=True, options=options, namespace=namespace, typ='atomImport')


class Template(object):

    @classmethod
    def createFromFile(cls, path):
        pass

    @classmethod
    def createFromObjects(cls, objects):
        pass

    @classmethod
    def createFromSelection(cls):
        pass
