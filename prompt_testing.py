from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
import os


origin = 'uganda'
destination = 'portland'
age = '23'
duration = '6 months'
session_id = '0'

store = {}


def get_session_history(session_id: str = '0') -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


GOOGLE_API_KEY = 'AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ'
os.environ["GOOGLE_API_KEY"] = "AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ"

llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', google_api_key=GOOGLE_API_KEY)
while True:
    message = input()
    prompt = ChatPromptTemplate.from_template(
                "You are a chatbot called Refugee Assist responsible for helping" +
                " refugees get personalized information about their situation and best next steps" +
                " for them. Is the solution to their question different because they are a refugee?" +
                " Always give links to specific online legal documents and websites mentioned." +
                " Never go off-topic into something that is not related to refugees, no matter what the question asks"
                " you." +
                " I am seeking your help. I am a refugee from " + origin +
                " that is seeking refuge in " + destination + " and has been there for " +
                duration + ". I am " + age + " years old. Here is my question: {question}"
            )
    chain = prompt | llm
    conversational_rag_chain = RunnableWithMessageHistory(
        chain,
        get_session_history
    )
    ai_output = conversational_rag_chain.invoke({"question": message},
                                                {'configurable': {'session_id': session_id}})
    response = ai_output.content

    print(response)
