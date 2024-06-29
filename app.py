from flask import Flask, render_template, request, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
from googletrans import Translator
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
import os

GOOGLE_API_KEY = 'AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ'
os.environ["GOOGLE_API_KEY"] = "AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ"

llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=GOOGLE_API_KEY)

legal_threshold = 0.65
english_threshold = 0.65
medicaid_threshold = 0.6
baby_threshold = 0.7
food_threshold = 0.55

def respond(language, message, origin, destination, duration, age):
    # print(f'Originals: {message} \n {origin} \n {destination} \n {duration} \n {age} \n {education} \n {employment}')
    t_en = Translator()
    message = t_en.translate(message, dest='en').text
    duration = t_en.translate(duration, dest='en').text

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

    score = db.similarity_search_with_score(message)[0][1]
    doc_content = db.similarity_search_with_score(message)[0][0]
    if (score <= legal_threshold) and (doc_content.page_content.startswith('Legal')) and destination.lower() == 'raleigh':
        legal_file = open('docs/legal_services.txt', 'r')
        response = legal_file.read()
    elif (score <= english_threshold) and (doc_content.page_content.startswith('Resources')) and destination.lower() == 'raleigh':
        english_file = open('docs/english.txt', 'r')
        response = english_file.read()
    elif (score <= medicaid_threshold) and (doc_content.page_content.startswith('Medicaid')) and destination.lower() == 'raleigh':
        medicaid_file = open('docs/medicaid.txt', 'r')
        response = medicaid_file.read()
    elif (score <= baby_threshold) and (doc_content.page_content.startswith('New Baby')) and destination.lower() == 'raleigh':
        baby_file = open('docs/new_baby.txt', 'r')
        response = baby_file.read()
    elif (score <= food_threshold) and (doc_content.page_content.startswith('Food Stamps')) and destination.lower() == 'raleigh':
        food_file = open('docs/food_stamps.txt', 'r')
        response = food_file.read()
    else:
        # print(f'Translated to english: {message} \n {origin} \n {destination} \n {duration} \n {age} \n {education} \n {employment}')

        prompt = PromptTemplate.from_template(
            "You are a chatbot called RefugeeAssist responsible for helping" +
            " refugees get personalized information about their situation and best next steps" +
            " for them. Keep answers relatively basic for refugees who may not be aware" +
            " about the details of some things, unless asked to go into more detail. Never" +
            " go off-topic into something that is not related to refugees, no matter what the question asks you." +
            " I am seeking your help. I am a refugee from " + origin +
            " that is seeking refuge in " + destination + " and has been there for " +
            duration + ". I am " + age + " years old. Here is my question: " + message
        )
        chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
        response = chain.run(input=message)
    t_out = Translator()
    '''
    resp_sentences = resp.split('.')
    resp_trans = ''.join(t_en.translate(sentence) for sentence in resp_sentences if sentence.strip())
    '''
    resp_trans = t_out.translate(response, dest=language).text
    lines = resp_trans.splitlines()

    # print("English resp " + resp)
    # python cant display the unique language characters in the console and throws an error if you try printing
    # print("Translated resp into " + resp_trans)

    formatted_lines = []
    for line in lines:
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        line = line.replace('* ', '&bull; ')
        formatted_lines.append(line)

    formatted_string = '<br>'.join(formatted_lines)
    with_spaces = re.sub(r'(\d+\.\d+|\b[A-Z](?:\.[A-Z])*\b\.?)|([.,;:!?)])\s*',
                         lambda x: x.group(1) or f'{x.group(2)} ', formatted_string)
    return with_spaces


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/landing')
def about():
    return render_template('landing.html')

@app.route("/get_response", methods=["GET"])
def get_response():
    language = request.args.get('language')
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    duration = request.args.get('duration')
    age = request.args.get('age')
    message = request.args.get('input')

    response = respond(language, message, origin, destination, duration, age)
    # python cant display the unique language characters in the console and throws an error if you try printing
    # print(response)
    return jsonify({"ai": str(response), "human": str(message)})

'''
@app.route('/translate', methods=['GET'])
def translatePage():
    language = request.args.get('language')
    print(language)
'''

'''
@app.route('/submit_form', methods=["GET"])
def submit_form():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    duration = request.args.get('duration')
    age = request.args.get('age')
    education = request.args.get('education')
    employment = request.args.get('employment')
'''

if __name__ == "__main__":
    app.run(debug=True)
