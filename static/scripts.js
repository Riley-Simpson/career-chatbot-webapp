document.addEventListener("DOMContentLoaded", () => {
    const consentGiven = localStorage.getItem('consentGiven');
    const sessionEnded = localStorage.getItem('sessionEnded');
    const backdoor = localStorage.getItem('backdoor');

    // Show the chat dialog if the session has been closed.
    if (backdoor) {
        showChat();
        // Show the modal dialog if the session has ended.
    } else if (sessionEnded) {
        showSessionEndedMessage();
        // Show modal if the user has not sent the modal.
    } else if (!consentGiven) {
        showModal();
    } else {
        showChat();
    }
});


/**
* Show modal to confirm consent. Called on click of consent button in consent. html. This is a function so we don't have to wait for user to confirm
*/
function showModal() {
    document.getElementById('consent-modal').style.display = 'block';
}

/**
* Close Consent Modal and make it disappear on click of consent button. This is a hack to avoid flicker
*/
function closeModal() {
    document.getElementById('consent-modal').style.display = 'none';
}

/**
* Shows and hides chat and start timer if it's not in localStorage. Used to send queries
*/
function showChat() {
    document.getElementById('chat-box').style.display = 'block';
    document.getElementById('query-input').style.display = 'block';
    document.querySelector('button[onclick="sendQuery()"]').style.display = 'block';
    document.getElementById('resume-upload').style.display = 'flex';

    // If the session is backdoor or backdoor is not set the timer will be started.
    if (!localStorage.getItem('backdoor')) {
        const endTime = localStorage.getItem('endTime');
        // Starts the chat timer if the end time is set to the current time.
        if (endTime) {
            startChatTimer(new Date(endTime));
        } else {
            const newEndTime = new Date(Date.now() + 10 * 60 * 1000);
            localStorage.setItem('endTime', newEndTime);
            startChatTimer(newEndTime);
        }
    }
}

/**
* Checks if user has consented and if so sets consent given in local storage to true closes the modal
*/
function checkGoogleFormSubmission() {
    localStorage.setItem('consentGiven', 'true');
    closeModal();
    showChat();
}

/**
* Sends the query to the backend and logs the query. This is called when the user presses the button
* 
* 
* @return { Promise } Resolves with the
*/
function sendQuery() {
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value;
    if (!query) return;

    addMessage(query, 'user');
    queryInput.value = '';

    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';

    console.log('Sending query to backend:', query);

    const payload = JSON.stringify({ input: query });
    console.log('Payload being sent:', payload);

    fetch('https://rileysimpson.pythonanywhere.com/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: payload
    })
        .then(response => {
            console.log('Response status:', response.status); // Log response status
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, details: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            spinner.style.display = 'none';
            console.log('Chat response data:', data);

            if (data.response) {
                const markdown = data.response;
                addMessage(markdown, 'bot', true);
            } else {
                addMessage('Response Error: Sorry, something went wrong. Please try again.', 'bot');
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            console.error('Error in sendQuery:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        });
}

/**
* Resumes upload of file. This is called when user presses resume button. It will try to upload file to Samsung server and display success or failure message.
* 
* 
* @return { Promise } Promise that resolves when upload is resumed or rejects with error message if upload failed
*/
function uploadResume() {
    const resumeInput = document.getElementById('resume-input');
    const file = resumeInput.files[0];

    if (!file) {
        console.log('No file selected for upload.');
        addMessage('No file selected for upload.', 'bot');
        return;
    }

    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';

    const formData = new FormData();
    formData.append('resume', file);

    console.log('Uploading resume...');

    fetch('/upload_resume', {
        method: 'POST',
        body: formData,
    })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, details: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            spinner.style.display = 'none';
            console.log('Chat response data:', data);

            if (data.response) {
                const markdown = data.response;
                addMessage(markdown, 'bot', true);
            } else {
                addMessage('Failed to read resume, please try again.', 'bot');
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            console.error('Error in uploadResume:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        });
}

/**
* Adds a message to the chat. This is used to display messages that are not part of the message API but are useful for debugging purposes.
* 
* @param text - The text of the message. Should be parsable by markdown.
* @param sender - The sender of the message. Defaults to the currently logged in user.
* @param isMarkdown - Whether the message is markdown or plain text
*/
function addMessage(text, sender, isMarkdown = false) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    // Parses the text content of the message.
    if (isMarkdown) {
        messageDiv.innerHTML = marked.parse(text);
    } else {
        messageDiv.textContent = text;
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
* Starts a timer to show how long the user has left the chat session. After this time the chat session is ended
* 
* @param endTime - The time when the user should end the chat session
* 
* @return { Promise } A promise that resolves when the timer has been started and is resolved when the user should
*/
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
        // Clear the interval and end the session if timeLeft 0.
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

/**
* End chat session with local storage and remove message from local storage for next 5 minutes ( to avoid spam
*/
function endChatSession() {
    addMessage('You have used your allocated 5 minutes, thank you for your time :)', 'bot');

    localStorage.setItem('sessionEnded', 'true');
    localStorage.removeItem('endTime');

    setTimeout(() => {
        document.getElementById('chat-box').style.display = 'none';
        document.getElementById('query-input').style.display = 'none';
        document.querySelector('button[onclick="sendQuery()"]').style.display = 'none';
        document.getElementById('resume-upload').style.display = 'none';
        document.getElementById('feedback-form').style.display = 'block';

        const timerDisplay = document.getElementById('timer');
        // Removes the timer display from the timer display.
        if (timerDisplay) {
            timerDisplay.remove();
        }
    }, 5000);
}

/**
* Shows a message to the user that they have used 10 minutes and thank you for their time. Intended to be used in response to session ended
*/
function showSessionEndedMessage() {
    const container = document.querySelector('.container');
    container.innerHTML = `
        <p>You have used your allocated 10 minutes, thank you for your time :)</p>
        <div class="feedback-form">
            <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdC3bxESKoKFVEL7cr8CwLykODbvn1QLCwZVJZ080u5hCdsvA/viewform?embedded=true"
                    width="100%" height="400px" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
        </div>`;
}

/**
* Enables backdoor and removes time to end from localStorage for next time it takes to load the next
*/
function enableBackdoor() {
    localStorage.setItem('backdoor', 'true');
    localStorage.removeItem('endTime');
}

/**
* Disable backdoor and reload to avoid session issues. This is called on logout and when user logs
*/
function disableBackdoor() {
    localStorage.removeItem('backdoor');
    localStorage.removeItem('sessionEnded');
    window.location.reload();
}
