#!/usr/bin/python
"""
"""
import os
import mutils
import studiolibrary
import mayabaseplugin

try:
    from PySide import QtGui
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtGui
    from PyQt4 import QtCore


class PluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class Plugin(mayabaseplugin.Plugin):

    def __init__(self, parent):
        """
        @type parent: QtGui.QWidget
        """
        mayabaseplugin.Plugin.__init__(self, parent)

        self.setName("Selection Set")
        self.setIcon(self.dirname() + "/images/set.png")
        self.setExtension("set")

        self.setRecord(Record)
        self.setInfoWidget(SelectionSetInfoWidget)
        self.setCreateWidget(SelectionSetCreateWidget)
        self.setPreviewWidget(SelectionSetPreviewWidget)


class Record(mayabaseplugin.Record):
    def __init__(self, *args, **kwargs):
        """
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)
        self.setTransferBasename("set.json")
        self.setTransferClass(mutils.SelectionSet)

        self.setTransferBasename("set.list")
        if not os.path.exists(self.transferPath()):
            self.setTransferBasename("set.json")

    def load(self):
        """
        """
        self.selectSelectionSet()


class SelectionSetInfoWidget(mayabaseplugin.InfoWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayabaseplugin.InfoWidget.__init__(self, *args, **kwargs)
        studiolibrary.loadUi(self)


class SelectionSetPreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayabaseplugin.PreviewWidget.__init__(self, *args, **kwargs)


class SelectionSetCreateWidget(mayabaseplugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        @type parent: QtGui.QWidget
        @type record: Record
        """
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)


if __name__ == "__main__":
    import studiolibrary
    studiolibrary.main()