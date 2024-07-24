import os
from typing import List, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import (
    RunnableParallel,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

from zep_cloud.client import AsyncZep
from langchain_community.chat_message_histories.zep import ZepChatMessageHistory


ZEP_API_KEY = ('z_1dWlkIjoiYmNmY2FiYjktNDZmMC00OGZjLWJlY2QtNTBiYzc3NWUzZmRiIn0.lTn-qyJMO1YsUY4UqSVVRhnYuKl7Nl1uJiVMi9t'
               '-i_BhmwkWQ2sea-r3Snqg_RuwL_JZhrfCwR1vZ22s1ipglA')
os.environ["GOOGLE_API_KEY"] = "AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ"

zep = AsyncZep(
    api_key=ZEP_API_KEY,
)

template = """Answer the question below as if you were a 19th centry poet:
    """
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{question}"),
    ]
)

inputs = RunnableParallel(
    {
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["chat_history"],
    },
)
chain = RunnableWithMessageHistory(
    inputs | answer_prompt | ChatGoogleGenerativeAI(model='gemini-pro') | StrOutputParser(),
    lambda session_id: ZepChatMessageHistory(
        session_id=session_id,  # This uniquely identifies the conversation
    ),
    input_messages_key="question",
    history_messages_key="chat_history",
)

chain.invoke(
    {"question": "-"},
    config={"configurable": {"session_id": "-"}},
)