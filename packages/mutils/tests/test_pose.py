#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/mutils\tests\test_pose.py
import os
import mutils
import maya.cmds
import test_base

class TestPose(test_base.TestBase):

    def setUp(self):
        """
        """
        self.srcPath = os.path.join(self.dataDir(), 'test_pose.ma')
        self.dstPath = os.path.join(self.dataDir(), 'test_pose.pose')

    def test_save(self):
        """
        Test save pose.
        """
        self.open()
        pose = mutils.Pose.fromObjects(self.srcObjects)
        pose.save(self.dstPath)

    def test_load(self):
        """
        Test load types.
        """
        self.open()
        pose = mutils.Pose.fromPath(self.dstPath)
        pose.load(self.dstObjects)
        for srcAttribute, dstAttribute in self.listAttr():
            self.assertEqual(srcAttribute.value(), dstAttribute.value(), 'Incorrect value for %s %s != %s' % (dstAttribute.fullname(), dstAttribute.value(), srcAttribute.value()))

    def test_older_version(self):
        """
        """
        srcPath = os.path.join(self.dataDir(), 'test_older_version.dict')
        dstPath = os.path.join(self.dataDir(), 'test_older_version.json')
        pose = mutils.Pose.fromPath(srcPath)
        print pose.objects()

    def test_non_unique_names(self):
        """
        """
        srcPath = os.path.join(self.dataDir(), 'test_non_unique_names.ma')
        dstPath = os.path.join(self.dataDir(), 'test_non_unique_names.pose')
        srcObjects = ['srcSphere:lockedNode', 'srcSphere:offset', 'srcSphere:sphere']
        dstObjects = ['lockedNode', 'offset', 'sphere']
        self.open(path=srcPath)
        pose = mutils.Pose.fromObjects(srcObjects)
        pose.save(dstPath)
        pose = mutils.Pose.fromPath(dstPath)
        pose.load(dstObjects)
        for srcAttribute, dstAttribute in self.listAttr(srcObjects, dstObjects):
            self.assertEqual(srcAttribute.value(), dstAttribute.value(), 'Incorrect value for %s %s != %s' % (dstAttribute.fullname(), dstAttribute.value(), srcAttribute.value()))

    def test_blend(self):
        """
        Test pose blending. At the moment this only tests float attribute types
        """
        self.open()
        for blend in [10,
         30,
         70,
         90]:
            dstObjects = {}
            for srcAttribute, dstAttribute in self.listAttr():
                if srcAttribute.type == 'float':
                    dstObjects[dstAttribute.fullname()] = (srcAttribute.value(), dstAttribute.value())

            pose = mutils.Pose.fromPath(self.dstPath)
            pose.load(self.dstObjects, blend=blend)
            for dstFullname in dstObjects.keys():
                srcValue, dstValue = dstObjects[dstFullname]
                value = (srcValue - dstValue) * (blend / 100.0)
                value = dstValue + value
                self.assertEqual(value, maya.cmds.getAttr(dstFullname), 'Incorrect value for %s %s != %s' % (dstFullname, value, maya.cmds.getAttr(dstFullname)))

    def test_select(self):
        """
        Test select content
        """
        self.open()
        pose = mutils.Pose.fromPath(self.dstPath)
        pose.select(namespaces=self.dstNamespaces)
        selection = maya.cmds.ls(selection=True)
        for dstName in self.dstObjects:
            if dstName not in selection:
                self.assertEqual(False)
                print 'Did not select %s' % dstName

    def test_count(self):
        """
        Test select content
        """
        self.open()
        pose = mutils.Pose.fromPath(self.dstPath)
        self.assertEqual(pose.count(), len(self.srcObjects))
