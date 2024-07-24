import translate from "translate";

document.getElementById('chatbot').style.display = 'none';
document.getElementById('typing').style.display = 'none';

document.addEventListener("DOMContentLoaded", function() {
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll(".nav-link");

    if (currentPath === '/') {
        navLinks.forEach(function(link) {
            if (link.textContent === 'Home') {
                link.classList.add('active');
            }
        });
    } else if (currentPath === '/about') {
        navLinks.forEach(function(link) {
            if (link.textContent === 'About') {
                link.classList.add('active');
            }
        });
    }

});

const elements = document.querySelectorAll(".question_prompt, .trans");
let originalText = [];
for (const element of elements) {
    originalText.push(element.textContent);
}
const placeholder = document.getElementById('origin').placeholder;

async function run() {
    var session_id = document.getElementById('session_id').textContent;
    var list = document.getElementById("dropdwn");
    var language = list.options[list.selectedIndex].value;
    var input = document.getElementById('user-input').value;
    if (input.trim() === "") {
        return; // break if the input is empty
    }
    var origin = document.getElementById('origin').value;
    var destination = document.getElementById('destination').value;
    var duration = document.getElementById('duration').value;
    var age = document.getElementById('age').value;

    origin = origin.trim() === "" ? "none" : origin;
    destination = destination.trim() === "" ? "none" : destination;
    duration = duration.trim() === "" ? "none" : duration;
    age = age.trim() === "" ? "none" : age;

    translate.engine = 'google';

    document.getElementById("user-input").value = "";
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += "<p><span style='font-weight: bold; color: orangered'>"+ await translate("You") + ": </span>" + input + "</p>";
    chatBox.innerHTML += "<span id='assist' class='pending' style='font-weight: bold; color: royalblue'>RefugeeAssist: </span>";
    var typing = document.getElementById('typing').cloneNode(true);
    typing.style.display = 'block'
    const scaleFactor = 0.075;
    typing.style.width = (typing.width * scaleFactor) + 'px';
    typing.style.height = (typing.height * scaleFactor) + 'px';
    typing.style.marginTop = '-8px';
    typing.classList.add('pending');

    const parent = document.createElement('div');
    const elements = document.querySelectorAll('.pending');
    elements.forEach(element => {
        parent.appendChild(element);
    });
    parent.appendChild(typing);
    parent.style.display = 'flex';
    parent.style.flexDirection = 'row';
    parent.style.alignContent = 'flex-start';
    chatBox.appendChild(parent);

    /*
    console.log(
        origin + " " + destination + " " + duration + " " + age + " " + education + " " + employment
    );
    */

    const params = new URLSearchParams({
        session_id: session_id,
        language: language,
        input: input,
        origin: origin,
        destination: destination,
        duration: duration,
        age: age
    });

    const url = `/get_response?${params.toString()}`;

    //const url = `/get_response?language=${encodeURIComponent(language)}&input=${encodeURIComponent(input_trans)}&origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&duration=${encodeURIComponent(duration)}&age=${encodeURIComponent(age)}&education=${encodeURIComponent(education)}&employment=${encodeURIComponent(employment)}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            translate.from = 'en';
            translate.to = language;
            parent.removeChild(typing);
            parent.removeChild(document.getElementById('assist'));
            chatBox.innerHTML += "<span style='font-weight: bold; color: royalblue'>RefugeeAssist: </span>";
            chatBox.innerHTML += "<p>" + data.ai + "</p>";
        })
}

function submitForm() {
    document.getElementById('form').style.display = 'none';
    document.getElementById('chatbot').style.display = 'block';
    fetch('/submit_form').then(r => {})
}


async function translatePage() {
    var list = document.getElementById("dropdwn");
    var language = list.options[list.selectedIndex].value;

    translate.engine = 'google';
    translate.to = language;
    var elements = document.querySelectorAll(".question_prompt, .trans");
    elements.forEach(async (element, i) => {
        element.textContent = await translate(originalText[i]);
    });

    var questions = document.querySelectorAll(".input_box");
    for (const question of questions) {
        question.placeholder = await translate(placeholder);
    }

}


window.translatePage = translatePage;
window.submitForm = submitForm;
window.run = run;