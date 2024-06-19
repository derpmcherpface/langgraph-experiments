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
from node_fcns import *



class CustomExecutor: 

    def invoke(self) -> str: 
        result = self.app.invoke(self.AgentState)
        return result['messages'][-1] # return last response
    
    def add_input(self, message : str):
        self.AgentState["input_queue"].put(message)

    def set_human_input_mode(self, mode : bool):
        self.AgentState["human_input_mode"] = mode

    def __init__(self):
        
        print("Starting initialize custom executor")
        self.tools=[multiply]

        self.model = ChatOllama(model="openhermes")
        #self.model = self.model.bind_tools(self.tools)
        self.input_node_runnable = RunnableLambda(input_node_fcn)
        self.invocation_node_runnable = RunnableLambda(partial(invocation_node_fcn, self.model))
        self.tool_execution_node_runnable = RunnableLambda(partial(tool_execution_node_fcn, self.model))

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

        self.workflow.add_conditional_edges("invocation_node", should_continue)


        self.workflow.set_entry_point("input_node")
        #self.workflow.set_finish_point("invocation_node")
        self.app = self.workflow.compile()

        self.AgentState["human_input_mode"] = False

        self.converse_runnable  = RunnableLambda(partial(converse, self.model))

        self.tools = [multiply, converse, add, get_secret_message]
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
        

        print("System prompt: " + self.system_prompt)


        self.tool_selection_prompt =  ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("user", "{input}")]
        )

        # invocation node only has access to the agent state, so use 
        # it to pass the prompt. Can be avoided with a RunnableLambda
        # but this will do for now
        self.AgentState["tool_selection_prompt"] = self.tool_selection_prompt

        print("Custom executor initialized")


    def one_pass_execute(self, input: str="My carpet is green. What color is my carpet?") -> str:
        self.add_input(input)
        result = str(self.invoke())
        return result
    
    def get_state(self) -> dict:
        return self.AgentState
    
def main():
    print("hello world!")
    customExecutor = CustomExecutor()
    customExecutor.set_human_input_mode(True)
    customExecutor.invoke()
    
if __name__ == "__main__":
    main()