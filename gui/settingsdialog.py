#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\gui\settingsdialog.py
from PySide import QtGui
from PySide import QtCore
import studioqt
import studiolibrary
__all__ = ['SettingsDialog']

class SettingsDialogSignal(QtCore.QObject):
    """
    """
    onNameChanged = QtCore.Signal(object)
    onPathChanged = QtCore.Signal(object)
    onColorChanged = QtCore.Signal(object)
    onBackgroundColorChanged = QtCore.Signal(object)


class SettingsDialog(QtGui.QDialog):
    """
    """
    signal = SettingsDialogSignal()
    onNameChanged = signal.onNameChanged
    onPathChanged = signal.onPathChanged
    onColorChanged = signal.onColorChanged
    onBackgroundColorChanged = signal.onBackgroundColorChanged

    def __init__(self, parent, library):
        """
        :type parent: QtGui.QWidget
        :type library: studiolibrary.Library
        """
        QtGui.QDialog.__init__(self, parent)
        studioqt.loadUi(self)
        self.setWindowTitle('Studio Library - %s' % studiolibrary.version())
        self.ui.saveButton.clicked.connect(self.save)
        self.ui.cancelButton.clicked.connect(self.close)
        self.ui.browseColorButton.clicked.connect(self.browseColor)
        self.ui.browseLocationButton.clicked.connect(self.browseLocation)
        self.ui.theme1Button.clicked.connect(self.setTheme1)
        self.ui.theme2Button.clicked.connect(self.setTheme2)
        self.ui.theme3Button.clicked.connect(self.setTheme3)
        self.ui.theme4Button.clicked.connect(self.setTheme4)
        self.ui.theme5Button.clicked.connect(self.setTheme5)
        self.ui.theme6Button.clicked.connect(self.setTheme6)
        self.ui.theme7Button.clicked.connect(self.setTheme7)
        self.ui.background1Button.clicked.connect(self.setBackground1)
        self.ui.background2Button.clicked.connect(self.setBackground2)
        self.ui.background3Button.clicked.connect(self.setBackground3)
        self._library = library
        self.updateStyleSheet()
        self.center()

    def save(self):
        """
        :rtype: None
        """
        self.validate()
        self.accept()

    def validate(self):
        """
        :rtype: None
        """
        try:
            library = self.library()
            library.validateName(self.name())
            library.validatePath(self.location())
        except Exception as e:
            QtGui.QMessageBox.critical(self, 'Validate Error', str(e))
            raise

    def center(self, width = 600, height = 435):
        """
        :rtype: None
        """
        desktopRect = QtGui.QApplication.desktop().availableGeometry()
        center = desktopRect.center()
        self.setGeometry(0, 0, width, height)
        self.move(center.x() - self.width() * 0.5, center.y() - self.height() * 0.5)

    def library(self):
        """
        :rtype: studiolibrary.Library
        """
        return self._library

    def setTitle(self, text):
        """
        :type text: str
        :rtype: None
        """
        self.ui.title.setText(text)

    def setText(self, text):
        """
        :type text: str
        :rtype: None
        """
        self.ui.text.setText(text)

    def setHeader(self, text):
        """
        :type text: str
        :rtype: None
        """
        self.ui.header.setText(text)

    def color(self):
        """
        :rtype: studioqt.Color
        """
        return self.library().accentColor()

    def backgroundColor(self):
        """
        :rtype: studioqt.Color
        """
        return self.library().backgroundColor()

    def name(self):
        """
        :rtype: str
        """
        return str(self.ui.nameEdit.text())

    def setName(self, name):
        """
        :type name: str
        :rtype: None
        """
        self.ui.nameEdit.setText(name)

    def setLocation(self, path):
        """
        :type path: str
        """
        self.ui.locationEdit.setText(path)

    def location(self):
        """
        :rtype: str
        """
        return str(self.ui.locationEdit.text())

    def setUpdateEnabled(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self._update = value

    def setTheme1(self):
        """
        """
        c = studioqt.Color(0, 175, 255)
        self.setColor(c)

    def setTheme2(self):
        """
        """
        c = studioqt.Color(150, 75, 240)
        self.setColor(c)

    def setTheme3(self):
        """
        """
        c = studioqt.Color(240, 100, 150)
        self.setColor(c)

    def setTheme4(self):
        """
        """
        c = studioqt.Color(240, 75, 50)
        self.setColor(c)

    def setTheme5(self):
        """
        """
        c = studioqt.Color(250, 155, 20)
        self.setColor(c)

    def setTheme6(self):
        """
        """
        c = studioqt.Color(255, 210, 20)
        self.setColor(c)

    def setTheme7(self):
        """
        """
        c = studioqt.Color(120, 200, 0)
        self.setColor(c)

    def setBackground1(self):
        """
        """
        c = studioqt.Color(80, 80, 80)
        self.setBackgroundColor(c)

    def setBackground2(self):
        """
        """
        c = studioqt.Color(65, 65, 65)
        self.setBackgroundColor(c)

    def setBackground3(self):
        """
        """
        c = studioqt.Color(50, 50, 50)
        self.setBackgroundColor(c)

    def setColor(self, color):
        """
        :type color: studioqt.Color
        :rtype: None
        """
        self.library().setAccentColor(color)
        self.updateStyleSheet()
        self.onColorChanged.emit(self)

    def setBackgroundColor(self, color):
        """
        :type color: studioqt.Color
        :rtype: None
        """
        self.library().setBackgroundColor(color)
        self.updateStyleSheet()
        self.onBackgroundColorChanged.emit(self)

    def browseColor(self):
        """
        :rtype: None
        """
        color = self.color()
        d = QtGui.QColorDialog(self)
        d.connect(d, QtCore.SIGNAL('currentColorChanged (const QColor&)'), self.setColor)
        d.open()
        if d.exec_():
            self.setColor(d.selectedColor())
        else:
            self.setColor(color)

    def updateStyleSheet(self):
        """
        :rtype: None
        """
        self.setStyleSheet(self.library().styleSheet())

    def browseLocation(self):
        """
        :rtype: None
        """
        path = self.location()
        path = self.browse(path, title='Browse Location')
        if path:
            self.setLocation(path)

    @staticmethod
    def browse(path, title = 'Browse Location'):
        """
        :type path: str
        :type title: str
        :rtype: str
        """
        if not path:
            from os.path import expanduser
            path = expanduser('~')
        path = str(QtGui.QFileDialog.getExistingDirectory(None, title, path))
        path = path.replace('\\', '/')
        return path
