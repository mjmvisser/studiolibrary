#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/mutils\modelpanelwidget.py
from PySide import QtGui
from PySide import QtCore
try:
    import maya.cmds
    import maya.OpenMayaUI as mui
    from shiboken import wrapInstance, getCppPointer
    isMaya = True
except ImportError:
    isMaya = False

__all__ = ['ModelPanelWidget']

class ModelPanelWidget(QtGui.QWidget):

    @staticmethod
    def findUniqueName(name):
        for i in range(0, 1000):
            name_ = name + str(i)
            if not maya.cmds.panel(name_, exists=True):
                return name_

        raise Exception('Name is not unique!')

    def __init__(self, parent, name = 'modelPanel', **kwargs):
        super(ModelPanelWidget, self).__init__(parent, **kwargs)
        name = self.findUniqueName(name)
        self.setObjectName(name + 'Widget')
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setObjectName(name + 'Layout')
        self.setLayout(layout)
        maya.cmds.setParent(layout.objectName())
        modelPanel = maya.cmds.modelPanel(name, label='ModelPanel')
        maya.cmds.modelEditor(modelPanel, edit=True, allObjects=False)
        maya.cmds.modelEditor(modelPanel, edit=True, grid=False)
        maya.cmds.modelEditor(modelPanel, edit=True, dynamics=False)
        maya.cmds.modelEditor(modelPanel, edit=True, activeOnly=False)
        maya.cmds.modelEditor(modelPanel, edit=True, manipulators=False)
        maya.cmds.modelEditor(modelPanel, edit=True, headsUpDisplay=False)
        maya.cmds.modelEditor(modelPanel, edit=True, selectionHiliteDisplay=False)
        maya.cmds.modelEditor(modelPanel, edit=True, polymeshes=True)
        maya.cmds.modelEditor(modelPanel, edit=True, nurbsSurfaces=True)
        maya.cmds.modelEditor(modelPanel, edit=True, subdivSurfaces=True)
        maya.cmds.modelEditor(modelPanel, edit=True, displayTextures=True)
        maya.cmds.modelEditor(modelPanel, edit=True, displayAppearance='smoothShaded')
        displayLights = maya.cmds.modelEditor(modelPanel, query=True, displayLights=True)
        maya.cmds.modelEditor(modelPanel, edit=True, displayLights=displayLights)
        self._modelPanel = modelPanel
        self.hideMenuBar()
        self.hideBarLayout()

    def name(self):
        return self._modelPanel

    def modelPanel(self):
        ptr = mui.MQtUtil.findControl(self._modelPanel)
        return wrapInstance(long(ptr), QtCore.QWidget)

    def barLayout(self):
        name = maya.cmds.modelPanel(self._modelPanel, query=True, barLayout=True)
        ptr = mui.MQtUtil.findControl(name)
        return wrapInstance(long(ptr), QtCore.QObject)

    def hideBarLayout(self):
        self.barLayout().hide()

    def hideMenuBar(self):
        maya.cmds.modelPanel(self._modelPanel, edit=True, menuBarVisible=False)

    def setCamera(self, name):
        maya.cmds.modelPanel(self._modelPanel, edit=True, cam=name)


if __name__ == '__main__':
    widget = ModelPanelWidget(None, 'modelPanel')
    widget.show()
