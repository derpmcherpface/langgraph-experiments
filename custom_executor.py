from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableLambda
from langgraph.graph import Graph
import queue
from functools import partial
from langchain_core.prompts import PromptTemplate
import sys, select

class CustomExecutor: 
    def state_to_context(state : dict):
        result=""
        for message in state["messages"]:
            result=result+'\n'+message

        return result
    
    def input_with_timeout(timeout):
        print("You have ten seconds to answer!")

        i, o, e = select.select( [sys.stdin], [], [], 10 )

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
            result="hello world!"

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
    
    def invoke_executor(self) -> str: 
        result = self.app.invoke(self.AgentState)
        return result['messages'][-1] # return last response
    
    def add_input(self, message : str):
        self.AgentState["input_queue"].put(message)

    def __init__(self):
        
        print("Starting initialize custom executor")
        self.model = ChatOllama(model="openhermes")
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
        self.workflow.set_entry_point("input_node")
        self.workflow.set_finish_point("invocation_node")
        self.app = self.workflow.compile()

        print("Custom executor initialized")


    def one_pass_execute(self, input: str) -> str:
        self.add_input(input)
        result = self.invoke_executor()
        return result