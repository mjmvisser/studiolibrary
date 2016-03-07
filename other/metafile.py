#Embedded file name: /automount/sun-01/home/mvisser/workspace/studiolibrary/other/metafile.py
"""
"""
import os
import time
import getpass
__all__ = ['MetaFile']

class MetaFile(dict):

    def __init__(self, path, read = True, **kwargs):
        super(MetaFile, self).__init__(**kwargs)
        self.setPath(str(path))
        if read and os.path.exists(self.path()):
            self.read()

    def prettyPrint(self):
        print '------ %s ------' % self.name()
        import json
        print json.dumps(self, indent=2)
        print '----------------\n'

    def delete(self):
        if self.exists():
            os.remove(self.path())

    def mkdir(self):
        dirname = os.path.dirname(self.path())
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def errors(self):
        return self.get('errors', '')

    def exists(self):
        if os.path.exists(self.path()):
            return True
        return False

    def description(self):
        return self.get('description', '')

    def setDescription(self, value):
        self.set('description', value)

    def set(self, key, value):
        self[key] = value

    def setOwner(self, value):
        self.set('owner', value)

    def owner(self):
        return self.get('owner', '')

    def mtime(self):
        return self.get('mtime', None)

    def setMtime(self, value):
        self.set('mtime', value)

    def setCtime(self, value):
        self.set('ctime', value)

    def ctime(self):
        """
        @rtype : str
        """
        return self.get('ctime', None)

    def setPath(self, path):
        self['_path'] = path
        self._path = path.replace('\\', '/')

    def path(self):
        return self._path

    def dirname(self):
        return os.path.dirname(self.path())

    def name(self):
        return os.path.basename(self.path())

    def read(self):
        data = self._read(self.path())
        self.update(data)
        return self

    def _read(self, path):
        """
        @type path: str
        @rtype: dict[]
        """
        results = {}
        f = open(path, 'r')
        data = f.read().strip()
        f.close()
        try:
            data = eval(data, {})
            results.update(data)
        except Exception as e:
            results = {}
            print "Cannot evaluate meta file '%s'." % path
            import traceback
            traceback.print_exc()
            results['errors'] = traceback.format_exc() + str(e)

        return results

    def write(self, path, data):
        """
        @type path: str
        @type data: str
        @rtype: dict[]
        """
        f = open(path, 'w')
        f.write(str(data))
        f.close()

    def save(self):
        t = str(time.time()).split('.')[0]
        if not self.ctime():
            self.setCtime(t)
        self.setMtime(t)
        if not self.owner():
            self.setOwner(getpass.getuser().lower())
        dirname = os.path.dirname(self.path())
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        data = dict()
        data['errors'] = ['An error has occurred when evaluating string: %s' % str(self)]
        try:
            data = eval(str(self), {})
            if 'errors' in data:
                del data['errors']
            path = None
            if '_path' in data:
                path = self['_path']
                del self['_path']
            self.write(self.path(), data=self)
            if path:
                self['_path'] = path
        except:
            print 'ERROR saving: ' + self.path()
            import traceback
            data['errors'].append(traceback.format_exc())
            raise
