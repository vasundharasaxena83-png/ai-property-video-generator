import unittest
from script_generator import generate_scenes, validate_property

class ScriptGeneratorTests(unittest.TestCase):
    def test_scene_generation_uses_supplied_facts(self):
        scenes = generate_scenes("Oak House", "Pune", "₹50 lakh", "Apartment",
                                 ["Balcony", "Modular kitchen"], "Book a visit")
        captions = [s["caption"] for s in scenes]
        self.assertIn("Discover Oak House", captions)
        self.assertIn("Located in Pune", captions)
        self.assertIn("Modular kitchen", captions)
        self.assertIn("Book a visit", captions)

    def test_validation_catches_missing_details_and_images(self):
        errors = validate_property("", "", "", "", [], [])
        self.assertGreaterEqual(len(errors), 6)
        self.assertTrue(any("at least 4" in e for e in errors))

    def test_validation_accepts_valid_input(self):
        errors = validate_property("Oak House", "Pune", "₹50 lakh",
                                   "Apartment", ["Balcony"], [1,2,3,4])
        self.assertEqual(errors, [])

if __name__ == "__main__":
    unittest.main()
