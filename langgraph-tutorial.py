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
    #result=input_2
    #return result #passthrough, invoke model here
    #response = model.invoke(input_2)
    print("invoking model with question:")

function2_runnable=RunnableLambda(function_2)

from langgraph.graph import Graph

# Define a Langchain graph
print("creating workflow")
workflow = Graph()

print("adding nodes")
workflow.add_node("node_1", function_1_runnable)
workflow.add_node("node_2", function2_runnable)

print("adding edges")
workflow.add_edge('node_1', 'node_2')

workflow.set_entry_point("node_1")
workflow.set_finish_point("node_2")

print("compiling workflow")
app = workflow.compile()

print("invoking app")
result=app.invoke("Hello")
print(result); 

# Adding LLM Call 

#from langchain_community.chat_models import ChatOllama

#chat = ChatOllama(model="openhermes", streaming=False, callbacks=[])
#print("creating model...")
#model = ChatOllama(model="openhermes")

#print("invoking model...")
#result=model.invoke("Hey There")
#result=app.invoke("Hey there")
#print(result)
#print(result.content)


