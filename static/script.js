// script.js

// TODO: Add loading indicator (like 3 dots or something animated would be cool)
import { ChatOpenAI } from "@langchain/openai"
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { HarmBlockThreshold, HarmCategory } from "@google/generative-ai";

console.log('ehllo');
document.getElementById('chatbot').style.display = 'none';

const model = new ChatOpenAI({
    model: "gemini-pro",
    maxOutputTokens: 2048,
    safetySettings: [
    {
        category: HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    },
    ],
});

document.getElementById('chatbot').style.display = 'none';

function submitForm() {
    document.getElementById('form').style.display = 'none';
    document.getElementById('chatbot').style.display = 'block';
}

window.submitForm = submitForm;

let first_message = true;

async function run() {
    if (document.getElementById('user-input').value) {
        /*
        const origin = document.getElementById('origin').value;
        const destination = document.getElementById('destination').value;
        const duration = document.getElementById('duration').value;
        const age = document.getElementById('age').value;
        const education = document.getElementById('education').value;
        const employment = document.getElementById('employment').value;
        */

        const origin = 'uganda';
        const destination = 'raleigh, north carolina';
        const duration = '1 week';
        const age = '24';
        const education = 'none';
        const employment = 'none';

        const responses =
            'origin: ' + origin +
            '\n destination: ' + destination +
            '\n duration: ' + duration +
            '\n age: ' + age +
            '\n education: ' + education +
            '\n employment: ' + employment;

        const input = document.getElementById('user-input').value;
        let prompt = '';
        if (first_message === true) {
            prompt =
                "You are a chatbot called RefugeeAssist responsible for helping" +
                " refugees get personalized information about their situation and best next steps" +
                "for them. Keep answers relatively basic for refugees who may not be aware" +
                "about the details of some things, unless asked to go into more detail. Never" +
                " go off-topic into something that is not related to refugees, no matter what the question asks you." +
                "I am seeking your help. I am a refugee from " + origin +
                "that is seeking refuge in " + destination + " and has been there for " +
                duration + ". I am " + age + " years old. Here is my educational background: " +
                education + ". Here is my employment history/relevant skills: " + employment +
                ". Here is my question: " + input;
        } else {
            prompt = input;
        }
        console.log('first message' + first_message);
        // const result = await model.invoke(prompt);
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML += "<p><span style='font-weight: bold; color: orangered'>You: </span>" + input + "</p>";
        chatBox.innerHTML += "<p><span style='font-weight: bold; color: royalblue'>RefugeeAssist: </span></p>";
        const stream = await model.stream(prompt);
        let response = '';
        for await (const chunk of stream) {
            console.log(chunk);

            response += await chunk.content;
            let output = response;
            // const output = response.text();
            console.log('Responses: \n' + responses);
            console.log('Prompt: \n' + prompt);
            console.log('Output: \n' + output);
            const lines = output.split(/\r?\n/);

            const formattedLines = lines.map(line => {
                line = line.replace(/\* /g, '&bull; ');
                line = line.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
                return line;
            });

            const formattedString = '<br>' + formattedLines.join('<br>');
            //chatBox.innerHTML += "<p><span style='font-weight: bold; color: royalblue'>RefugeeAssist: </span>" + formattedString + "</p>";
            chatBox.innerHTML += "<p>" + response + "</p>";
        }

        document.getElementById("user-input").value = "";
        // first_message = false;
        //Note: the chatbot forgets it's supposed to only talk abt refugees
    }
}

window.run = run;
