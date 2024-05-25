from flask import Flask, render_template, request, jsonify
import langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

GOOGLE_API_KEY = 'AIzaSyDJRBE7Xp6zWJYHvJf4zjx0FuH_mnu9_NQ'

llm = ChatGoogleGenerativeAI(model='gemini-pro', google_api_key=GOOGLE_API_KEY)


def respond(message, origin, destination, duration, age, education, employment):
    prompt = PromptTemplate.from_template(
        "You are a chatbot called RefugeeAssist responsible for helping" +
        " refugees get personalized information about their situation and best next steps" +
        "for them. Keep answers relatively basic for refugees who may not be aware" +
        "about the details of some things, unless asked to go into more detail. Never" +
        " go off-topic into something that is not related to refugees, no matter what the question asks you." +
        "I am seeking your help. I am a refugee from " + origin +
        "that is seeking refuge in " + destination + " and has been there for " +
        duration + ". I am " + age + " years old. Here is my educational background: " +
        education + ". Here is my employment history/relevant skills: " + employment +
        ". Here is my question: " + message
    )
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    resp = chain.run(input=message)
    return resp


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_response", methods=["GET"])
def get_response():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    duration = request.args.get('duration')
    age = request.args.get('age')
    education = request.args.get('education')
    employment = request.args.get('employment')
    message = request.args.get('input')
    response = respond(message, origin, destination, duration, age, education, employment)
    return jsonify({"ai": str(response), "human": str(message)})

@app.route('/submit_form', methods=["GET"])
def submit_form():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    duration = request.args.get('duration')
    age = request.args.get('age')
    education = request.args.get('education')
    employment = request.args.get('employment')

if __name__ == "__main__":
    app.run(debug=True)
