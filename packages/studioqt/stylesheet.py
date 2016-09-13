#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/studioqt\stylesheet.py
import os
import re
import studioqt

class StyleSheet(object):

    @classmethod
    def fromPath(cls, path, **kwargs):
        """
        :type path: str
        :rtype: str
        """
        styleSheet = cls()
        data = styleSheet.read(path)
        data = StyleSheet.format(data, **kwargs)
        styleSheet.setData(data)
        return styleSheet

    @classmethod
    def fromText(cls, text, options = None):
        """
        :type text: str
        :rtype: str
        """
        styleSheet = cls()
        data = StyleSheet.format(text, options=options)
        styleSheet.setData(data)
        return styleSheet

    def __init__(self):
        self._data = ''

    def setData(self, data):
        """
        :type data: str
        """
        self._data = data

    def data(self):
        """
        :rtype: str
        """
        return self._data

    @staticmethod
    def read(path):
        """
        :type path: str
        :rtype: str
        """
        data = ''
        if os.path.isfile(path):
            with open(path, 'r') as f:
                data = f.read()
        return data

    @staticmethod
    def format(data = None, options = None, dpi = 1):
        """
        :type data:
        :type options: dict
        :rtype: str
        """
        if options is not None:
            keys = options.keys()
            keys.sort(key=len, reverse=True)
            for key in keys:
                data = data.replace(key, options[key])

        reDpi = re.compile('[0-9]+[*]DPI')
        newData = []
        for line in data.split('\n'):
            dpi_ = reDpi.search(line)
            if dpi_:
                new = dpi_.group().replace('DPI', str(dpi))
                val = int(eval(new))
                line = line.replace(dpi_.group(), str(val))
            newData.append(line)

        data = '\n'.join(newData)
        return data
