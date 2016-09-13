#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/mutils\tests\test_anim.py
import os
import mutils
import maya.cmds
import test_base

class TestAnim(test_base.TestBase):

    def setUp(self):
        """
        """
        pass

    def save(self, bakeConnected = False):
        """
        Test save animation.
        """
        self.open()
        anim = mutils.Animation.fromObjects(self.srcObjects)
        anim.save(self.dstPath, bakeConnected=bakeConnected)

    def test_older_version(self):
        """
        """
        srcPath = os.path.join(self.dataDir(), 'test_older_version.anim')
        a = mutils.Animation.fromPath(srcPath)

    def test_load_replace_completely(self):
        """
        Test load animation.
        """
        self.srcPath = os.path.join(self.dataDir(), 'test_anim.ma')
        self.dstPath = os.path.join(self.dataDir(), 'test_load_replace_completely.anim')
        self.save()
        anim = mutils.Animation.fromPath(self.dstPath)
        anim.load(self.dstObjects)
        for frame in [1, 10, 24]:
            maya.cmds.currentTime(frame)
            for srcAttribute, dstAttribute in self.listAttr():
                if dstAttribute.exists():
                    self.assertEqual(srcAttribute.value(), dstAttribute.value(), 'Incorrect value for %s %s != %s' % (dstAttribute.fullname(), dstAttribute.value(), srcAttribute.value()))

    def test_bake_connected(self):
        """
        Test load animation.
        """
        srcPath = os.path.join(self.dataDir(), 'test_bake_connected.ma')
        dstPath = os.path.join(self.dataDir(), 'test_bake_connected.anim')
        srcObjects = ['srcSphere:group',
         'srcSphere:lockedNode',
         'srcSphere:offset',
         'srcSphere:sphere']
        dstObjects = ['dstSphere:group',
         'dstSphere:lockedNode',
         'dstSphere:offset',
         'dstSphere:sphere']
        self.open(path=srcPath)
        anim = mutils.Animation.fromObjects(srcObjects)
        anim.save(dstPath, bakeConnected=True)
        anim = mutils.Animation.fromPath(dstPath)
        anim.load(dstObjects)
        for frame in [1, 10, 24]:
            maya.cmds.currentTime(frame)
            for srcAttribute, dstAttribute in self.listAttr(srcObjects, dstObjects):
                self.assertEqual(srcAttribute.value(), dstAttribute.value(), 'Incorrect value for %s %s != %s' % (dstAttribute.fullname(), dstAttribute.value(), srcAttribute.value()))

    def test_load_replace(self):
        """
        Test load animation.
        """
        self.srcPath = os.path.join(self.dataDir(), 'test_anim.ma')
        self.dstPath = os.path.join(self.dataDir(), 'test_load_replace.anim')
        self.save()
        anim = mutils.Animation.fromPath(self.dstPath)
        anim.load(self.dstObjects, option=mutils.PasteOption.Replace, startFrame=5)

    def test_load_insert(self):
        """
        Test load animation.
        """
        self.srcPath = os.path.join(self.dataDir(), 'test_anim.ma')
        self.dstPath = os.path.join(self.dataDir(), 'test_load_insert.anim')
        self.save()
        anim = mutils.Animation.fromPath(self.dstPath)
        anim.load(self.dstObjects, option=mutils.PasteOption.Insert, startFrame=5)
