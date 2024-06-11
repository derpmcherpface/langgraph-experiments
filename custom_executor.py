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

def printr(s):
    print(s)
    print(Style.RESET_ALL)

class CustomExecutor: 

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
            result=result+'\n'+message

        return result
    
    def input_with_timeout(timeout):
        print("You have ten seconds to answer!")

        i, o, e = select.select( [sys.stdin], [], [], timeout)

        if (i):
            print("You said " + sys.stdin.readline().strip())
        else:
            print("You said nothing!")

    # static methods used as nodes in the graph



    def input_node_fcn(state: dict): 
        printr(Fore.BLUE + "running node input fcn")
        print("What is your question?")
        #result=input()
        if not state['input_queue'].empty():
            result = state['input_queue'].get()
        else:
            result=input()

        #CustomExecutor.input_with_timeout(10)
        state['messages'].append(result)
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
        chain = state["prompt"] | model | JsonOutputParser()
        result = chain.invoke({'input': state['question']})
        printr(Fore.GREEN + str(result))
        state['tool_selection']=result
        return state
    
    def invocation_node_fcn(model,state: dict):
        printr(Fore.BLUE + "running node invocation fcn")

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
        context=CustomExecutor.state_to_context(state), 
        question=state['question']
        )
        

        print("prompt:" + str(resulting_prompt))

        result = model.invoke(str(resulting_prompt))
        chain = state["prompt"] | model | JsonOutputParser()

        # move this to a prior chain of tool_invocation_node for choice, with only 
        # converse tool available. with conditional edges to tool execution nodes
        # only one tool available: converse (executed by invoke)

        #print(chain.invoke({'input': 'How are you?'}))
        #{'name': 'converse', 'arguments': {'input': 'How are you?', 'model': ''}}
        # -> construct the converse fcn as a runnablelambda with partial evaluation ( or use pydantic)

        #print(chain.invoke({'input': 'What is 3 times 23'}))
        #{'name': 'multiply', 'arguments': {'first': 3, 'second': 23}}


        # add result content to agent state
        state['messages'].append(result.content)
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
    
    def invoke(self) -> str: 
        result = self.app.invoke(self.AgentState)
        return result['messages'][-1] # return last response
    
    def add_input(self, message : str):
        self.AgentState["input_queue"].put(message)

    def set_human_input_mode(self, mode : bool):
        self.AgentState["human_input_mode"] = mode

    def __init__(self):
        
        print("Starting initialize custom executor")
        self.tools=[CustomExecutor.multiply]

        self.model = ChatOllama(model="openhermes")
        #self.model = self.model.bind_tools(self.tools)
        self.input_node_runnable = RunnableLambda(CustomExecutor.input_node_fcn)
        self.invocation_node_runnable = RunnableLambda(partial(CustomExecutor.invocation_node_fcn, self.model))
        self.tool_execution_node_runnable = RunnableLambda(partial(CustomExecutor.tool_execution_node_fcn, self.model))

        # messages key will be assigned as an empty array. 
        # We will append new messages as we pass along nodes.
        self.AgentState = {}
        self.AgentState["messages"] = []
        self.AgentState["question"] = ""

        self.AgentState["input_queue"] = queue.Queue()

        self.workflow = Graph()
        self.workflow.add_node("input_node", self.input_node_runnable)
        self.workflow.add_node("invocation_node", self.invocation_node_runnable)
        self.workflow.add_node("tool_execution_node", self.tool_execution_node_runnable)

        self.workflow.add_edge('input_node', 'tool_execution_node')
        self.workflow.add_edge('tool_execution_node', 'invocation_node')

        self.workflow.add_conditional_edges("invocation_node", CustomExecutor.should_continue)


        self.workflow.set_entry_point("input_node")
        #self.workflow.set_finish_point("invocation_node")
        self.app = self.workflow.compile()

        self.AgentState["human_input_mode"] = False

        self.converse_runnable  = RunnableLambda(partial(CustomExecutor.converse, self.model))

        self.tools = [CustomExecutor.multiply, CustomExecutor.converse, CustomExecutor.add]
        # This is a lousy hack to get rid of the "model" arg from the converse function
        # and is only used for "rendering" the tools for the system prompt.
        #  Tool invocations should be nodes 
        # unto themselves, but will do as a subchain in the model invocation node for now. 
        #self.tools = [CustomExecutor.multiply, CustomExecutor.add]
        self.rendered_tools = render_text_description(self.tools)
        self.system_prompt = f"""You are an assistant that has access to the following set of tools.
Here are the names and descriptions for each tool:

{self.rendered_tools}
Given the user input, return the name and input of the tool to use.
Return your response as a JSON blob with 'name' and 'arguments' keys.
The value associated with the 'arguments' key should be a dictionary of parameters."""
        
        self.prompt =  ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("user", "{input}")]
        )

        # invocation node only has access to the agent state, so use 
        # it to pass the prompt. Can be avoided with a RunnableLambda
        # but this will do for now
        self.AgentState["prompt"] = self.prompt

        print("Custom executor initialized")


    def one_pass_execute(self, input: str="My carpet is green. What color is my carpet?") -> str:
        self.add_input(input)
        result = self.invoke()
        return result
    
    def get_state(self) -> dict:
        return self.AgentState
    
def main():
    print("hello world!")
    customExecutor = CustomExecutor()
    #customExecutor.set_human_input_mode(True)
    customExecutor.invoke()
    
if __name__ == "__main__":
    main()