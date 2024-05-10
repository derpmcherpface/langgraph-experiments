# from: https://www.youtube.com/watch?v=R8KB-Zcynxc
# and: https://github.com/menloparklab/LangGraphJourney/blob/main/LangGraphLearning.ipynb
from langchain_community.chat_models import ChatOllama
model = ChatOllama(model="openhermes")
# Input node function
def function_1(state):
    #result=input_1 + " Hi "
    print("What is your question?")
    result=input()
    #result="Who was Napoleon?"
    state['messages'].append(result)
    return state
from langchain_core.runnables import RunnableLambda
function_1_runnable = RunnableLambda(function_1)

# model invocation node function
def function_3(state):
    print("state: " + str(state))
    messages=state['messages']
    input_2=messages[-1]
    print("input_2:" + input_2)
    #response = model.invoke("Who was Napoleon?")
    response = model.invoke(input_2)
    print("response: " + str(response))
    return state
function_3_runnable=RunnableLambda(function_3)

def router(state):
    return "node_1"
    #return "__end__"

# assing AgentState as an empty dict 
AgentState = {}
# messages key will be assigned as an empty array. 
# We will append new messages as we pass along nodes.
AgentState["messages"] = []

from langgraph.graph import Graph

# Define a Langchain graph
print("creating workflow")
workflow = Graph()

print("adding nodes")
workflow.add_node("node_1", function_1_runnable)

workflow.add_node("node_3", function_3_runnable)

print("adding edges")
workflow.add_edge('node_1', 'node_3')
workflow.add_conditional_edges('node_3', router)
workflow.set_entry_point("node_1")
#workflow.set_finish_point("node_3")

print("compiling workflow")
app = workflow.compile()

print("invoking app")
result=app.invoke(AgentState)
#print(result); 