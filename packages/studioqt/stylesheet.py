#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/studioqt\stylesheet.py
import os
import re
import studioqt

class StyleSheet(object):

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

    @classmethod
    def fromPath(cls, path, options = None):
        """
        :type path: str
        :rtype: str
        """
        styleSheet = cls()
        data = styleSheet.read(path)
        data = StyleSheet.format(data, options=options)
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

    @staticmethod
    def read(path):
        """
        :type path: str
        :rtype: str
        """
        p = path
        data = ''
        if p is not None and os.path.exists(p):
            f = open(p, 'r')
            data = f.read()
            f.close()
        return data

    @staticmethod
    def format(data = None, options = None):
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
            dpi = reDpi.search(line)
            if dpi:
                new = dpi.group().replace('DPI', str(studioqt.DPI))
                val = int(eval(new))
                line = line.replace(dpi.group(), str(val))
            newData.append(line)

        data = '\n'.join(newData)
        return data
