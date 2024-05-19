# experimenting with injecting context into prompts


from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage
model = ChatOllama(model="openhermes", streaming=True)

from langchain_core.prompts import ChatPromptTemplate





from langchain_core.prompts import PromptTemplate
# assing AgentState as an empty dict 
AgentState = {}
# messages key will be assigned as an empty array. 
# We will append new messages as we pass along nodes.
AgentState["messages"] = []
AgentState["messages"].append("User: What is your name?")
AgentState["messages"].append("Ai: my name is Steve")
AgentState["messages"].append("User: The carpet in my house is green")

def state_to_context(state):
    result=""
    for message in state["messages"]:
        result=result+'\n'+message

    return result

print(state_to_context(AgentState))

prompt_template = PromptTemplate.from_template(
"""Give a short answer to the question given the context below
---
Context: {context}
---
Question: {question}
Answer:
"""
)
#resulting_prompt=prompt_template.format(adjective="funny", content="chickens")
resulting_prompt=prompt_template.format(
    context=state_to_context(AgentState), 
    question="What color is my carpet?"
)
print(resulting_prompt)
result=model.invoke(resulting_prompt)
print(result)







#print(model.invoke(resulting_prompt))

#print(few_shot_prompt_template.format(query=query))
#result=model.invoke(dynamic_prompt_template.format(query=query))
#print(result)

