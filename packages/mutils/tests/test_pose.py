#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\tests\test_pose.py
"""
# Released subject to the BSD License
# Please visit http://www.voidspace.org.uk/python/license.shtml
#
# Copyright (c) 2014, Kurt Rathjen
# All rights reserved.
# Comments, suggestions and bug reports are welcome.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
   # * Redistributions of source code must retain the above copyright
   #   notice, this list of conditions and the following disclaimer.
   # * Redistributions in binary form must reproduce the above copyright
   # notice, this list of conditions and the following disclaimer in the
   # documentation and/or other materials provided with the distribution.
   # * Neither the name of Kurt Rathjen nor the
   # objects of its contributors may be used to endorse or promote products
   # derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY KURT RATHJEN  ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL KURT RATHJEN BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""
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
        pose = mutils.Pose.createFromObjects(self.srcObjects)
        pose.save(self.dstPath)

    def test_load(self):
        """
        Test load types.
        """
        self.open()
        pose = mutils.Pose.createFromPath(self.dstPath)
        pose.load(self.dstObjects)
        for srcAttribute, dstAttribute in self.listAttr():
            self.assertEqual(srcAttribute.value(), dstAttribute.value(), 'Incorrect value for %s %s != %s' % (dstAttribute.fullname(), dstAttribute.value(), srcAttribute.value()))

    def test_older_version(self):
        """
        """
        srcPath = os.path.join(self.dataDir(), 'test_older_version.dict')
        dstPath = os.path.join(self.dataDir(), 'test_older_version.json')
        pose = mutils.Pose.createFromPath(srcPath)
        print pose.objects()

    def test_non_unique_names(self):
        """
        """
        srcPath = os.path.join(self.dataDir(), 'test_non_unique_names.ma')
        dstPath = os.path.join(self.dataDir(), 'test_non_unique_names.pose')
        srcObjects = ['srcSphere:lockedNode', 'srcSphere:offset', 'srcSphere:sphere']
        dstObjects = ['lockedNode', 'offset', 'sphere']
        self.open(path=srcPath)
        pose = mutils.Pose.createFromObjects(srcObjects)
        pose.save(dstPath)
        pose = mutils.Pose.createFromPath(dstPath)
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

            pose = mutils.Pose.createFromPath(self.dstPath)
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
        pose = mutils.Pose.createFromPath(self.dstPath)
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
        pose = mutils.Pose.createFromPath(self.dstPath)
        self.assertEqual(pose.count(), len(self.srcObjects))
