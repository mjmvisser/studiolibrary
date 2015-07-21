#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\modelpanelwidget.py
__all__ = ['SnapshotWindow', 'ModelPanelWidget', 'showSnapshotWindow']
try:
    from PySide import QtGui
    from PySide import QtCore
    import shiboken
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore
    import sip

try:
    import maya.cmds
    import maya.OpenMayaUI as mui
except Exception as e:
    import traceback
    print traceback.format_exc()

class Window:
    main = None


def wrapinstance(ptr, base = None):
    """
    """
    if ptr is None:
        return
    ptr = long(ptr)
    try:
        base = QtCore.QObject
        return sip.wrapinstance(long(ptr), base)
    except:
        qObj = shiboken.wrapInstance(long(ptr), QtCore.QObject)
        metaObj = qObj.metaObject()
        cls = metaObj.className()
        superCls = metaObj.superClass().className()
        if hasattr(QtGui, cls):
            base = getattr(QtGui, cls)
        elif hasattr(QtGui, superCls):
            base = getattr(QtGui, superCls)
        else:
            base = QtGui.QWidget
        return shiboken.wrapInstance(long(ptr), base)


def unwrapinstance(qobject):
    """
    """
    try:
        return long(sip.unwrapinstance(qobject))
    except:
        return long(shiboken.getCppPointer(qobject)[0])


class ModelPanelWidget(QtGui.QWidget):

    def __init__(self, parent, name = 'customModelPanel', **kwargs):
        super(ModelPanelWidget, self).__init__(parent, **kwargs)
        try:
            maya.cmds.deleteUI('modelPanelWidget', panel=True)
        except:
            pass

        self.setObjectName('modelPanelWidget')
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName('modelPanelLayout')
        layout = mui.MQtUtil.fullName(unwrapinstance(self.verticalLayout))
        maya.cmds.setParent(layout)
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
        self.verticalLayout.addWidget(self.modelPanel())
        self.verticalLayout.itemAt(0).widget().hide()

    def name(self):
        return self._modelPanel

    def modelPanel(self):
        ptr = mui.MQtUtil.findControl(self._modelPanel)
        return wrapinstance(ptr, QtCore.QObject)

    def barLayout(self):
        name = maya.cmds.modelPanel(self._modelPanel, query=True, barLayout=True)
        ptr = mui.MQtUtil.findControl(name)
        return wrapinstance(ptr, QtCore.QObject)

    def hideBarLayout(self):
        self.barLayout().hide()

    def hideMenuBar(self):
        maya.cmds.modelPanel(self._modelPanel, edit=True, menuBarVisible=False)

    def setCamera(self, name):
        maya.cmds.modelPanel(self._modelPanel, edit=True, cam=name)

    def showEvent(self, event):
        super(ModelPanelWidget, self).showEvent(event)
        self.modelPanel().repaint()


class ModelPanelWindow(QtGui.QDialog):

    def __init__(self, parent, **kwargs):
        super(ModelPanelWindow, self).__init__(parent, **kwargs)
        self._width = 250
        self._height = 250
        self.setObjectName('modelPanelWindow')
        self.setWindowTitle('Qt Model Panel Window')
        self._label = QtGui.QLabel('x', self)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName('modelPanelWindowLayout')
        self._modelPanel = ModelPanelWidget(self, 'modelPanelWidget')
        self.verticalLayout.addWidget(self.modelPanel())
        self.verticalLayout.addWidget(self.label())
        self.resize(self.width(), self.height())
        self.modelPanel().show()
        self.label().hide()

    def width(self):
        return self._width

    def height(self):
        return self._height

    def label(self):
        return self._label

    def modelPanel(self):
        return self._modelPanel

    def keyReleaseEvent(self, event):
        path = '/tmp/snapshot.png'
        modelPanel = 'modelPanelWidget'


class SnapshotWindow(QtGui.QDialog):

    def __init__(self, parent, **kwargs):
        QtGui.QDialog.__init__(self, parent, **kwargs)
        self._width = 250
        self._height = 250
        try:
            maya.cmds.deleteUI('snapshotWindow', window=True)
        except:
            pass

        self.setObjectName('snapshotWindow')
        self.setWindowTitle('Snapshot Window')
        self._label = QtGui.QLabel('x', self)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName('modelPanelWindowLayout')
        self._modelPanel = ModelPanelWidget(self, 'modelPanelWidget')
        self.verticalLayout.addWidget(self.modelPanel())
        self.verticalLayout.addWidget(self.label())
        self.resize(self.width(), self.height())
        self.modelPanel().show()
        self.label().hide()

    def width(self):
        return self._width

    def height(self):
        return self._height

    def label(self):
        return self._label

    def modelPanel(self):
        return self._modelPanel

    def keyReleaseEvent(self, event):
        path = '/tmp/snapshot.png'
        modelPanel = 'modelPanelWidget'


def showSnapshotWindow():
    if Window.main:
        return Window.main
    ptr = mui.MQtUtil.mainWindow()
    win = wrapinstance(ptr, QtCore.QObject)
    Window.main = SnapshotWindow(win)
    Window.main.show()
    return Window.main


def delete():
    try:
        maya.cmds.deleteUI('snapshotWindow', panel=True)
        maya.cmds.deleteUI('modelPanelWindow', window=True)
    except:
        pass

    Window.main = None


if __name__ == '__main__':
    delete()
    show()
