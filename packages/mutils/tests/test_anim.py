#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\tests\test_anim.py
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
        anim = mutils.Animation.createFromObjects(self.srcObjects)
        anim.save(self.dstPath, compress=True, bakeConnected=bakeConnected)

    def test_older_version(self):
        """
        """
        srcPath = os.path.join(self.dataDir(), 'test_older_version.anim')
        a = mutils.Animation.createFromPath(srcPath)

    def test_load_replace_completely(self):
        """
        Test load animation.
        """
        self.srcPath = os.path.join(self.dataDir(), 'test_anim.ma')
        self.dstPath = os.path.join(self.dataDir(), 'test_load_replace_completely.anim')
        self.save()
        anim = mutils.Animation.createFromPath(self.dstPath)
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
        anim = mutils.Animation.createFromObjects(srcObjects)
        anim.save(dstPath, compress=True, bakeConnected=True)
        anim = mutils.Animation.createFromPath(dstPath)
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
        anim = mutils.Animation.createFromPath(self.dstPath)
        anim.load(self.dstObjects, option=mutils.Option.Replace, start=5)

    def test_load_insert(self):
        """
        Test load animation.
        """
        self.srcPath = os.path.join(self.dataDir(), 'test_anim.ma')
        self.dstPath = os.path.join(self.dataDir(), 'test_load_insert.anim')
        self.save()
        anim = mutils.Animation.createFromPath(self.dstPath)
        anim.load(self.dstObjects, option=mutils.Option.Insert, start=5)
