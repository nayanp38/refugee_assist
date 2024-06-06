from flask import Flask, render_template, request, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
from googletrans import Translator

GOOGLE_API_KEY = 'AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ'

llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=GOOGLE_API_KEY)


def respond(language, message, origin, destination, duration, age, education, employment):
    # print(f'Originals: {message} \n {origin} \n {destination} \n {duration} \n {age} \n {education} \n {employment}')
    # Rewriting t_en to refresh the autodetect language in case each resp is a diff language.
    t_en = Translator()
    message = t_en.translate(message, dest='en').text
    duration = t_en.translate(duration, dest='en').text
    education = t_en.translate(education, dest='en').text
    employment = t_en.translate(employment, dest='en').text

    # print(f'Translated to english: {message} \n {origin} \n {destination} \n {duration} \n {age} \n {education} \n {employment}')

    prompt = PromptTemplate.from_template(
        "You are a chatbot called RefugeeAssist responsible for helping" +
        " refugees get personalized information about their situation and best next steps" +
        " for them. Keep answers relatively basic for refugees who may not be aware" +
        " about the details of some things, unless asked to go into more detail. Never" +
        " go off-topic into something that is not related to refugees, no matter what the question asks you." +
        " I am seeking your help. I am a refugee from " + origin +
        " that is seeking refuge in " + destination + " and has been there for " +
        duration + ". I am " + age + " years old. Here is my educational background: " +
        education + ". Here is my employment history/relevant skills: " + employment +
        ". Here is my question: " + message
    )
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    resp = chain.run(input=message)
    t_out = Translator()
    '''
    resp_sentences = resp.split('.')
    resp_trans = ''.join(t_en.translate(sentence) for sentence in resp_sentences if sentence.strip())
    '''
    resp_trans = t_out.translate(resp, dest=language).text
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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/get_response", methods=["GET"])
def get_response():
    language = request.args.get('language')
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    duration = request.args.get('duration')
    age = request.args.get('age')
    education = request.args.get('education')
    employment = request.args.get('employment')
    message = request.args.get('input')


    response = respond(language, message, origin, destination, duration, age, education, employment)
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
