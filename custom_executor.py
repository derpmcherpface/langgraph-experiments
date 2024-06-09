from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableLambda
from langgraph.graph import Graph
import queue
from functools import partial
from langchain_core.prompts import PromptTemplate
import sys, select
from langchain_core.tools import tool
from langchain.tools.render import render_text_description # to describe tools as a string 

class CustomExecutor: 

    @tool
    def add(first: int, second: int) -> int:
        "Add two integers."
        return first + second
    
    @tool
    def multiply(first: int, second: int) -> int:
        """Multiply two integers together."""
        return first * second

    @tool
    def converse(input: str, model) -> str:
        "Provide a natural language response using the user input."
        return model.invoke(input)


    def state_to_context(state : dict):
        result=""
        for message in state["messages"]:
            result=result+'\n'+message

        return result
    
    def input_with_timeout(timeout):
        print("You have ten seconds to answer!")

        i, o, e = select.select( [sys.stdin], [], [], timeout)

        if (i):
            print("You said " + sys.stdin.readline().strip())
        else:
            print("You said nothing!")

    # static methods used as nodes in the graph
    def input_node_fcn(state: dict): 
        print("What is your question?")
        #result=input()
        if not state['input_queue'].empty():
            result = state['input_queue'].get()
        else:
            result=input()

        #CustomExecutor.input_with_timeout(10)
        state['messages'].append(result)
        state['question']=result
        return state
    
    def invocation_node_fcn(model,state: dict):
        print("running node invocation fcn")

        prompt_template = PromptTemplate.from_template(
"""Give a short answer to the question given the context below
---
Context: {context}
---
Question: {question}
Answer:
"""
        )
        resulting_prompt=prompt_template.format(
        context=CustomExecutor.state_to_context(state), 
        question=state['question']
        )
        

        print("prompt:" + str(resulting_prompt))

        result = model.invoke(str(resulting_prompt))
        # add result content to agent state
        state['messages'].append(result.content)
        print(result)
        return state
    
    def should_continue(state):
        #return "__end__"
        if not state['input_queue'].empty() or state["human_input_mode"]:
            print("input queue not empty or human input mode, returning to input_node")
            return "input_node"
        else:
            print("input queue empty, returning to __end__")
            return "__end__"
    
    def invoke(self) -> str: 
        result = self.app.invoke(self.AgentState)
        return result['messages'][-1] # return last response
    
    def add_input(self, message : str):
        self.AgentState["input_queue"].put(message)

    def set_human_input_mode(self, mode : bool):
        self.AgentState["human_input_mode"] = mode

    def __init__(self):
        
        print("Starting initialize custom executor")
        self.tools=[CustomExecutor.multiply]

        self.model = ChatOllama(model="openhermes")
        #self.model = self.model.bind_tools(self.tools)
        self.input_node_runnable = RunnableLambda(CustomExecutor.input_node_fcn)
        self.invocation_node_runnable = RunnableLambda(partial(CustomExecutor.invocation_node_fcn, self.model))

        # messages key will be assigned as an empty array. 
        # We will append new messages as we pass along nodes.
        self.AgentState = {}
        self.AgentState["messages"] = []
        self.AgentState["question"] = ""

        self.AgentState["input_queue"] = queue.Queue()

        self.workflow = Graph()
        self.workflow.add_node("input_node", self.input_node_runnable)
        self.workflow.add_node("invocation_node", self.invocation_node_runnable)
        self.workflow.add_edge('input_node', 'invocation_node')
        self.workflow.add_conditional_edges("invocation_node", CustomExecutor.should_continue)


        self.workflow.set_entry_point("input_node")
        #self.workflow.set_finish_point("invocation_node")
        self.app = self.workflow.compile()

        self.AgentState["human_input_mode"] = False

        self.tools = [CustomExecutor.multiply, CustomExecutor.converse, CustomExecutor.add]
        self.rendered_tools = render_text_description(self.tools)

        print("Custom executor initialized")


    def one_pass_execute(self, input: str="My carpet is green. What color is my carpet?") -> str:
        self.add_input(input)
        result = self.invoke()
        return result
    
def main():
    print("hello world!")
    customExecutor = CustomExecutor()
    customExecutor.set_human_input_mode(True)
    customExecutor.invoke()
    
if __name__ == "__main__":
    main()