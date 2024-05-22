from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableLambda
from langgraph.graph import Graph
import queue
class CustomExecutor: 

    # static methods used as nodes in the graph
    def input_node_fcn(state): 
        print("What is your question?")
        #result=input()
        result="hello world!"
        state['messages'].append(result)
        state['question']=result
        return state
    
    def invoke_executor(self): 
        return self.model.invoke("Hi! how are you?")

    def __init__(self):
        print("Starting initialize custom executor")
        self.model = ChatOllama(model="openhermes")
        self.input_node_runnable = RunnableLambda(CustomExecutor.input_node_fcn)

        # messages key will be assigned as an empty array. 
        # We will append new messages as we pass along nodes.
        self.AgentState = {}
        self.AgentState["messages"] = []
        self.AgentState["question"] = ""

        self.input_queue = queue.Queue()

        self.workflow = Graph()
        self.workflow.add_node("input_node", self.input_node_runnable)
        self.workflow.set_entry_point("input_node")
        self.workflow.set_finish_point("input_node")
        self.app = self.workflow.compile()

        print("Custom executor initialized")


