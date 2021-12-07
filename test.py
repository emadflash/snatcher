import unittest
from url_handler import Url, Preprocess_url

class test_url_handler(unittest.TestCase):
    def test_url_join(self):
        u = Url("https://example.com")
        self.assertEqual(u.join('/blah'), Url("https://example.com/blah"))
        self.assertEqual(u.join('blah'), Url("https://example.com/blah"))


if __name__ == '__main__':
    unittest.main()
