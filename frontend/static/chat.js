document.addEventListener('DOMContentLoaded', function () {
    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const logoutButton = document.getElementById('logout-button');

    let isAIThinking = false;
    let hasSentFirstMessage = false;

    checkDecisionStatus();

    messageInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        sendButton.disabled = this.value.trim() === '' || isAIThinking;
    });

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';

        const avatar = document.createElement('div');
        avatar.className = isUser ? 'avatar user-avatar' : 'avatar bot-avatar';
        avatar.textContent = isUser ? 'You' : 'AI';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        scrollToBottom();

        if (isUser) {
            contentDiv.textContent = content;
        }

        return contentDiv;
    }

    function showThinkingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';

        const avatar = document.createElement('div');
        avatar.className = 'avatar bot-avatar';
        avatar.textContent = 'AI';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';

        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'thinking-indicator';

        const spinner = document.createElement('div');
        spinner.className = 'spinner';

        const text = document.createElement('div');
        text.className = 'thinking-text';
        text.textContent = 'AI is thinking...';

        thinkingDiv.appendChild(spinner);
        thinkingDiv.appendChild(text);
        contentDiv.appendChild(thinkingDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);

        scrollToBottom();
        return messageDiv;
    }

   async function getAIResponse(userMessage) {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error("Not authenticated");

  const resp = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
    body: JSON.stringify({ query: userMessage })
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch response.");
  }

  const data = await resp.json();
  // data must have { role, content: [...] }
  if (!data || !Array.isArray(data.content)) {
    throw new Error("Malformed assistant response.");
  }
  return data;
}

async function sendMessage() {
  const message = messageInput.value.trim();
  if (message === '' || isAIThinking) return;

  addMessage(message, true);
  messageInput.value = '';
  messageInput.style.height = 'auto';
  sendButton.disabled = true;
  isAIThinking = true;

  const thinkingIndicator = showThinkingIndicator();

  try {
    const aiResponse = await getAIResponse(message);
    thinkingIndicator.remove();

    const aiMessageElement = addMessage('', false);

    aiResponse.content.forEach(item => {
      if (item.type === "text") {
        aiMessageElement.innerHTML += `<div class="response-card">${item.text}</div>`;
      } else if (item.type === "code") {
        aiMessageElement.innerHTML += `<pre class="response-card"><code>${item.text}</code></pre>`;
      } else if (item.type === "image" && item.url) {
        aiMessageElement.innerHTML += `
          <div class="response-card">
            <img src="${item.url}" alt="${item.subtype || 'graph'}" class="graph-image"/>
            <p class="graph-label">${(item.subtype || 'graph').toUpperCase()} Graph</p>
          </div>`;
      }
    });

  } catch (error) {
    console.error('AI error:', error);
    thinkingIndicator.remove();
    addMessage("Error: " + error.message, false);
  } finally {
    isAIThinking = false;
    sendButton.disabled = messageInput.value.trim() === '';
  }
}


    async function loadChatHistory() {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            const response = await fetch("/api/history", {
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (!response.ok) throw new Error("Failed to fetch history");

            const data = await response.json();
            const history = data.history;

            if (!history || history.length === 0) return;

            for (const item of history) {
                const userMsg = item.message;
                const responseText = item.response;
                const cfgURL = item.cfg_image_url;
                const dfgURL = item.dfg_image_url;

                // Add user message
                addMessage(userMsg, true);

                // Build bot message
                const aiMessageElement = addMessage('', false);
                aiMessageElement.innerHTML = `
                    <div class="response-card"><pre><code>${responseText}</code></pre></div>
                `;

                if (cfgURL) {
                    aiMessageElement.innerHTML += `
                        <div class="response-card">
                            <img src="${cfgURL}" alt="CFG Graph" class="graph-image"/>
                            <p class="graph-label">CFG Graph</p>
                        </div>
                    `;
                }

                if (dfgURL) {
                    aiMessageElement.innerHTML += `
                        <div class="response-card">
                            <img src="${dfgURL}" alt="DFG Graph" class="graph-image"/>
                            <p class="graph-label">DFG Graph</p>
                        </div>
                    `;
                }
            }
        } catch (err) {
            console.error("Failed to load chat history:", err);
        }
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    });

    async function checkDecisionStatus() {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            const res = await fetch("/api/me", {
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (!res.ok) return;
            const data = await res.json();

            if (data.decision === "1" || data.decision === "0") {
                messageInput.disabled = true;
                sendButton.disabled = true;
            }
        } catch (e) {
            console.error("Failed to check decision status:", e);
        }
    }

    // Load chat history on first load
    if (!hasSentFirstMessage) loadChatHistory();
    scrollToBottom();
});
