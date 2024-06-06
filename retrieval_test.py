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

cats_loader = TextLoader("docs/cats.txt")
dogs_loader = TextLoader("docs/dogs.txt")
quant_loader = TextLoader("docs/quant.txt")

documents = cats_loader.load()
documents += dogs_loader.load()
documents += quant_loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')

db = FAISS.from_documents(texts, embeddings)

retriever = db.as_retriever(search_type='mmr')
message = """
Answer this question using the provided context only.

{question}

Context:
{context}
"""

prompt = ChatPromptTemplate.from_messages([("human", message)])

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

response = rag_chain.invoke("How do quantum computers compare to classical computers?")
print(response.content)