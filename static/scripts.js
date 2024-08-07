document.addEventListener("DOMContentLoaded", () => {
    const consentGiven = localStorage.getItem('consentGiven');
    const sessionEnded = localStorage.getItem('sessionEnded');
    const backdoor = localStorage.getItem('backdoor');

    if (backdoor) {
        showChat();
    } else if (sessionEnded) {
        showSessionEndedMessage();
    } else if (!consentGiven) {
        showModal();
    } else {
        showChat();
    }
});

function showModal() {
    document.getElementById('consent-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('consent-modal').style.display = 'none';
}

function showChat() {
    document.getElementById('chat-box').style.display = 'block';
    document.getElementById('query-input').style.display = 'block';
    document.querySelector('button[onclick="sendQuery()"]').style.display = 'block';
    document.getElementById('resume-upload').style.display = 'flex'; // Show the resume upload section

    if (!localStorage.getItem('backdoor')) {
        const endTime = localStorage.getItem('endTime');
        if (endTime) {
            startChatTimer(new Date(endTime));
        } else {
            const newEndTime = new Date(Date.now() + 10 * 60 * 1000);
            localStorage.setItem('endTime', newEndTime);
            startChatTimer(newEndTime);
        }
    }
}

function checkGoogleFormSubmission() {
    localStorage.setItem('consentGiven', 'true');
    closeModal();
    showChat();
}

function sendQuery() {
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value;
    if (!query) return;

    addMessage(query, 'user');
    queryInput.value = '';

    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: query }),
    })
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none';

            if (data.response) {
                addMessage(data.response, 'bot', true);
            } else {
                addMessage('Response Error: Sorry, something went wrong. Please try again.', 'bot');
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        });
}

function uploadResume() {
    const resumeInput = document.getElementById('resume-input');
    const file = resumeInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('resume', file);

    fetch('/upload_resume', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addMessage('Resume uploaded successfully.', 'bot');
            } else {
                addMessage('Resume upload failed. Please try again.', 'bot');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Resume upload failed. Please try again.', 'bot');
        });
}

function addMessage(text, sender, isMarkdown = false) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    if (isMarkdown) {
        messageDiv.innerHTML = marked.parse(text);
    } else {
        messageDiv.textContent = text;
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function startChatTimer(endTime) {
    const timerDisplay = document.createElement('div');
    timerDisplay.id = 'timer';
    timerDisplay.style.position = 'absolute';
    timerDisplay.style.bottom = '10px';
    timerDisplay.style.right = '10px';
    timerDisplay.style.backgroundColor = '#f9f9f9';
    timerDisplay.style.padding = '10px';
    timerDisplay.style.borderRadius = '5px';
    timerDisplay.style.border = '1px solid #ddd';
    document.body.appendChild(timerDisplay);

    const interval = setInterval(() => {
        const timeLeft = new Date(endTime) - Date.now();
        if (timeLeft <= 0) {
            clearInterval(interval);
            endChatSession();
            return;
        }
        const minutesLeft = Math.floor(timeLeft / 1000 / 60);
        const secondsLeft = Math.floor((timeLeft / 1000) % 60);
        timerDisplay.textContent = `Time left: ${minutesLeft}:${secondsLeft < 10 ? '0' : ''}${secondsLeft}`;
    }, 1000);
}

function endChatSession() {
    addMessage('You have used your allocated 5 minutes, thank you for your time :)', 'bot');

    localStorage.setItem('sessionEnded', 'true');
    localStorage.removeItem('endTime');

    setTimeout(() => {
        document.getElementById('chat-box').style.display = 'none';
        document.getElementById('query-input').style.display = 'none';
        document.querySelector('button[onclick="sendQuery()"]').style.display = 'none';
        document.getElementById('feedback-form').style.display = 'block';

        const timerDisplay = document.getElementById('timer');
        if (timerDisplay) {
            timerDisplay.remove();
        }
    }, 5000);
}

function showSessionEndedMessage() {
    const container = document.querySelector('.container');
    container.innerHTML = `
        <p>You have used your allocated 10 minutes, thank you for your time :)</p>
        <div class="feedback-form">
            <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdC3bxESKoKFVEL7cr8CwLykODbvn1QLCwZVJZ080u5hCdsvA/viewform?embedded=true"
                    width="100%" height="400px" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
        </div>`;
}

function enableBackdoor() {
    localStorage.setItem('backdoor', 'true');
    localStorage.removeItem('endTime');
}

function disableBackdoor() {
    localStorage.removeItem('backdoor');
    localStorage.removeItem('sessionEnded');
    window.location.reload();
}
