#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.6.14/build27/studiolibrary/packages/mutils\tests\test_match.py
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
import mutils
import test_base

class TestMatch(test_base.TestBase):

    def setUp(self):
        """
        """
        pass

    def matchObjects(self, expectedResult, srcObjects = None, dstObjects = None, dstNamespaces = None):
        """
        """
        result = []
        for srcNode, dstNode in mutils.matchObjects(srcObjects, dstObjects=dstObjects, dstNamespaces=dstNamespaces):
            result.append((srcNode.name(), dstNode.name()))

        if result != expectedResult:
            raise Exception('Result does not match the expected result: %s != %s' % (str(result), expectedResult))

    def test_match0(self):
        """
        Test no matches
        """
        srcObjects = ['control2', 'control1', 'control3']
        dstObjects = ['control4', 'control5', 'control6']
        expectedResult = []
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match1(self):
        """
        Test simple match
        """
        srcObjects = ['control2', 'control1', 'control3']
        dstObjects = ['control1', 'control2', 'control3']
        expectedResult = [('control2', 'control2'), ('control1', 'control1'), ('control3', 'control3')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match2(self):
        """
        """
        srcObjects = ['control1']
        dstObjects = ['character1:control1', 'character2:control1']
        expectedResult = [('control1', 'character1:control1'), ('control1', 'character2:control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match3(self):
        """
        """
        srcObjects = ['control1']
        dstNamespaces = ['character1', 'character2']
        expectedResult = [('control1', 'character1:control1'), ('control1', 'character2:control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match4(self):
        """
        """
        srcObjects = ['character1:control1']
        dstNamespaces = ['']
        expectedResult = [('character1:control1', 'control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match5(self):
        """
        Test namespace
        Test short name
        Test multiple namespaces in source objects
        """
        srcObjects = ['character1:control1', 'character1:control2']
        dstNamespaces = ['character2']
        expectedResult = [('character1:control1', 'character2:control1'), ('character1:control2', 'character2:control2')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match6(self):
        """
        Test namespace
        Test long name
        Test namespace in source objects
        Test namespace that is not in source objects
        """
        srcObjects = ['character1:group1|character1:control1', 'character1:group2|character1:control1']
        dstNamespaces = ['character2']
        expectedResult = [('character1:group1|character1:control1', 'character2:group1|character2:control1'), ('character1:group2|character1:control1', 'character2:group2|character2:control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match7(self):
        """
        Test namespace
        Test multiple namespaces in source objects
        Test only one destination namespace
        """
        srcObjects = ['character1:control1', 'character2:control1']
        dstNamespaces = ['character2']
        expectedResult = [('character2:control1', 'character2:control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match8(self):
        """
        Test multiple namespaces in source objects
        Test namespace that is not in source objects
        """
        srcObjects = ['character1:control1', 'character2:control1']
        dstNamespaces = ['character3']
        expectedResult = [('character1:control1', 'character3:control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match9(self):
        """
        """
        srcObjects = ['character1:group1|character1:control1', 'character1:group1|character1:control2']
        dstObjects = ['group1|control1', 'group1|control2']
        expectedResult = [('character1:group1|character1:control1', 'group1|control1'), ('character1:group1|character1:control2', 'group1|control2')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match10(self):
        """
        WARNING: The expected result is a little strange.
        It will always match source objects without a namespace first.
        expectedResult = [("group1|control1", "character2:group1|character2:control1")]
        NOT
        expectedResult = [("character1:group1|character1:control1", "character2:group1|character2:control1")]
        """
        srcObjects = ['character1:group1|character1:control1', 'group1|control1']
        dstNamespaces = ['character2']
        expectedResult = [('group1|control1', 'character2:group1|character2:control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match11(self):
        """
        Match long name to short name.
        """
        srcObjects = ['|grpEyeAllLf|grpLidTpLf|ctlLidTpLf']
        dstObjects = ['ctlLidTpLf']
        expectedResult = [('|grpEyeAllLf|grpLidTpLf|ctlLidTpLf', 'ctlLidTpLf')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match12(self):
        """
        Match short name to long name.
        """
        srcObjects = ['ctlLidTpLf']
        dstObjects = ['|grpEyeAllLf|grpLidTpLf|ctlLidTpLf']
        expectedResult = [('ctlLidTpLf', '|grpEyeAllLf|grpLidTpLf|ctlLidTpLf')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match13(self):
        """
        Match short name to long name with namespace.
        """
        srcObjects = ['ctlLidTpLf']
        dstObjects = ['|malcolm:grpEyeAllLf|malcolm:grpLidTpLf|malcolm:ctlLidTpLf']
        expectedResult = [('ctlLidTpLf', '|malcolm:grpEyeAllLf|malcolm:grpLidTpLf|malcolm:ctlLidTpLf')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match14(self):
        """
        Match long name to short name with namespace.
        """
        srcObjects = ['|malcolm:grpEyeAllLf|malcolm:grpLidTpLf|malcolm:ctlLidTpLf']
        dstObjects = ['ctlLidTpLf']
        expectedResult = [('|malcolm:grpEyeAllLf|malcolm:grpLidTpLf|malcolm:ctlLidTpLf', 'ctlLidTpLf')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match15(self):
        """
        Testing multiple source namespace to only one destination namespace. They should not merge.
        """
        srcObjects = ['character1:group1|character1:control1', 'character2:group1|character2:control2']
        dstObjects = ['group1|control1', 'group1|control2']
        expectedResult = [('character1:group1|character1:control1', 'group1|control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match16(self):
        """
        Testing multiple source namespace and destination namespaces
        """
        srcObjects = ['character1:group1|character1:control1', 'character2:group1|character2:control1', 'character3:group1|character3:control1']
        dstObjects = ['character3:group1|character3:control1', 'character1:group1|character1:control1', 'character2:group1|character2:control1']
        expectedResult = [('character1:group1|character1:control1', 'character1:group1|character1:control1'), ('character3:group1|character3:control1', 'character3:group1|character3:control1'), ('character2:group1|character2:control1', 'character2:group1|character2:control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match17(self):
        """
        Testing multiple source namespace and destination namespaces.
        """
        srcObjects = ['character1:group1|character1:control1', 'group1|control1', 'character3:group1|character3:control1']
        dstObjects = ['character3:group1|character3:control1', 'character1:group1|character1:control1', 'group1|control1']
        expectedResult = [('group1|control1', 'group1|control1'), ('character1:group1|character1:control1', 'character1:group1|character1:control1'), ('character3:group1|character3:control1', 'character3:group1|character3:control1')]
        self.matchObjects(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)
