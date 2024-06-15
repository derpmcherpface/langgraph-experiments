    
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableLambda
from langgraph.graph import Graph
import queue
from functools import partial
from langchain_core.prompts import PromptTemplate
import sys, select
from langchain_core.tools import tool
from langchain.tools.render import render_text_description # to describe tools as a string 
from langchain_core.prompts import ChatPromptTemplate # crafts prompts for our llm
from langchain_core.output_parsers import JsonOutputParser # ensure JSON input for tools
from colorama import Fore, Style, Back
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


@tool
def add(first: int, second: int) -> int:
    "Add two integers."
    return first + second

@tool
def multiply(first: int, second: int) -> int:
    """Multiply two integers together."""
    return first * second

    # Consider creating this tool function without the decorator, as it 
    # creates problems with the the rendering of the tools where the args 
    # are evaluated for rendering before being partially evaluated
@tool
def converse(input: str, model) -> str:
    "Provide a natural language response using the user input."
    return model.invoke(input)


def state_to_context(state : dict):
    result=""
    for message in state["messages"]:
        result=result+'\n'+str(message)

    return result
    
def input_with_timeout(timeout):
    print("You have ten seconds to answer!")

    i, o, e = select.select( [sys.stdin], [], [], timeout)

    if (i):
        print("You said " + sys.stdin.readline().strip())
    else:
        print("You said nothing!")

def printr(s):
    print(s)
    print(Style.RESET_ALL)


def input_node_fcn(state: dict): 
    printr(Fore.BLUE + "running node input fcn")
    print("What is your question?")
    #result=input()
    if not state['input_queue'].empty():
        result = state['input_queue'].get()
        print("Simulated user input: " + str(result))
    else:
        result=input()
        print("User input: " + result)

    #CustomExecutor.input_with_timeout(10)
    state['messages'].append(HumanMessage(result))
    state['question']=result
    return state
    
def tool_execution_node_fcn(model,state: dict):
    #We can now wrap these tools in a simple LangGraph ToolNode.
    #  This class receives the list of messages
    #  (containing tool_calls, calls the tool(s) the LLM has requested to run,
    #  and returns the output as new ToolMessage(s).

    # -> We need to refactor invocation node to use AiMessage, HumanMessage, ToolMessage and 
    # MessagesPlaceholder 
    printr(Fore.BLUE + "running node tool_execution fcn")
    chain = state["tool_selection_prompt"] | model | JsonOutputParser()
    result = chain.invoke({'input': state['question']})
    printr(Fore.GREEN + str(result))
    state['tool_selection']=result
    return state

def invocation_node_fcn(model,state: dict):
    printr(Fore.BLUE + "running model invocation node fcn")

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
    
    print("prompt:" + str(resulting_prompt))

    result = model.invoke(str(resulting_prompt))

    # add result content to agent state
    state['messages'].append(AIMessage(result.content))
    print(result)
    return state

def should_continue(state):
    #return "__end__"
    if not state['input_queue'].empty() or state["human_input_mode"]:
        print("input queue not empty or human input mode, returning to input_node")
        return "input_node"
    else:
        print("input queue empty, returning to __end__")
        return "__end__"