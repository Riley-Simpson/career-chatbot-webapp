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
}

function checkGoogleFormSubmission() {
    // This is a manual check, as we can't programmatically verify Google Form submission
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

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: query }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                addMessage(data.response, 'bot');
            } else {
                addMessage('Sorry, something went wrong. Please try again.', 'bot');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        });
}

function addMessage(text, sender) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.textContent = text;

    // Add feedback buttons for bot messages
    if (sender === 'bot') {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.classList.add('feedback');

        const likeButton = document.createElement('button');
        likeButton.innerHTML = '👍';
        likeButton.onclick = () => sendFeedback(text, 'like');

        const dislikeButton = document.createElement('button');
        dislikeButton.innerHTML = '👎';
        dislikeButton.onclick = () => sendFeedback(text, 'dislike');

        feedbackDiv.appendChild(likeButton);
        feedbackDiv.appendChild(dislikeButton);
        messageDiv.appendChild(feedbackDiv);
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function sendFeedback(message, feedback) {
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, feedback }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Thank you for your feedback!');
            } else {
                alert('Sorry, something went wrong. Please
