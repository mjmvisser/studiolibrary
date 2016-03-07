#Embedded file name: /automount/sun-01/home/mvisser/workspace/studiolibrary/other/eventhook.py
"""
"""
__all__ = ['EventHook']

class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.connect(handler)
        return self

    def __isub__(self, handler):
        self.disconnect(handler)
        return self

    def connect(self, handler):
        self.disconnect(handler)
        self.__handlers.append(handler)

    def disconnect(self, handler):
        for h in self.__handlers:
            if str(h) == str(handler):
                self.__handlers.remove(h)

    def disconnectAll(self):
        self.__handlers = []

    def handlers(self):
        return self.__handlers

    def emit(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)
