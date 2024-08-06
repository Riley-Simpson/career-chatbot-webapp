document.addEventListener("DOMContentLoaded", () => {
    const consentGiven = localStorage.getItem('consentGiven');
    if (!consentGiven) {
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
    startChatTimer();
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

function startChatTimer() {
    setTimeout(() => {
        endChatSession();
    }, 300000); // 300,000 milliseconds = 5 minutes
}

function endChatSession() {
    document.getElementById('chat-box').style.display = 'none';
    document.getElementById('query-input').style.display = 'none';
    document.querySelector('button[onclick="sendQuery()"]').style.display = 'none';
    document.getElementById('feedback-form').style.display = 'block';
}
