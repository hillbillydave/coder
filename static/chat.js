// static/chat.js
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatLog = document.getElementById('chat-log');
    let eventSource; // Variable to hold our connection

    const sendMessage = () => {
        const messageText = chatInput.value.trim();
        if (messageText === '') return;

        appendMessage('You', messageText, 'user-message');
        chatInput.value = '';
        chatInput.disabled = true; // Disable input while AI is typing
        sendButton.disabled = true;

        // Create a new response container for the AI
        const aiResponseContainer = appendMessage('Vespera', '', 'daisy-message');
        const aiMessageSpan = aiResponseContainer.querySelector('.log-message');
        aiMessageSpan.classList.add('typing-cursor'); // Add cursor effect

        // Close any existing connection
        if (eventSource) {
            eventSource.close();
        }

        // --- NEW: Open a streaming connection ---
        eventSource = new EventSource(`/stream_chat?message=${encodeURIComponent(messageText)}`); // Send message as a query param for simplicity in this new route
        
        let fullResponse = "";

        // Listen for new message chunks
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            fullResponse += data.chunk;
            aiMessageSpan.textContent = fullResponse;
            chatLog.scrollTop = chatLog.scrollHeight; // Keep scrolled to bottom
        };

        // Listen for the special "stream-end" event
        eventSource.addEventListener('stream-end', function(event) {
            eventSource.close();
            chatInput.disabled = false;
            sendButton.disabled = false;
            aiMessageSpan.classList.remove('typing-cursor');
            chatInput.focus();
        });

        // Listen for errors
        eventSource.onerror = function(event) {
            console.error("EventSource failed:", event);
            aiMessageSpan.textContent = fullResponse + " (Connection error)";
            eventSource.close();
            chatInput.disabled = false;
            sendButton.disabled = false;
            aiMessageSpan.classList.remove('typing-cursor');
        };
    };
    
    // (This function is the same)
    const appendMessage = (sender, text, cssClass) => {
        const msg = document.createElement('div');
        msg.className = cssClass;
        msg.innerHTML = `<span class="log-source">${sender} →</span> <span class="log-message">${text}</span>`;
        chatLog.appendChild(msg);
        chatLog.scrollTop = chatLog.scrollHeight;
        return msg;
    };

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
});```

.typing-cursor::after {
    content: '▋';
    animation: blink 1s step-end infinite;
}
@keyframes blink { 50% { opacity: 0; } }
