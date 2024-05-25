document.getElementById('chatbot').style.display = 'none';

function run() {
    var input = document.getElementById('user-input').value;
    const origin = document.getElementById('origin').value;
    const destination = document.getElementById('destination').value;
    const duration = document.getElementById('duration').value;
    const age = document.getElementById('age').value;
    const education = document.getElementById('education').value;
    const employment = document.getElementById('employment').value;
    const url = `/get_response?input=${encodeURIComponent(input)}&origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&duration=${encodeURIComponent(duration)}&age=${encodeURIComponent(age)}&education=${encodeURIComponent(education)}&employment=${encodeURIComponent(employment)}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += "<p><span style='font-weight: bold; color: orangered'>You: </span>" + data.human + "</p>";
            chatBox.innerHTML += "<p><span style='font-weight: bold; color: royalblue'>RefugeeAssist: </span>" + data.ai + "</p>";
            document.getElementById("user-input").value = "";
        })
}

function submitForm() {
    document.getElementById('form').style.display = 'none';
    document.getElementById('chatbot').style.display = 'block';
    /*
    const origin = document.getElementById('origin').value;
    const destination = document.getElementById('destination').value;
    const duration = document.getElementById('duration').value;
    const age = document.getElementById('age').value;
    const education = document.getElementById('education').value;
    const employment = document.getElementById('employment').value;
    const url = `/submit_form?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&duration=${encodeURIComponent(duration)}&age=${encodeURIComponent(age)}&education=${encodeURIComponent(education)}&employment=${encodeURIComponent(employment)}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {

        })

     */
}

window.submitForm = submitForm;
window.run = run;