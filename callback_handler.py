from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
#from langchain_openai import ChatOpenAI


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

from termcolor import colored

#Python doesn't recognize Dict and List as types by default;
# they are part of the typing module, which provides support for type hints.
from typing import Dict, List

class MyCustomHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(f"My custom handler, token: {token}")

    def on_llm_start(
        self, serialized: Dict[str, any], prompts: List[str], **kwargs: any
        ) -> any:
        print(colored("LLM start",'green'))
        """Run when LLM starts running."""

    def on_tool_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: any
        ) -> any:
        print(colored("Tool error",'red'))    
        """Run when tool errors."""

    def on_text(self, text: str, **kwargs: any) -> any:
        print(colored(text,'blue'))    
        """Run on arbitrary text."""

# To enable streaming, we pass in `streaming=True` to the ChatModel constructor
# Additionally, we pass in a list with our custom handler
#chat = ChatOpenAI(max_tokens=25, streaming=True, callbacks=[MyCustomHandler()])
chat = ChatOllama(model="openhermes", streaming=False, callbacks=[MyCustomHandler()])

chat.invoke([HumanMessage(content="Tell me a joke")])