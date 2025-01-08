import unittest

from settings.settings import load_settings, get_setting


class TestSettings(unittest.TestCase):
    def test_load_settings(self):
        load_settings()
