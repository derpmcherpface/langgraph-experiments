import unittest
from custom_executor import CustomExecutor

class TestSumTest(unittest.TestCase):

    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 3)), 6, "Should be 6")


    def test_init_custom_executor(self):
        self.customExecutor = CustomExecutor()
        print("response: " + str(self.customExecutor.invoke_executor()))

if __name__ == '__main__':
    unittest.main()