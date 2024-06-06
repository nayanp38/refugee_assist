from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


os.environ["GOOGLE_API_KEY"] = "AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ"

loaders = [
    TextLoader("docs/quant.txt"),
    TextLoader("docs/dogs.txt"),
    TextLoader("docs/cats.txt"),
    TextLoader("docs/ml.txt")
]
docs = []
for loader in loaders:
    docs.extend(loader.load())

# This text splitter is used to create the child documents
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
# The vectorstore to use to index the child chunks
embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')
vectorstore = FAISS.from_documents(docs, embeddings)
# The storage layer for the parent documents
store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    search_type="similarity",
    search_kwargs={"score_threshold": 0.75}
)

# retriever = vectorstore.as_retriever(search_type='similarity', search_kwargs={'score_threshold': 0.5})

retriever.add_documents(docs, ids=None)

sub_docs = vectorstore.similarity_search_with_score("quantum")
docs = retriever.invoke('quantum')
print(sub_docs)
print(len(sub_docs))
print(docs)
