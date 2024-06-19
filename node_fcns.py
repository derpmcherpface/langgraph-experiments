    
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
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, FunctionMessage


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


@tool
def get_secret_message() -> str:
    "Get the secret message"
    return "abc123"


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
        print("Human input mode")
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
    tool_selection_result = chain.invoke({'input': state['question']})
    printr(Fore.GREEN +"tool selection:" +str(tool_selection_result))

    if tool_selection_result["name"] == "converse":
        pass

    elif tool_selection_result["name"] == "multiply":
        tool_invocation_result=add.invoke(tool_selection_result["arguments"])
        # See: https://github.com/langchain-ai/langchain/pull/22339
        #toolMessage=ToolMessage(content=str(tool_invocation_result), tool_call_id="1")
        toolMessage=AIMessage(content=str(tool_invocation_result))
        state["messages"].append(toolMessage)
        printr(Fore.RED + "chose multiply tool")
    

    state['tool_selection']=tool_selection_result
    return state

def invocation_node_fcn(model,state: dict):
    printr(Fore.BLUE + "running model invocation node fcn")

    from langchain_core.prompts import MessagesPlaceholder
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Give a short answer to the question given the context below"),
        MessagesPlaceholder("history"),
        ("human", "{question}")
    ]
    )

    prompt_invocation = prompt.invoke(
    {
        "history": state['messages'],
        "question": state['question']
    }
    )
    result = model.invoke(prompt_invocation)
    print("model invocation result: " + str(result))
    # add result content to agent state
    state['messages'].append(AIMessage(result.content))
    return state

def should_continue(state):
    #return "__end__"
    if not state['input_queue'].empty() or state["human_input_mode"]:
        print("input queue not empty or human input mode, returning to input_node")
        return "input_node"
    else:
        print("input queue empty, returning to __end__")
        return "__end__"