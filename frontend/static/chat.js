document.addEventListener('DOMContentLoaded', function () {
  const chatContainer = document.getElementById('chat-container');
  const messageInput = document.getElementById('message-input');
  const sendButton = document.getElementById('send-button');
  const logoutButton = document.getElementById('logout-button');

  let isAIThinking = false;
  let hasSentFirstMessage = false;

  checkUserRole();

  messageInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
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
    if (!token) throw new Error('Not authenticated');

    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ query: userMessage }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to fetch response.');
    }

    const data = await resp.json();
    if (!data || !Array.isArray(data.content)) {
      throw new Error('Malformed assistant response.');
    }
    return data;
  }

  async function uploadFile(file, userMessage = "") {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("Not authenticated");

    const formData = new FormData();
    formData.append("file", file);
    if (userMessage.trim() !== "") formData.append("query", userMessage.trim());

    const resp = await fetch("/api/chat/upload", {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
      body: formData
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to fetch response.");
    }

    const data = await resp.json();
    if (!data || !Array.isArray(data.content)) {
      throw new Error("Malformed assistant response.");
    }
    return data;
  }


  async function sendMessage() {
    const message = messageInput.value.trim();
    const fileInput = document.getElementById("file-input");
    const file = fileInput ? fileInput.files[0] : null;
    if ((message === "" && !file) || isAIThinking) return;


    if (message) addMessage(message, true);
    if (file) addMessage(`📄 Uploaded file: ${file.name}`, true);
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;
    isAIThinking = true;

    const thinkingIndicator = showThinkingIndicator();

    try {
      let aiResponse;
      if (file) {
        aiResponse = await uploadFile(file, message);
      } else {
        aiResponse = await getAIResponse(message);
      }
      thinkingIndicator.remove();

      const aiMessageElement = addMessage('', false);

      aiResponse.content.forEach((item) => {
        if (item.type === 'text') {
          aiMessageElement.innerHTML += `
            <div class="response-card reasoning-card">
              <div class="reasoning-header">Explanation</div>
              <div class="reasoning-body">${item.text}</div>
            </div>`;
        } else if (item.type === 'code') {
          aiMessageElement.innerHTML += `
            <div class="response-card code-card">
              <div class="code-header">💻 Python Code</div>
              <pre><code class="language-python">${item.text}</code></pre>
            </div>`;
        } else if (item.type === 'image' && item.url) {
          aiMessageElement.innerHTML += `
            <div class="response-card graph-card">
              <img src="${item.url}" alt="${item.subtype || 'graph'}" class="graph-image"/>
              <p class="graph-label">${(item.subtype || 'graph').toUpperCase()} Graph</p>
            </div>`;
        }
      });

      // Apply syntax highlighting after rendering
      if (window.hljs) hljs.highlightAll();

    } catch (error) {
      console.error('AI error:', error);
      thinkingIndicator.remove();
      addMessage('Error: ' + error.message, false);
    } finally {
      isAIThinking = false;
      sendButton.disabled = messageInput.value.trim() === '';
      if (fileInput) fileInput.value = "";
    }
  }

    async function loadChatHistory() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await fetch('/api/history', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Failed to fetch history');

      const data = await response.json();
      const history = data.history;
      if (!history || history.length === 0) return;

      for (const item of history) {
        const userMsg = item.message;
        const responseText = item.response;
        const cfgURL = item.cfg_image_url;
        const dfgURL = item.dfg_image_url;
        const reasoning = item.reasoning;

        // Handle the welcome message case — no userMsg and contains "Welcome!"
        const isWelcome =
          !userMsg &&
          responseText &&
          responseText.includes('Welcome! I am a chatbot programmed to assist you');

        if (isWelcome) {
          const aiMessageElement = addMessage('', false);

          // hide the AI avatar for the welcome message
          const avatar = aiMessageElement.parentElement.querySelector('.avatar');
          if (avatar) avatar.style.visibility = 'hidden';

          aiMessageElement.innerHTML += `
            <div class="welcome-message">
              <span class="welcome-highlight">Welcome!</span>
              <span class="welcome-text"> I am a chatbot programmed to assist you with Python code.</span>
            </div>`;
          continue;
        }



        // Normal chat history rendering
        addMessage(userMsg, true);
        const aiMessageElement = addMessage('', false);

        if (reasoning) {
          aiMessageElement.innerHTML += `
            <div class="response-card reasoning-card">
              <div class="reasoning-header">Explanation</div>
              <div class="reasoning-body">${reasoning}</div>
            </div>`;
        }

        if (responseText) {
          aiMessageElement.innerHTML += `
            <div class="response-card code-card">
              <div class="code-header">💻 Python Code</div>
              <pre><code class="language-python">${responseText}</code></pre>
            </div>`;
        }

        if (cfgURL) {
          aiMessageElement.innerHTML += `
            <div class="response-card graph-card">
              <img src="${cfgURL}" alt="CFG Graph" class="graph-image"/>
              <p class="graph-label">CFG Graph</p>
            </div>`;
        }

        if (dfgURL) {
          aiMessageElement.innerHTML += `
            <div class="response-card graph-card">
              <img src="${dfgURL}" alt="DFG Graph" class="graph-image"/>
              <p class="graph-label">DFG Graph</p>
            </div>`;
        }
      }

      if (window.hljs) hljs.highlightAll();
    } catch (err) {
      console.error('Failed to load chat history:', err);
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

  async function checkUserRole() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const res = await fetch('/api/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();

      if (data.role === 'generate code') {
        const uploadWrapper = document.querySelector('.upload-wrapper');
        if (uploadWrapper) uploadWrapper.style.display = 'none';
      }

    } catch (e) {
      console.error('Failed to check user role:', e);
    }
  }


  if (!hasSentFirstMessage) loadChatHistory();
  scrollToBottom();

  const uploadButton = document.getElementById("upload-button");
  const fileInput = document.getElementById("file-input");

  uploadButton.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => {
      const selectedFile = fileInput.files[0];
      const uploadLabel = document.getElementById("upload-label");

      if (selectedFile) {
        uploadLabel.textContent = `📄 Selected: ${selectedFile.name}`;
        uploadLabel.style.color = "#007bff";
      } else {
        uploadLabel.textContent = "No file selected";
        uploadLabel.style.color = "#666";
      }
  });

});
