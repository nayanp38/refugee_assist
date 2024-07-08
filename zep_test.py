from uuid import uuid4
import os

from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.memory.zep_memory import ZepMemory
from langchain_community.retrievers import ZepRetriever
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

session_id = str(uuid4())  # This is a unique identifier for the session

GOOGLE_API_KEY = 'AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ'
os.environ["GOOGLE_API_KEY"] = "AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ"
ZEP_API_KEY = ('z_1dWlkIjoiYmNmY2FiYjktNDZmMC00OGZjLWJlY2QtNTBiYzc3NWUzZmRiIn0.lTn-qyJMO1YsUY4UqSVVRhnYuKl7Nl1uJiVMi9t'
               '-i_BhmwkWQ2sea-r3Snqg_RuwL_JZhrfCwR1vZ22s1ipglA')


search = WikipediaAPIWrapper()
tools = [
    Tool(
        name="Search",
        func=search.run,
        description=(
            "useful for when you need to search online for answers. You should ask"
            " targeted questions"
        ),
    ),
]

# Set up Zep Chat History
memory = ZepMemory(
    session_id=session_id,
    api_key=ZEP_API_KEY,
    return_messages=True,
    memory_key="chat_history",
)

# Initialize the agent
llm = ChatGoogleGenerativeAI(model='gemini-pro')
agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
)

# Preload some messages into the memory. The default message window is 12 messages. We want to push beyond this to demonstrate auto-summarization.
test_history = [
    {"role": "human", "content": "Who was Octavia Butler?"},
    {
        "role": "ai",
        "content": (
            "Octavia Estelle Butler (June 22, 1947 – February 24, 2006) was an American"
            " science fiction author."
        ),
    },
    {"role": "human", "content": "Which books of hers were made into movies?"},
    {
        "role": "ai",
        "content": (
            "The most well-known adaptation of Octavia Butler's work is the FX series"
            " Kindred, based on her novel of the same name."
        ),
    },
    {"role": "human", "content": "Who were her contemporaries?"},
    {
        "role": "ai",
        "content": (
            "Octavia Butler's contemporaries included Ursula K. Le Guin, Samuel R."
            " Delany, and Joanna Russ."
        ),
    },
    {"role": "human", "content": "What awards did she win?"},
    {
        "role": "ai",
        "content": (
            "Octavia Butler won the Hugo Award, the Nebula Award, and the MacArthur"
            " Fellowship."
        ),
    },
    {
        "role": "human",
        "content": "Which other women sci-fi writers might I want to read?",
    },
    {
        "role": "ai",
        "content": "You might want to read Ursula K. Le Guin or Joanna Russ.",
    },
    {
        "role": "human",
        "content": (
            "Write a short synopsis of Butler's book, Parable of the Sower. What is it"
            " about?"
        ),
    },
    {
        "role": "ai",
        "content": (
            "Parable of the Sower is a science fiction novel by Octavia Butler,"
            " published in 1993. It follows the story of Lauren Olamina, a young woman"
            " living in a dystopian future where society has collapsed due to"
            " environmental disasters, poverty, and violence."
        ),
        "metadata": {"foo": "bar"},
    },
]

for msg in test_history:
    memory.chat_memory.add_message(
        (
            HumanMessage(content=msg["content"])
            if msg["role"] == "human"
            else AIMessage(content=msg["content"])
        ),
        metadata=msg.get("metadata", {}),
    )


agent_chain.invoke(
    input="What is the book's relevance to the challenges facing contemporary society?",
)