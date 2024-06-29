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
ZEP_API_KEY = ('z_1dWlkIjoiYmNmY2FiYjktNDZmMC00OGZjLWJlY2QtNTBiYzc3NWUzZmRiIn0.lTn-qyJMO1YsUY4UqSVVRhnYuKl7Nl1uJiVMi9t'
               '-i_BhmwkWQ2sea-r3Snqg_RuwL_JZhrfCwR1vZ22s1ipglA')

llm = ChatGoogleGenerativeAI(model='gemini-pro')

legal_loader = TextLoader('docs/legal_services.txt')
english_loader = TextLoader('docs/english.txt')
medicaid_loader = TextLoader('docs/medicaid.txt')
baby_loader = TextLoader('docs/new_baby.txt')
food_loader = TextLoader('docs/food_stamps.txt')

documents = legal_loader.load()
documents += english_loader.load()
documents += medicaid_loader.load()
documents += baby_loader.load()
documents += food_loader.load()

text_splitter = CharacterTextSplitter(chunk_size=4000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')

db = FAISS.from_documents(texts, embeddings)

legal_threshold = 0.65
english_threshold = 0.65
medicaid_threshold = 0.6
baby_threshold = 0.7
food_threshold = 0.55

# retriever = db.as_retriever(search_type="similarity", search_kwargs={"score_threshold": threshold})
retriever = db.as_retriever(search_type="similarity")

message_strict = """
Answer this question using the below context.

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

message_repeat = """
Repeat the following context verbatim, however ignore the context it if the question does not pertain to the context:
Question:
{question}

Context:
{context}
"""

message_none = """
{question}
"""

question = """

Hello, I just arrived in Raleigh, North Carolina, and I need help understanding what steps I should take next for my resettlement. WHat should i do with a new child?
"""

print(db.similarity_search_with_score(question))
score = db.similarity_search_with_score(question)[0][1]
print(score)
print(len(db.similarity_search_with_score(question)))

prompt = ChatPromptTemplate.from_messages([("human", (message_repeat if (score <= legal_threshold) else message_none))])

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

doc_content = db.similarity_search_with_score(question)[0][0]
if (score <= legal_threshold) and (doc_content.page_content.startswith('Legal')):
    print("LEGAL QUESTION")
    legal_file = open('docs/legal_services.txt', 'r')
    response = legal_file.read()
elif (score <= english_threshold) and (doc_content.page_content.startswith('Resources')):
    print("ENGLISH QUESTION")
    english_file = open('docs/english.txt', 'r')
    response = english_file.read()
elif (score <= medicaid_threshold) and (doc_content.page_content.startswith('Medicaid')):
    print("MEDICAID QUESTION")
    medicaid_file = open('docs/medicaid.txt', 'r')
    response = medicaid_file.read()
elif (score <= baby_threshold) and (doc_content.page_content.startswith('New Baby')):
    print("BABY QUESTION")
    baby_file = open('docs/new_baby.txt', 'r')
    response = baby_file.read()
elif (score <= food_threshold) and (doc_content.page_content.startswith('Food Stamps')):
    print("FOOD STAMP QUESTION")
    food_file = open('docs/food_stamps.txt', 'r')
    response = food_file.read()
else:
    response = rag_chain.invoke(question).content

print(response)
