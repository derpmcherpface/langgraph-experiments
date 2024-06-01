import unittest
from custom_executor import CustomExecutor
import timeout_decorator

class TestSumTest(unittest.TestCase):

    def test_init_custom_executor(self):
        self.customExecutor = CustomExecutor()
        self.customExecutor.add_input("My carpet is green. What color is my carpet?")
        print("response: " + str(self.customExecutor.invoke_executor()))

    #@timeout_decorator.timeout(5)
    def test_reasoning_custom_executor(self):
        self.customExecutor = CustomExecutor()
        self.customExecutor.add_input("My carpet is green. What color is my carpet?")
        self.response2=self.customExecutor.invoke_executor()
        print("response: " + str(self.response2))
        if str(self.response2).lower().find("green") != -1:
            self.assertTrue(True)
        else:
            self.assertTrue(False)


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

    def test_one_pass_execute(self):
        self.customExecutor = CustomExecutor()
        result= self.customExecutor.one_pass_execute("test one pass execute")
        print(result)

if __name__ == '__main__':
    unittest.main()