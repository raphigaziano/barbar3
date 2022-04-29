import unittest
from barbarian.targetting import TargettingInfo, TargetMode


class TestTargettingInfo(unittest.TestCase):

    def test_mode_defaults_to_usable(self):
        target_info = TargettingInfo()
        self.assertEqual(TargetMode.USABLE, target_info.mode)

    def test_requires_prompt(self):

        target_info = TargettingInfo(mode=TargetMode.USABLE)
        self.assertFalse(target_info.requires_prompt)

        target_info = TargettingInfo(mode=TargetMode.ACTOR)
        self.assertFalse(target_info.requires_prompt)

        target_info = TargettingInfo(mode=TargetMode.DIR)
        self.assertTrue(target_info.requires_prompt)

        target_info = TargettingInfo(mode=TargetMode.POS)
        self.assertTrue(target_info.requires_prompt)

