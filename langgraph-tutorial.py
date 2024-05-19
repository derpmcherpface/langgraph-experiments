from functools import partial
# from: https://www.youtube.com/watch?v=R8KB-Zcynxc
# and: https://github.com/menloparklab/LangGraphJourney/blob/main/LangGraphLearning.ipynb
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage
model = ChatOllama(model="openhermes")

def state_to_context(state):
    result=""
    for message in state["messages"]:
        result=result+'\n'+message

    return result

# Input node function
def function_1(state):
    #result=input_1 + " Hi "
    print("What is your question?")
    result=input()
    #result="Who was Napoleon?"
    state['messages'].append(result)
    state['question']=result
    return state


# model invocation node function
def function_3(model,state):
    print("state: " + str(state))
    messages=state['messages']
    #input_2=messages[-1] # Create a proper prompt here instead with 
    input_2=state['question']
    # context from the agent state
    print("input_2:" + input_2)
    from langchain_core.prompts import PromptTemplate
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
    context=state_to_context(state), 
    question=state['question']
    )
    #print(state_to_context(AgentState))
    print("prompt:" + str(resulting_prompt))
    #response = model.invoke("Who was Napoleon?")
    response = model.invoke(str(resulting_prompt))
    print("response: " + str(response))
    return state

def router(state):
    return "node_1"
    #return "__end__"

def main(): 


    from langchain_core.runnables import RunnableLambda
    function_1_runnable = RunnableLambda(function_1)
    function_3_runnable=RunnableLambda(partial(function_3,model))


    print("Hello world!")
    AgentState = {}
    # messages key will be assigned as an empty array. 
    # We will append new messages as we pass along nodes.
    AgentState["messages"] = []
    AgentState["question"] = ""

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

if __name__ == "__main__":
    main()
# assing AgentState as an empty dict 
