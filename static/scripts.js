document.addEventListener("DOMContentLoaded", () => {
    const consentGiven = localStorage.getItem('consentGiven');
    const sessionEnded = localStorage.getItem('sessionEnded');

    if (sessionEnded) {
        showFeedbackForm();
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

    // Start 5-minute timer
    startChatTimer(5);
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

    document.getElementById('loading-spinner').style.display = 'block';

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: query }),
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('loading-spinner').style.display = 'none';

            if (data.response) {
                addMessage(data.response, 'bot');
            } else {
                addMessage('Response Error: Sorry, something went wrong. Please try again.', 'bot');
            }
        })
        .catch(error => {
            document.getElementById('loading-spinner').style.display = 'none';

            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        });
}

function addMessage(text, sender) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.textContent = text;

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function startChatTimer(minutes) {
    const endTime = Date.now() + minutes * 60 * 1000;
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
        const timeLeft = endTime - Date.now();
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
    document.getElementById('chat-box').style.display = 'none';
    document.getElementById('query-input').style.display = 'none';
    document.querySelector('button[onclick="sendQuery()"]').style.display = 'none';
    document.getElementById('feedback-form').style.display = 'block';

    const timerDisplay = document.getElementById('timer');
    if (timerDisplay) {
        timerDisplay.remove();
    }

    // Set session ended flag
    localStorage.setItem('sessionEnded', 'true');
}

function showFeedbackForm() {
    document.getElementById('feedback-form').style.display = 'block';
}
