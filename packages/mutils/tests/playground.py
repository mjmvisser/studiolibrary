#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/mutils\tests\playground.py
import time
import json

def timing(fn):

    def wrapped(*args, **kwargs):
        time1 = time.time()
        ret = fn(*args, **kwargs)
        time2 = time.time()
        print '%s function took %0.5f sec' % (fn.func_name, time2 - time1)
        return ret

    return wrapped


@timing
def test():
    f = open('/homes/krathjen/StudioLibraryRoot/Temp/test3.anim/pose.dict')
    data = f.read()
    f.close()
    eval(data, {})


@timing
def test2():
    f = open('/homes/krathjen/StudioLibraryRoot/Temp/test3.anim/pose2.dict')
    data = f.read()
    f.close()
    eval(data, {})


@timing
def test3():
    f = open('/tmp/local/pose.dict')
    data = f.read()
    f.close()
    eval(data, {})


@timing
def test4():
    f = open('/tmp/local/pose2.dict')
    data = f.read()
    f.close()
    data = data.replace(': false', ': False').replace(': true', ': True')
    eval(data, {})


test()
test2()
test3()
test4()
