import unittest
from custom_executor import CustomExecutor
import timeout_decorator

class CustomExecutorTests(unittest.TestCase):

    def test_init_custom_executor(self):
        self.customExecutor = CustomExecutor()
        self.customExecutor.add_input("My carpet is green. What color is my carpet?")
        print("response: " + str(self.customExecutor.invoke()))

    #@timeout_decorator.timeout(5)
    def test_reasoning_custom_executor(self):
        self.customExecutor = CustomExecutor()
        self.customExecutor.add_input("My carpet is green. What color is my carpet?")
        self.response2=self.customExecutor.invoke()
        print("response: " + str(self.response2))
        if str(self.response2).lower().find("green") != -1:
            self.assertTrue(True)
        else:
            self.assertTrue(False)


    def test_memory_custom_executor(self):
        self.customExecutor = CustomExecutor()
        self.customExecutor.add_input("My carpet is green.")
        self.response1=self.customExecutor.invoke()
        print("response: " + str(self.response1))
        self.customExecutor.add_input("What color is my carpet?")
        self.response2=self.customExecutor.invoke()
        print("response: " + str(self.response2))
        if str(self.response2).lower().find("green") != -1:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_one_pass_execute(self):
        self.customExecutor = CustomExecutor()
        result= self.customExecutor.one_pass_execute("test one pass execute")
        print(result)

    def test_addition_tool_selection(self):
        self.customExecutor = CustomExecutor()
        result= self.customExecutor.one_pass_execute("What is 1+1?")
        state = self.customExecutor.get_state()
        self.assertTrue(state['tool_selection']['name'] == 'add')
        print(result)

    def test_multiplication_tool_selection(self):
        self.customExecutor = CustomExecutor()
        result= self.customExecutor.one_pass_execute("What is 5 multiplied by 4?")
        state = self.customExecutor.get_state()
        self.assertTrue(state['tool_selection']['name'] == 'multiply')
        print(result)


    def test_secret_question_tool_selection(self):
        self.customExecutor = CustomExecutor()
        result= self.customExecutor.one_pass_execute("What is the answer to the secret question?")
        state = self.customExecutor.get_state()
        print("tool selection: " + str(state['tool_selection']))
        #self.assertTrue(state['tool_selection']['name'] == 'multiply')
        print(result)

        #TODO: add test for results

    def test_converse_tool_selection(self):
        self.customExecutor = CustomExecutor()
        result= self.customExecutor.one_pass_execute("Hi! How are you?")
        state = self.customExecutor.get_state()
        self.assertTrue(state['tool_selection']['name'] == 'converse')
        print(result)

    def test_one_pass_execute_default_input(self):
        self.customExecutor = CustomExecutor()
        result= self.customExecutor.one_pass_execute()
        print(result)

if __name__ == '__main__':
    unittest.main()