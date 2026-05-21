import unittest

from app_utils import get_available_destinations, get_default_destinations, DEFAULT_DESTINATIONS


class TestAppUtils(unittest.TestCase):
    def test_available_destinations_excludes_depot(self):
        self.assertNotIn("Pune", get_available_destinations("Pune"))
        self.assertNotIn("Mumbai", get_available_destinations("Mumbai"))
        self.assertNotIn("Ahmedabad", get_available_destinations("Ahmedabad"))

    def test_default_destinations_excludes_depot(self):
        self.assertEqual(get_default_destinations("Pune"), ["Mumbai", "Ahmedabad"])
        self.assertEqual(get_default_destinations("Mumbai"), ["Pune", "Ahmedabad"])
        self.assertEqual(get_default_destinations("Ahmedabad"), ["Mumbai", "Pune"])

    def test_default_destinations_using_fallback_defaults(self):
        self.assertEqual(get_default_destinations("Delhi"), DEFAULT_DESTINATIONS)

    def test_default_destinations_with_custom_defaults(self):
        custom_defaults = ["Pune", "Delhi"]
        self.assertEqual(get_default_destinations("Pune", defaults=custom_defaults), ["Delhi"])


if __name__ == "__main__":
    unittest.main()
