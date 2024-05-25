from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableLambda
from langgraph.graph import Graph
import queue
from functools import partial
class CustomExecutor: 

    # static methods used as nodes in the graph
    def input_node_fcn(state): 
        print("What is your question?")
        #result=input()
        result="hello world!"
        state['messages'].append(result)
        state['question']=result
        return state
    
    def invocation_node_fcn(model,state):
        print("running node invocation fcn")
        return state
    
    def invoke_executor(self): 
        return self.app.invoke(self.AgentState)

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

        self.input_queue = queue.Queue()

        self.workflow = Graph()
        self.workflow.add_node("input_node", self.input_node_runnable)
        self.workflow.add_node("invocation_node", self.invocation_node_runnable)
        self.workflow.add_edge('input_node', 'invocation_node')
        self.workflow.set_entry_point("input_node")
        self.workflow.set_finish_point("invocation_node")
        self.app = self.workflow.compile()

        print("Custom executor initialized")


