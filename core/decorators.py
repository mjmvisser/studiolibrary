#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\core\decorators.py
import time
import logging
__all__ = ['timing']
logger = logging.getLogger(__name__)

def timing(fn):
    """
    :type fn: func
    :rtype:
    """

    def wrapped(*args, **kwargs):
        time1 = time.time()
        result = fn(*args, **kwargs)
        time2 = time.time()
        logger.debug('%s function took %0.5f sec' % (fn.func_name, time2 - time1))
        return result

    return wrapped
