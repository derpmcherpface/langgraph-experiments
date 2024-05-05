# from: https://www.youtube.com/watch?v=R8KB-Zcynxc
# and: https://github.com/menloparklab/LangGraphJourney/blob/main/LangGraphLearning.ipynb

def function_1(input_1):
    result=input_1 + " Hi "
    return result
from langchain_core.runnables import RunnableLambda
function_1_runnable = RunnableLambda(function_1)

def function_2(input_2):
    result=input_2 + " there "
    return result

from langgraph.graph import Graph

# Define a Langchain graph
workflow = Graph()

workflow.add_node("node_1", function_1_runnable)
workflow.add_node("node_2", function_2)

workflow.add_edge('node_1', 'node_2')

workflow.set_entry_point("node_1")
workflow.set_finish_point("node_2")

app = workflow.compile()

result=app.invoke("Hello")
print(result); 

# Adding LLM Call 

from langchain_community.chat_models import ChatOllama

#chat = ChatOllama(model="openhermes", streaming=False, callbacks=[])
print("creating model...")
model = ChatOllama(model="openhermes")

print("invoking model...")
result=model.invoke("Hey There")
print(result)
print(result.content)


