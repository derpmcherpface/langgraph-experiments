#import react_prompts
from react_prompts import react_prompt
from langchain_community.llms import Ollama
#print(react_prompt)
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser # ensure JSON input for tools
from langchain_core.output_parsers import StrOutputParser

model = Ollama(model='mistral:instruct')


prompt_tempelate = PromptTemplate.from_template(react_prompt)
prompt = prompt_tempelate.format(tools=[], tool_names=[], chat_history="", input="hello", agent_scratchpad="")
#print(prompt)

#chain = prompt_tempelate | model | JsonOutputParser()
chain = prompt_tempelate | model | StrOutputParser()

# TODO: add all inputs demanded by prompt_template, inspect input schema
# TODO: ensure json output from model
# TODO: parse all outputs
# TODO: add mock tools
# TODO: loop
input="What is the weather like in california?"
result=chain.invoke({"input":input,"tools":[],"tool_names":[], "chat_history":"","agent_scratchpad":""})
print(result)