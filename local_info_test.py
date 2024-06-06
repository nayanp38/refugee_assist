from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
import os
from langchain_google_genai import ChatGoogleGenerativeAI

GOOGLE_API_KEY = 'AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ'
os.environ["GOOGLE_API_KEY"] = "AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ"

llm = ChatGoogleGenerativeAI(model='gemini-pro')

cats_loader = TextLoader("docs/grocery.txt")

documents = cats_loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')

db = FAISS.from_documents(texts, embeddings)

threshold = 0.5

retriever = db.as_retriever(search_type="similarity", search_kwargs={"score_threshold": threshold})
message_strict = """
Answer this question using the provided context only.

{question}

Context:
{context}
"""

message_full = """
You are a chatbot called RefugeeAssist responsible for helping
 refugees get personalized information about their situation and best next steps
for them. Keep answers relatively basic for refugees who may not be aware
about the details of some things, unless asked to go into more detail. Never
go off-topic into something that is not related to refugees, no matter what the question asks you.
I am seeking your help. I am a refugee from 
that is seeking refuge in and has been there for.
I am years old. Here is my educational background: . 
Here is my employment history/relevant skills: .
Here is my question: {question}
"""

message_loose = """

"""

message_none = """
{question}
"""

question = "Hello, I am new to the country and this place and have not been here for too long. Where can i find food in raleigh"
print(db.similarity_search_with_score(question))
score = db.similarity_search_with_score(question)[0][1]
print(score)

prompt = ChatPromptTemplate.from_messages([("human", (message_strict if (score <= threshold) else message_none))])

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

response = rag_chain.invoke(question)

print(response.content)
