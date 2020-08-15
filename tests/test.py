import unittest

class SampleTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_sample_method(self):
        expected = 1
        actual = 1
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()
