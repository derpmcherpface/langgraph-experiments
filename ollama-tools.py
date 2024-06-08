# following https://medium.com/pythoneers/power-up-ollama-chatbots-with-tools-113ed8229a7a
import streamlit as st # to render the user interface.
from langchain_community.llms import Ollama # to use Ollama llms in langchain
from langchain_core.prompts import ChatPromptTemplate # crafts prompts for our llm
from langchain_community.chat_message_histories import\
StreamlitChatMessageHistory # stores message history
from langchain_core.tools import tool # tools for our llm
from langchain.tools.render import render_text_description # to describe tools as a string 
from langchain_core.output_parsers import JsonOutputParser # ensure JSON input for tools
from operator import itemgetter # to retrieve specific items in our chain.

# Set up the LLM which will power our application.
model = Ollama(model='mistral:instruct')

@tool
def add(first: int, second: int) -> int:
    "Add two integers."
    return first + second

print(add.name)
print(add.description)
print(add.args)

add.invoke({'first':3, 'second':6})

@tool
def multiply(first: int, second: int) -> int:
    """Multiply two integers together."""
    return first * second

@tool
def converse(input: str) -> str:
    "Provide a natural language response using the user input."
    return model.invoke(input)

tools = [add, multiply, converse]
rendered_tools = render_text_description(tools)
print(rendered_tools)

system_prompt = f"""You are an assistant that has access to the following set of tools.
Here are the names and descriptions for each tool:

{rendered_tools}
Given the user input, return the name and input of the tool to use.
Return your response as a JSON blob with 'name' and 'arguments' keys.
The value associated with the 'arguments' key should be a dictionary of parameters."""

prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("user", "{input}")]
)

chain = prompt | model | JsonOutputParser()

print(chain.invoke({'input': 'What is 3 times 23'}))

print(chain.invoke({'input': 'How are you today?'}))
#Looks like our LLM is choosing the right tool for each input. But how do we actually run the tool to return a response to the user?
# Define a function which returns the chosen tool
def tool_chain(model_output):
    tool_map = {tool.name: tool for tool in tools}
    chosen_tool = tool_map[model_output["name"]]
    return itemgetter("arguments") | chosen_tool
#This function:
'''
Takes the model output e.g. {‘name’: ‘multiply’, ‘arguments’: {‘first’: 3, ‘second’: 23}}.
Creates a dictionary mapping of the tools e.g. {'add': <tool_object>, 'multiply': <tool_object>, 'converse': <tool_object>}.
Selects the chosen tool based on the value associated with the ‘name’ key of the model output e.g. 'multiply'
Returns a runnable that passes the arguments e.g. {‘first’: 3, ‘second’: 23} to the chosen tool.
We can add this to our chain and test our LLM with tools.'''

chain = prompt | model | JsonOutputParser() | tool_chain
print(chain.invoke({'input': 'What is 3 times 23'}))

#Bingo! Our LLM is using its tools to get to the right answer.

#Now its time to turn this chain into an intelligent chatbot.

#First, we configure the Streamlit chat history:



# Set up message history.
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("I can add, multiply, or just chat! How can I help you?")


# Set the page title.
st.title("Chatbot with tools")

# Render the chat history.
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

    # React to user input
if input := st.chat_input("What is up?"):
# Display user input and save to message history.
    st.chat_message("user").write(input)
    msgs.add_user_message(input) 
    # Invoke chain to get reponse.
    response = chain.invoke({'input': input})                 
    # Display AI assistant response and save to message history.
    st.chat_message("assistant").write(str(response))
    msgs.add_ai_message(response)