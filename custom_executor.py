from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableLambda
from langgraph.graph import Graph
class CustomExecutor: 

    # static methods used as nodes in the graph
    def input_node_fcn(state): 
        print("What is your question?")
        result=input()
        state['messages'].append(result)
        state['question']=result
        return state

    def __init__(self):
        print("Starting initialize custom executor")
        self.model = ChatOllama(model="openhermes")
        input_node_runnable = RunnableLambda(CustomExecutor.input_node_fcn)

        # messages key will be assigned as an empty array. 
        # We will append new messages as we pass along nodes.
        AgentState = {}
        AgentState["messages"] = []
        AgentState["question"] = ""

        workflow = Graph()
        workflow.add_node("input_node", input_node_runnable)
        workflow.set_entry_point("input_node")
        workflow.set_finish_point("input_node")
        app = workflow.compile()

        print("Custom executor initialized")


