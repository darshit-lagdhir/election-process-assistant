/**
 * Election Assistant: Frontend Logic
 * Refactored for professional Chat UI/UX.
 */

class StateManager {
    constructor() {
        this.state = {
            isConnected: false,
            isProcessing: false,
            history: []
        };
        this.subscribers = [];
    }

    update(newState) {
        this.state = { ...this.state, ...newState };
        this.subscribers.forEach(sub => sub(this.state));
    }

    subscribe(callback) {
        this.subscribers.push(callback);
    }
}

const Store = new StateManager();

class APIProtocol {
    static async transmit(endpoint, payload) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP_${response.status}`);
            return await response.json();
        } catch (err) {
            console.error("API_PROTOCOL_ERROR", err);
            throw err;
        }
    }
}

class ChatInterface {
    constructor() {
        this.messagesList = document.getElementById('messages-list');
        this.chatForm = document.getElementById('chat-form');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.connectionStatus = document.getElementById('connection-status');
        
        this.init();
    }

    init() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        Store.subscribe((state) => this.renderState(state));
        
        this.initializeConnection();
    }

    initializeConnection() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/v6/hadron/telemetry`;
        
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            Store.update({ isConnected: true });
            this.connectionStatus.textContent = "Securely Connected";
            this.connectionStatus.style.color = "#22c55e";
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // We can handle background updates here if needed
        };

        this.socket.onclose = () => {
            Store.update({ isConnected: false });
            this.connectionStatus.textContent = "Disconnected. Reconnecting...";
            this.connectionStatus.style.color = "#ef4444";
            setTimeout(() => this.initializeConnection(), 5000);
        };
    }

    async handleSubmit(e) {
        e.preventDefault();
        const query = this.userInput.value.trim();
        if (!query || Store.state.isProcessing) return;

        // User Message
        this.appendMessage('user', query);
        this.userInput.value = '';
        Store.update({ isProcessing: true });

        // Show Processing
        this.showProcessing();

        try {
            const result = await APIProtocol.transmit('/api/v6/hadron/reason', { query });
            this.hideProcessing();
            
            // Core Extraction Logic: Navigate the radiant response packet
            let answer = "No response received.";
            if (result.response && result.response.answer) {
                answer = result.response.answer;
            } else if (result.answer) {
                answer = result.answer;
            }
            
            this.appendMessage('ai', answer);
        } catch (error) {
            this.hideProcessing();
            this.appendMessage('ai', "I'm sorry, I encountered a communication error. Please try again.");
        } finally {
            Store.update({ isProcessing: false });
        }
    }

    appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.innerHTML = `<div class="message-content">${text}</div>`;
        this.messagesList.appendChild(msgDiv);
        
        // Auto-scroll to bottom
        const container = document.getElementById('chat-container');
        container.scrollTop = container.scrollHeight;
    }

    showProcessing() {
        const procDiv = document.createElement('div');
        procDiv.id = 'processing-indicator';
        procDiv.className = 'message ai processing';
        procDiv.innerHTML = `<div class="message-content">Thinking...</div>`;
        this.messagesList.appendChild(procDiv);
        
        const container = document.getElementById('chat-container');
        container.scrollTop = container.scrollHeight;
    }

    hideProcessing() {
        const indicator = document.getElementById('processing-indicator');
        if (indicator) indicator.remove();
    }

    renderState(state) {
        this.sendBtn.disabled = state.isProcessing;
        this.userInput.disabled = state.isProcessing;
        if (!state.isProcessing) {
            this.userInput.focus();
        }
    }
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});
