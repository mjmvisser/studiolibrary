#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\__init__.py
"""
mutils (maya utils)

------------
TRANSFER API
------------

mutils.Animation
+ Inherits mutils.Pose
----------

curve = getAttrCurve(name, attr)
load(objects=None, namespaces=None, bakeConnected=False, mirror=False, mirrorTable=None)
setAttrCurve(name, attr, curve)
attrCurve(name, attr)


mutils.Pose
+ Inherits mutils.SelectionSet
-----

load(objects=None, namespaces=None, blend=100, mirror=False, mirrorTable=None)
attrs()
attrType(name, attr)
attrValue(name, attr)
attrMirrorValue(name, attr)
mirrorTable(mutils.MirrorTable)
mirrorAxis(name)
mirrorObject(name)


mutils.SelectionSet
+ Inherits mutils.MayaTransfer
--------------

load(objects=None, namespaces=None)
select(namespaces=None, **kwargs)
list[str] namespaces()


mutils.MayaTransfer
--------------

createFromPath(str)
createFromObjects(str)

setObject(name, data)
object(name)
objects()
save(path)
read(path)
data()
metadata()
metadata(key=None)
setMetadata(key, value)
count()


"""
__author__ = 'kurt.rathjen'
from logger import *
from transfer import *
from decorators import *
from attribute import *
from node import *
from match import *
from reference import *
from selectionset import *
from modelpanelwidget import *
from pose import *
from animation import *
from mirrortable import *
from shaderassign import *
from snapshot import *
from utils import *
