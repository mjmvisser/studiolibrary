#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/mutils\tests\__init__.py
"""
# Example:
# RUN TEST SUITE
import mutils.tests
reload(mutils.tests)
mutils.tests.run()
"""
import unittest
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(funcName)s: %(message)s', filemode='w')

def suite():
    """
    :rtype: unittest.TestSuite
    """
    import test_pose
    import test_anim
    import test_match
    suite_ = unittest.TestSuite()
    suite_.addTest(test_match.TestMatch('test_match1'))
    suite_.addTest(test_match.TestMatch('test_match2'))
    suite_.addTest(test_match.TestMatch('test_match3'))
    suite_.addTest(test_match.TestMatch('test_match4'))
    suite_.addTest(test_match.TestMatch('test_match5'))
    suite_.addTest(test_match.TestMatch('test_match6'))
    suite_.addTest(test_match.TestMatch('test_match7'))
    suite_.addTest(test_match.TestMatch('test_match8'))
    suite_.addTest(test_match.TestMatch('test_match9'))
    suite_.addTest(test_match.TestMatch('test_match10'))
    suite_.addTest(test_match.TestMatch('test_match11'))
    suite_.addTest(test_match.TestMatch('test_match12'))
    suite_.addTest(test_match.TestMatch('test_match13'))
    suite_.addTest(test_match.TestMatch('test_match14'))
    suite_.addTest(test_match.TestMatch('test_match15'))
    suite_.addTest(test_match.TestMatch('test_match16'))
    suite_.addTest(test_match.TestMatch('test_match17'))
    suite_.addTest(test_pose.TestPose('test_save'))
    suite_.addTest(test_pose.TestPose('test_load'))
    suite_.addTest(test_pose.TestPose('test_blend'))
    suite_.addTest(test_pose.TestPose('test_select'))
    suite_.addTest(test_pose.TestPose('test_older_version'))
    suite_.addTest(test_anim.TestAnim('test_load_insert'))
    suite_.addTest(test_anim.TestAnim('test_older_version'))
    suite_.addTest(test_anim.TestAnim('test_load_replace'))
    suite_.addTest(test_anim.TestAnim('test_bake_connected'))
    suite_.addTest(test_anim.TestAnim('test_load_replace_completely'))
    return suite_


def run():
    """
    """
    tests = unittest.TextTestRunner()
    tests.run(suite())
