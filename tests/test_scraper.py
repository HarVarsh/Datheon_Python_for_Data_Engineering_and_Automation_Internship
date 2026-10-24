
import unittest

from scraper import clean_price


class TestScraper(unittest.TestCase):

    def test_clean_price(self):
        self.assertEqual(clean_price("£51.77"), 51.77)

    def test_integer_price(self):
        self.assertEqual(clean_price("£10"), 10.0)

    def test_missing_price(self):
        self.assertIsNone(clean_price(None))

    def test_invalid_price(self):
        self.assertIsNone(clean_price("not available"))


if __name__ == "__main__":
    unittest.main()
