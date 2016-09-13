#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/mutils\selectionset.py
import os
import logging
import mutils
try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()

logger = logging.getLogger(__name__)

class SelectionSet(mutils.TransferBase):

    def __init__(self):
        mutils.TransferBase.__init__(self)
        self._namespaces = None

    def namespaces(self):
        """
        :rtype: list[str]
        """
        if self._namespaces is None:
            group = mutils.groupObjects(self.objects())
            self._namespaces = group.keys()
        return self._namespaces

    def iconPath(self):
        """
        Return the icon path for this transfer object.
        
        :rtype: str
        """
        return os.path.dirname(self.path()) + '/thumbnail.jpg'

    def setPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        if path.endswith('.set'):
            path += '/set.json'
        mutils.TransferBase.setPath(self, path)

    def load(self, objects = None, namespaces = None, **kwargs):
        """
        :type objects:
        :type namespaces: list[str]
        :type kwargs:
        """
        validNodes = []
        dstObjects = objects
        srcObjects = self.objects()
        matches = mutils.matchNames(srcObjects, dstObjects=dstObjects, dstNamespaces=namespaces)
        for srcNode, dstNode in matches:
            if '*' in dstNode.name():
                validNodes.append(dstNode.name())
            else:
                dstNode.stripFirstPipe()
                try:
                    dstNode = dstNode.toShortName()
                except mutils.NoObjectFoundError as msg:
                    logger.debug(msg)
                    continue
                except mutils.MoreThanOneObjectFoundError as msg:
                    logger.debug(msg)

                validNodes.append(dstNode.name())

        if validNodes:
            maya.cmds.select(validNodes, **kwargs)
        else:
            raise mutils.NoMatchFoundError('No objects match when loading data')

    def select(self, objects = None, namespaces = None, **kwargs):
        """
        :type objects:
        :type namespaces: list[str]
        :type kwargs:
        """
        SelectionSet.load(self, objects=objects, namespaces=namespaces, **kwargs)

    @mutils.showWaitCursor
    def save(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        self.setMetadata('mayaVersion', maya.cmds.about(v=True))
        self.setMetadata('mayaSceneFile', maya.cmds.file(q=True, sn=True))
        mutils.TransferBase.save(self, *args, **kwargs)
