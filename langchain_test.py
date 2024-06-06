from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
import os

GOOGLE_API_KEY = 'AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ'
os.environ["GOOGLE_API_KEY"] = "AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ"

cats_loader = TextLoader("docs/cats.txt")
dogs_loader = TextLoader("docs/dogs.txt")

documents = cats_loader.load()
documents += dogs_loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', task_type='SEMANTIC_SIMILARITY')

db = FAISS.from_documents(texts, embeddings)
print(db.similarity_search_with_score('cat'))

retriever = db.as_retriever(search_type='mmr')

print(retriever.invoke('What are cats?'))




