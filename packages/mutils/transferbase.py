#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/mutils\transferbase.py
"""
A common abstract interface for saving poses, animation, selection sets and
mirror tables

import mutils

t = mutils.TransferBase.fromPath("/tmp/pose.dict")
t = mutils.TransferBase.fromObjects(["object1", "object2"])

t.load(selection=True)
t.load(objects=["obj1", "obj2"])
t.load(namespaces=["namespace1", "namespace2"])

t.save("/tmp/pose.dict")
t.read("/tmp/pose.dict")
"""
import os
import abc
import json
import getpass
import logging
logger = logging.getLogger(__name__)

class TransferBase(object):

    def __init__(self):
        self._path = None
        self._data = {'metadata': {},
         'objects': {}}

    def setMetadata(self, key, value):
        """
        :type key: str
        :type value: int | str | float | dict
        """
        self.data()['metadata'][key] = value

    @classmethod
    def fromPath(cls, path):
        """
        :type path: str
        """
        data = cls.read(path)
        t = cls()
        t.setPath(path)
        t.setData(data)
        return t

    @classmethod
    def fromObjects(cls, objects, **kwargs):
        """
        :type objects: list[str]
        :type kwargs: dict
        """
        t = cls(**kwargs)
        for obj in objects:
            t.add(obj)

        return t

    def path(self):
        """
        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        :type path: str
        """
        self._path = path

    def data(self):
        """
        :rtype: dict
        """
        return self._data

    def setData(self, data):
        """
        :type data:
        """
        self._data = data

    def objects(self):
        """
        :rtype: dict
        """
        return self.data().get('objects', {})

    def object(self, name):
        """
        :type name: str
        :rtype: dict
        """
        return self.objects().get(name, {})

    def metadata(self):
        """
        data = {
            "User": "",
            "Scene": "",
            "Reference": {"filename": "", "namespace": ""},
            "Description": "",
        }
        :rtype: dict
        """
        return self.data().get('metadata', {})

    def add(self, objects):
        """
        :type objects: str | list[str]
        """
        if isinstance(objects, basestring):
            objects = [objects]
        for name in objects:
            self.objects()[name] = self.createObjectData(name)

    def createObjectData(self, name):
        """
        :type name: str
        :rtype: dict
        """
        return {}

    def count(self):
        """
        :rtype: int
        """
        return len(self.objects() or [])

    def remove(self, objects):
        """
        :type objects: str | list[str]
        """
        if isinstance(objects, basestring):
            objects = [objects]
        for obj in objects:
            del self.objects()[obj]

    @abc.abstractmethod
    def load(self, *args, **kwargs):
        pass

    @staticmethod
    def read(path):
        """
        :type path: str
        :rtype: dict
        """
        with open(path, 'r') as f:
            data = f.read()
        if path.endswith('.dict'):
            return TransferBase.readDictData(data)
        elif path.endswith('.list'):
            return TransferBase.readListData(data)
        else:
            return TransferBase.readJsonData(data)

    @staticmethod
    def readJsonData(data):
        """
        :type data: str
        :rtype: dict
        """
        data = data.replace(': false', ': False').replace(': true', ': True')
        data = eval(data, {})
        return data

    @staticmethod
    def readListData(data):
        """
        :type data: str
        :rtype: dict
        """
        data = eval(data, {})
        result = {}
        for obj in data:
            result.setdefault(obj, {})

        return {'objects': result}

    @staticmethod
    def readDictData(data):
        """
        :type: str
        :rtype: dict
        """
        logger.debug('Reading .dict format')
        data = eval(data, {})
        result = {}
        for obj in data:
            result.setdefault(obj, {'attrs': {}})
            for attr in data[obj]:
                typ, val = data[obj][attr]
                result[obj]['attrs'][attr] = {'type': typ,
                 'value': val}

        return {'objects': result}

    def save(self, path, description = ''):
        """
        :type path: str
        """
        logger.info('Saving pose: %s' % path)
        self.setMetadata('version', '1.0.0')
        self.setMetadata('user', getpass.getuser())
        self.setMetadata('description', description)
        metadata = {'metadata': self.metadata()}
        data = self.dump(metadata)[:-1] + ','
        objects = {'objects': self.objects()}
        data += self.dump(objects)[1:]
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            logger.debug('Creating dirname: ' + dirname)
            os.makedirs(dirname)
        with open(path, 'w') as f:
            f.write(str(data))
        logger.info('Saved pose: %s' % path)

    def dump(self, data = None):
        """
        :type data: str | dict
        :rtype: str
        """
        if data is None:
            data = self.data()
        return json.dumps(data, indent=2)
