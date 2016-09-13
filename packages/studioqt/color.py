#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/studioqt\color.py
from studioqt import QtGui

class Color(QtGui.QColor):

    @classmethod
    def fromColor(cls, color):
        """
        :type color: QtGui.QColor
        """
        color = 'rgb(%d, %d, %d, %d)' % color.getRgb()
        return cls.fromString(color)

    @classmethod
    def fromString(cls, text):
        """
        :type text: str
        """
        a = 255
        try:
            r, g, b, a = text.replace('rgb(', '').replace(')', '').split(',')
        except ValueError:
            r, g, b = text.replace('rgb(', '').replace(')', '').split(',')

        return cls(int(r), int(g), int(b), int(a))

    def __eq__(self, other):
        if other == self:
            return True
        elif isinstance(other, Color):
            return self.toString() == other.toString()
        else:
            return False

    def toString(self):
        """
        :type: str
        """
        return 'rgb(%d, %d, %d, %d)' % self.getRgb()

    def isDark(self):
        """
        :type: bool
        """
        return self.red() < 125 and self.green() < 125 and self.blue() < 125
