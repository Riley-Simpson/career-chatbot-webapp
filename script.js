document.addEventListener('DOMContentLoaded', () => {
    const acceptTermsCheckbox = document.getElementById('acceptTerms');
    const startChatButton = document.getElementById('startChat');
    const chatContainer = document.getElementById('chatContainer');
    const disclosure = document.getElementById('disclosure');
    const userInput = document.getElementById('userInput');
    const sendMessageButton = document.getElementById('sendMessage');
    const chatLog = document.getElementById('chatLog');

    acceptTermsCheckbox.addEventListener('change', () => {
        startChatButton.disabled = !acceptTermsCheckbox.checked;
    });

    startChatButton.addEventListener('click', () => {
        disclosure.classList.add('hidden');
        chatContainer.classList.remove('hidden');
        userInput.disabled = false;
        sendMessageButton.disabled = false;
    });

    sendMessageButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage) {
            addMessageToChatLog('User', userMessage);
            userInput.value = '';

            fetch("/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ query: userMessage })
            })
                .then(response => response.json())
                .then(data => {
                    addMessageToChatLog('Career Bot', data.response.generated_text);
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessageToChatLog('Career Bot', 'Sorry, there was an error processing your request.');
                });
        }
    }

    function addMessageToChatLog(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    }
});
