/**
 * Hadron Core: Sovereign Minimalist Interface (v7.0)
 * Fixed visibility and input capture logic.
 */

class HadronStore {
    constructor() {
        this.state = {
            isProcessing: false,
            isConnected: false
        };
        this.listeners = [];
    }

    update(patch) {
        this.state = { ...this.state, ...patch };
        this.listeners.forEach(fn => fn(this.state));
    }

    subscribe(fn) {
        this.listeners.push(fn);
    }
}

const Store = new HadronStore();

class HadronInterface {
    constructor() {
        this.stream = document.getElementById('neural-stream');
        this.form = document.getElementById('command-form');
        this.input = document.getElementById('citizen-input');
        this.btn = document.getElementById('execute-btn');
        this.trace = document.getElementById('thought-trace');
        this.statusText = document.getElementById('status-text');
        this.modelDisplay = document.getElementById('active-model');

        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUserInquiry(this.input.value);
        });
        
        document.querySelectorAll('.orb').forEach(orb => {
            orb.addEventListener('click', (e) => {
                e.stopPropagation();
                const query = orb.getAttribute('data-query') || orb.dataset.query;
                console.log("[HUD] Orb Clicked. Query:", query);
                if (query) this.handleUserInquiry(query);
            });
        });

        Store.subscribe((state) => this.syncUI(state));
        this.connectTelemetry();
    }

    connectTelemetry() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/v6/hadron/telemetry`;
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            Store.update({ isConnected: true });
            this.statusText.textContent = "Neural Link Active";
        };

        socket.onmessage = () => { /* Metrics inactive */ };

        socket.onclose = () => {
            Store.update({ isConnected: false });
            this.statusText.textContent = "Reconnecting...";
            setTimeout(() => this.connectTelemetry(), 5000);
        };
    }

    async handleUserInquiry(query) {
        const text = query.trim();
        if (!text || Store.state.isProcessing) return;

        // Clear input and append user message
        this.input.value = '';
        this.appendMessage('citizen', text);
        Store.update({ isProcessing: true });

        try {
            const response = await fetch('/api/v1/reason', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: text, session_id: 'sovereign_citizen' })
            });

            const data = await response.json();
            if (data.status === "bridge_fault" || data.status === "quarantine" || data.status === "latency_limit") {
                this.appendMessage('hadron', `FAULT: ${data.error || "Neural bridge failed."}`);
                return;
            }

            const answer = data.answer || data.response?.answer || "Critical fault in neural conduit.";
            await this.typeResponse(answer, data.model_active);
        } catch (err) {
            this.appendMessage('hadron', `Neural conduit collapse: ${err.message}`);
        } finally {
            Store.update({ isProcessing: false });
        }
    }

    appendMessage(role, text) {
        const bubble = document.createElement('div');
        bubble.className = `thought-bubble ${role}`;
        
        const tag = document.createElement('span');
        tag.className = 'role-tag';
        tag.textContent = role === 'hadron' ? 'Hadron Core' : 'Citizen';
        
        const content = document.createElement('div');
        content.className = 'bubble-content';
        content.textContent = text;
        
        bubble.appendChild(tag);
        bubble.appendChild(content);
        
        this.stream.appendChild(bubble);
        this.scrollToBottom();
    }

    scrollToBottom() {
        requestAnimationFrame(() => {
            this.stream.scrollTo({ top: this.stream.scrollHeight, behavior: 'smooth' });
        });
    }

    async typeResponse(text, activeModel) {
        if (activeModel) this.modelDisplay.textContent = `Conduit: ${activeModel}`;
        
        const bubble = document.createElement('div');
        bubble.className = `thought-bubble hadron`;
        bubble.innerHTML = `
            <span class="role-tag">Hadron Core</span>
            <div class="bubble-content"></div>
            <div class="meta-info"><span class="grounding-tag">Verified Source</span></div>
        `;
        this.stream.appendChild(bubble);
        
        const contentDiv = bubble.querySelector('.bubble-content');
        const words = text.split(' ');
        
        for (let i = 0; i < words.length; i++) {
            contentDiv.textContent += words[i] + ' ';
            this.scrollToBottom();
            if (i % 3 === 0) await new Promise(r => setTimeout(r, 10));
        }
    }

    syncUI(state) {
        this.btn.disabled = state.isProcessing;
        this.input.disabled = state.isProcessing;
        this.trace.classList.toggle('active', state.isProcessing);
        if (!state.isProcessing) this.input.focus();
    }
}

window.addEventListener('DOMContentLoaded', () => new HadronInterface());
