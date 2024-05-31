import unittest
from custom_executor import CustomExecutor
import timeout_decorator

class TestSumTest(unittest.TestCase):

    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 3)), 6, "Should be 6")


    #@timeout_decorator.timeout(5)
    def test_init_custom_executor(self):
        self.customExecutor = CustomExecutor()
        self.customExecutor.add_input("My carpet is green. What color is my carpet?")
        print("response: " + str(self.customExecutor.invoke_executor()))


    def test_memory_custom_executor(self):
        self.customExecutor = CustomExecutor()
        self.customExecutor.add_input("My carpet is green.")
        self.response1=self.customExecutor.invoke_executor()
        print("response: " + str(self.response1))
        self.customExecutor.add_input("What color is my carpet?")
        self.response2=self.customExecutor.invoke_executor()
        print("response: " + str(self.response2))
        if str(self.response2).lower().find("green") != -1:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()