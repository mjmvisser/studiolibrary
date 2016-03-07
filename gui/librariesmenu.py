#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\gui\librariesmenu.py
import sys
import logging
from PySide import QtGui
import studioqt
import studiolibrary
__all__ = ['LibrariesMenu']
logger = logging.getLogger(__name__)

class LibrariesMenu(QtGui.QMenu):

    def __init__(self, *args):
        """
        """
        QtGui.QMenu.__init__(self, *args)
        self.setTitle('Libraries')
        self.reload()

    def reload(self):
        self.clear()
        for library in studiolibrary.libraries():
            action = LibraryAction(self, library)
            self.addAction(action)
            action.setStatusTip('Load library "%s" "%s"' % (library.name(), library.path()))
            action.triggered.connect(library.load)


class LibraryAction(QtGui.QWidgetAction):
    STYLE_SHEET = '\n#actionIcon {\n    background-color: ACCENT_COLOR;\n}\n\n#actionWidget {\n    background-color: BACKGROUND_COLOR;\n}\n\n#actionLabel, #actionLabel, #actionOption {\n    background-color: BACKGROUND_COLOR;\n    color: rgb(255, 255, 255);\n}\n#actionLabel:hover, #actionLabel:hover, #actionOption:hover {\n    background-color: COLOR;\n    color: rgb(255, 255, 255);\n}\n'

    def __init__(self, parent, library):
        """
        :type parent: QtGui.QMenu
        :type library: studiolibrary.Library
        """
        QtGui.QWidgetAction.__init__(self, parent)
        self._library = library
        self.setText(self.library().name())

    def library(self):
        """
        :rtype: studiolibrary.Librarya
        """
        return self._library

    def deleteLibrary(self):
        """
        :rtype: None
        """
        self.parent().close()
        self.library().showDeleteDialog()

    def createWidget(self, parent):
        """
        :type parent: QtGui.QMenu
        """
        height = 25
        spacing = 1
        actionWidget = QtGui.QFrame(parent)
        actionWidget.setObjectName('actionWidget')
        styleSheet = studioqt.StyleSheet.fromText(LibraryAction.STYLE_SHEET, options=self.library().theme())
        actionWidget.setStyleSheet(styleSheet.data())
        actionLabel = QtGui.QLabel(self.library().name(), actionWidget)
        actionLabel.setObjectName('actionLabel')
        actionLabel.setFixedHeight(height)
        iconColor = QtGui.QColor(255, 255, 255, 220)
        icon = studiolibrary.resource().icon('delete', color=iconColor)
        actionOption = QtGui.QPushButton('', actionWidget)
        actionOption.setObjectName('actionOption')
        actionOption.setIcon(icon)
        actionOption.setFixedHeight(height + spacing)
        actionOption.setFixedWidth(height)
        actionOption.clicked.connect(self.deleteLibrary)
        actionIcon = QtGui.QLabel('', actionWidget)
        actionIcon.setObjectName('actionIcon')
        actionIcon.setFixedWidth(10)
        actionIcon.setFixedHeight(height)
        actionLayout = QtGui.QHBoxLayout(actionWidget)
        actionLayout.setSpacing(0)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(actionIcon, stretch=1)
        actionLayout.addWidget(actionLabel, stretch=1)
        actionLayout.addWidget(actionOption, stretch=1)
        return actionWidget


class Example(QtGui.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()
        menubar = self.menuBar()
        menu = LibrariesMenu('Libraries', menubar)
        menubar.addMenu(menu)
        self.statusBar()
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Menubar')
        self.show()


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(funcName)s: %(message)s', filemode='w')
    app = QtGui.QApplication(sys.argv)
    e = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
