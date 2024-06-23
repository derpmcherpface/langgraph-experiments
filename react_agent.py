# from: https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/#define-the-graph

# define model and tools
from typing import Literal

from langchain_core.tools import tool
#from langchain_openai import ChatOpenAI

from langchain_community.llms import Ollama # to use Ollama llms in langchain
#model = ChatOpenAI(model="gpt-4o", temperature=0)
model = Ollama(model='llama2')

@tool
def get_weather(city: str):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        return "It is raining in " + city
    
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
#from langchain_openai import OpenAI
# from https://python.langchain.com/v0.1/docs/modules/agents/agent_types/react/
print("hello world!")

#tools = [TavilySearchResults(max_results=1)]
tools=[get_weather]

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/react")

# Choose the LLM to use
#llm = OpenAI()
llm = Ollama(model='mistral:instruct')

# Construct the ReAct agent
agent = create_react_agent(llm, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

agent_executor.invoke({"input": "What is the weather like in san francisco?"})