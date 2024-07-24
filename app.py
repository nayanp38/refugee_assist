from flask import Flask, render_template, request, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI
import re
from googletrans import Translator
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
import os
import uuid
from datetime import datetime

# absolute root dir for website hosting:
# '/home/npatel38/mysite/'
root_dir = ''

GOOGLE_API_KEY = 'AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ'
os.environ["GOOGLE_API_KEY"] = "AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ"

llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', google_api_key=GOOGLE_API_KEY)

legal_threshold = 0.65
english_threshold = 0.65
medicaid_threshold = 0.6
baby_threshold = 0.7
food_threshold = 0.55

store = {}


def get_session_history(session_id: str = '0') -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def respond(session_id, language, message, origin, destination, duration, age):
    # print(f'Originals: {message} \n {origin} \n {destination} \n {duration} \n {age} \n {education} \n {employment}')
    t_en = Translator()
    message = t_en.translate(message, dest='en').text
    duration = t_en.translate(duration, dest='en').text

    legal_loader = TextLoader(root_dir + 'docs/legal_services.txt')
    english_loader = TextLoader(root_dir + 'docs/english.txt')
    medicaid_loader = TextLoader(root_dir + 'docs/medicaid.txt')
    baby_loader = TextLoader(root_dir + 'docs/new_baby.txt')
    food_loader = TextLoader(root_dir + 'docs/food_stamps.txt')

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
    if (score <= legal_threshold) and (
            doc_content.page_content.startswith('Legal')) and destination.lower() == 'raleigh':
        legal_file = open(root_dir + 'docs/legal_services.txt', 'r')
        response = legal_file.read()
    elif (score <= english_threshold) and (
            doc_content.page_content.startswith('Resources')) and destination.lower() == 'raleigh':
        english_file = open(root_dir + 'docs/english.txt', 'r')
        response = english_file.read()
    elif (score <= medicaid_threshold) and (
            doc_content.page_content.startswith('Medicaid')) and destination.lower() == 'raleigh':
        medicaid_file = open(root_dir + 'docs/medicaid.txt', 'r')
        response = medicaid_file.read()
    elif (score <= baby_threshold) and (
            doc_content.page_content.startswith('New Baby')) and destination.lower() == 'raleigh':
        baby_file = open(root_dir + 'docs/new_baby.txt', 'r')
        response = baby_file.read()
    elif (score <= food_threshold) and (
            doc_content.page_content.startswith('Food Stamps')) and destination.lower() == 'raleigh':
        food_file = open(root_dir + 'docs/food_stamps.txt', 'r')
        response = food_file.read()
    else:
        # print(f'Translated to english: {message} \n {origin} \n {destination} \n {duration} \n {age} \n {education} \n {employment}')

        prompt = ChatPromptTemplate.from_template(
            "You are a chatbot called RefugeeAssist responsible for helping" +
            " refugees get personalized information about their situation and best next steps" +
            " for them. Keep answers relatively basic for refugees who may not be aware" +
            " about the details of some things, unless asked to go into more detail. Never" +
            " go off-topic into something that is not related to refugees, no matter what the question asks you." +
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


def count_up(name, value, increment):
    with open(f'{root_dir}static/counter-{name}.txt', 'w') as file:
        file.write(str(value + increment))


app = Flask(__name__)


@app.route("/")
def index():
    with open(root_dir + 'static/counter-users.txt', 'r') as file:
        users = int(file.read().strip())
    with open(root_dir + 'static/counter-answers.txt', 'r') as file:
        answers = int(file.read().strip())
    with open(root_dir + 'static/counter-words.txt', 'r') as file:
        words = int(file.read().strip())

    return render_template("index.html", users=users, answers=answers, words=words)


@app.route('/chatbot')
def chatbot():
    # reset the chat history for each person that arrives at the site
    session_id = str(uuid.uuid4())
    return render_template('chatbot.html', session_id=session_id)


@app.route("/get_response", methods=["GET"])
def get_response():
    session_id = request.args.get('session_id')
    language = request.args.get('language')
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    duration = request.args.get('duration')
    age = request.args.get('age')
    message = request.args.get('input')

    sid_present = False

    dt_string = datetime.now().strftime("%m/%d/%Y %H:%M")

    response = respond(session_id, language, message, origin, destination, duration, age)
    with open(root_dir + 'static/chat_history_log.txt', 'w') as file:
        for ses_id in store:
            file.write(ses_id + ':\n')
            for conv_message in store[ses_id].messages:
                file.write('[START] ' + conv_message.content + '\n')
    with open(root_dir + 'static/session_ids.txt', 'r') as file:
        content = file.read()
        if session_id in content:
            sid_present = True

    with open(root_dir + 'static/session_ids.txt', 'a') as file:
        if not sid_present:
            file.write(f'[{dt_string}] ' + session_id + ':\n')
            file.write(f'Language: {language}; Origin: {origin}; Dest: {destination}; Dur: {duration}; Age: {age}\n\n')

    with open(root_dir + 'static/counter-answers.txt', 'r') as file:
        answers = int(file.read().strip())
    with open(root_dir + 'static/counter-words.txt', 'r') as file:
        words = int(file.read().strip())

    count_up('answers', answers, 1)
    if language != 'en':
        count_up('words', words, len(message.split()) + len(response.split()))
    # python cant display the unique language characters in the console and throws an error if you try printing
    # print(response)
    return jsonify({"ai": str(response), "human": str(message)})


@app.route('/submit_form', methods=["GET"])
def submit_form():
    with open(root_dir + 'static/counter-users.txt', 'r') as file:
        users = int(file.read().strip())
    count_up('users', users, 1)
    return 'complete'


@app.route('/contact_us', methods=["GET"])
def contact_us():
    name = request.args.get('name')
    email = request.args.get('email')
    number = request.args.get('number')
    message = request.args.get('message')

    dt_string = datetime.now().strftime("%m/%d/%Y %H:%M")

    with open(root_dir + 'static/contact_log.txt', 'a') as file:
        file.write(f'[{dt_string}] Name: {name}; Email: {email}; Number: {number}; Message: \n{message}\n\n')
    return 'complete'

if __name__ == "__main__":
    app.run(debug=True)
