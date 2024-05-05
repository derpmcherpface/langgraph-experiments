# from: https://www.youtube.com/watch?v=R8KB-Zcynxc
# and: https://github.com/menloparklab/LangGraphJourney/blob/main/LangGraphLearning.ipynb

def function_1(input_1):
    #result=input_1 + " Hi "
    print("What is your question?")
    result=input()
    return result
from langchain_core.runnables import RunnableLambda
function_1_runnable = RunnableLambda(function_1)

def function_2(input_2):
    print("invoking model with question: " + input_2)
    return input_2
function2_runnable=RunnableLambda(function_2)

from langchain_community.chat_models import ChatOllama
model = ChatOllama(model="openhermes")

from langgraph.graph import Graph

# Define a Langchain graph
print("creating workflow")
workflow = Graph()

print("adding nodes")
workflow.add_node("node_1", function_1_runnable)
workflow.add_node("node_2", function2_runnable)
workflow.add_node("node_3", model) # models are runnables, i.e. valid nodes

print("adding edges")
workflow.add_edge('node_1', 'node_2')
workflow.add_edge('node_2', 'node_3')

workflow.set_entry_point("node_1")
workflow.set_finish_point("node_3")

print("compiling workflow")
app = workflow.compile()

print("invoking app")
result=app.invoke("") # consider removing input to function_1
print(result); 