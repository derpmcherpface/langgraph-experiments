#From: https://medium.com/@lifanov.a.v/integrating-langgraph-with-ollama-for-advanced-llm-applications-d6c10262dafa

import operator
from datetime import datetime
from typing import Annotated, TypedDict, Union

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import create_react_agent
from langchain_community.chat_models import ChatOllama
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation

load_dotenv()

@tool
def get_now(format: str = "%Y-%m-%d %H:%M:%S"):
    """
    Get the current time
    """
    return datetime.now().strftime(format)


tools = [get_now]

tool_executor = ToolExecutor(tools)

class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


model = ChatOllama(model="openhermes")
prompt = hub.pull("hwchase17/react")
#print("the prompt is:\n" + prompt.template)


agent_runnable = create_react_agent(model, tools, prompt)
#prompt.input_schema.schema() 
#agent_runnable.input_schema.schema()


def execute_tools(state):
    print("Called `execute_tools`")
    messages = [state["agent_outcome"]]
    last_message = messages[-1]

    tool_name = last_message.tool

    print(f"Calling tool: {tool_name}")

    action = ToolInvocation(
        tool=tool_name,
        tool_input=last_message.tool_input
    )
    response = tool_executor.invoke(action)
    return {"intermediate_steps": [(state["agent_outcome"], response)]}


def run_agent(state):
    """
    #if you want to better manages intermediate steps
    inputs = state.copy()
    if len(inputs['intermediate_steps']) > 5:
        inputs['intermediate_steps'] = inputs['intermediate_steps'][-5:]
    """
    agent_outcome = agent_runnable.invoke(state)
    return {"agent_outcome": agent_outcome}


def should_continue(state):
    messages = [state["agent_outcome"]]
    last_message = messages[-1]
    if "Action" not in last_message.log:
        return "end"
    else:
        return "continue"
    
    
workflow = StateGraph(AgentState)

workflow.add_node("agent", run_agent)
workflow.add_node("action", execute_tools)


workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent", should_continue, {"continue": "action", "end": END}
)


workflow.add_edge("action", "agent")
app = workflow.compile()

input_text = "Whats the current time?"

inputs = {"input": input_text, "chat_history": []}
results = []

#from langchain_core.globals import set_debug
#set_debug(True)


#print(app.invoke(inputs))
from termcolor import colored
from langchain_core.tracers import ConsoleCallbackHandler

#for s in app.stream(inputs, config={'callbacks': [ConsoleCallbackHandler()]}):
for s in app.stream(inputs):
    result = list(s.values())[0]
    results.append(result)
    print(result)


# now parse with termcolor

app.get_graph().print_ascii()
graph=app.get_graph()

for res in results:
    print("----")
    res=colored(str(res),'blue')
    print(res)

