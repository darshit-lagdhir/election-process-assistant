/**
 * THE FRONTEND OCULAR APERTURE: ELECTION PROCESS ASSISTANT
 * THE SINGULARITY SCALE CONVERGENCE (PROMPT 56)
 */

class StateManager {
    constructor() {
        this.state = {
            currentPhase: 'registration',
            session_id: localStorage.getItem('assistant_sid') || null,
            isHydrated: false,
            latency: 0,
            radiance: 100,
            metabolism: { cpu: 0, mem: 0 },
            history: []
        };
        this.subscribers = [];
    }

    update(newState) {
        this.state = { ...this.state, ...newState };
        if (newState.session_id) localStorage.setItem('assistant_sid', newState.session_id);
        this.subscribers.forEach(sub => sub(this.state));
    }

    subscribe(callback) {
        this.subscribers.push(callback);
    }
}

const Store = new StateManager();

class ConduitProtocol {
    /**
     * Handles secure, high-frequency data transmission between the Frontier and the Hadron Core.
     */
    static async transmit(endpoint, payload) {
        const url = `http://127.0.0.1:8000${endpoint}`;
        const headers = { 
            'Content-Type': 'application/json',
            'X-Session-Token': Store.state.session_token || ''
        };
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`PROTOCOL_FAULT_${response.status}`);
            return await response.json();
        } catch (err) {
            console.error("[CONDUIT_FAULT]", err);
            throw err;
        }
    }
}

class OcularAperture {
    constructor() {
        this.chatConduit = document.getElementById('chat-conduit');
        this.timelineConduit = document.getElementById('timeline-conduit');
        this.inputForm = document.getElementById('input-form');
        this.queryInput = document.getElementById('user-query');
        this.statusText = document.getElementById('status-text');
        this.telemetryShield = document.getElementById('telemetry-shield');
        
        this.init();
    }

    async init() {
        this.inputForm.addEventListener('submit', (e) => this.handleTransmission(e));
        Store.subscribe((state) => this.render(state));
        
        // Start background metabolic sync
        this.beginMetabolicSync();
        await this.hydrateSubstrate();
    }

    async hydrateSubstrate() {
        try {
            const response = await fetch('http://127.0.0.1:8000/data');
            const { data, checksum } = await response.json();
            this.renderTimeline(data.phases);
            Store.update({ isHydrated: true, checksum });
        } catch (error) {
            this.handleSystemicFault("Hydration Failure", error);
        }
    }

    async beginMetabolicSync() {
        setInterval(async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/health/diagnostics');
                const stats = await response.json();
                Store.update({ 
                    radiance: stats.cryptography.security_score,
                    metabolism: { 
                        cpu: stats.metabolism.cpu_percent, 
                        mem: stats.metabolism.memory_mb 
                    }
                });
            } catch (err) {
                // Background sync failure is non-blocking
            }
        }, 5000);
    }

    renderTimeline(phases) {
        this.timelineConduit.innerHTML = phases.map(phase => `
            <div class="timeline-node ${Store.state.currentPhase === phase.id ? 'active' : ''}" 
                 onclick="window.aperture.jumpToPhase('${phase.id}')">
                <div class="node-glow"></div>
                <strong>${phase.title}</strong>
                <p>${phase.id.toUpperCase()}</p>
            </div>
        `).join('');
    }

    async handleTransmission(e) {
        e.preventDefault();
        const query = this.queryInput.value.trim();
        if (!query) return;

        const sanitizedQuery = query.replace(/[<>]/g, ""); 
        this.appendMessage('user', sanitizedQuery);
        this.queryInput.value = '';
        this.queryInput.disabled = true;

        const startTime = performance.now();
        this.showProcessing();

        try {
            const result = await ConduitProtocol.transmit('/query', {
                query: sanitizedQuery,
                session_id: Store.state.session_id
            });
            
            const latency = performance.now() - startTime;
            this.hideProcessing();
            this.appendMessage('ai', result.response);
            
            Store.update({ 
                currentPhase: result.phase, 
                session_id: result.session_id,
                latency: latency
            });

            // Update Ocular status
            this.statusText.textContent = `Phase: ${result.phase.toUpperCase()}`;
            
        } catch (error) {
            this.hideProcessing();
            this.appendMessage('ai', "Systemic interruption detected. Re-aligning Hadron Core...");
            this.handleSystemicFault("Transmission Failure", error);
        } finally {
            this.queryInput.disabled = false;
            this.queryInput.focus();
        }
    }

    appendMessage(role, text) {
        const msg = document.createElement('div');
        msg.className = `message ${role}`;
        msg.innerHTML = `<div class="message-content">${text}</div><div class="message-timestamp">${new Date().toLocaleTimeString()}</div>`;
        this.chatConduit.appendChild(msg);
        this.chatConduit.scrollTop = this.chatConduit.scrollHeight;
    }

    showProcessing() {
        const loader = document.createElement('div');
        loader.id = 'aperture-loader';
        loader.className = 'message ai loading';
        loader.innerHTML = '<div class="loading-pulse"></div> Processing Neural Pulse...';
        this.chatConduit.appendChild(loader);
        this.chatConduit.scrollTop = this.chatConduit.scrollHeight;
    }

    hideProcessing() {
        const loader = document.getElementById('aperture-loader');
        if (loader) loader.remove();
    }

    jumpToPhase(phaseId) {
        Store.update({ currentPhase: phaseId });
        this.appendMessage('ai', `Navigating to ${phaseId.toUpperCase()} module. Systemic integrity confirmed.`);
        this.hydrateSubstrate();
    }

    handleSystemicFault(type, error) {
        console.error(`[FAULT] ${type}:`, error);
        this.statusText.textContent = `FAULT: ${type}`;
        document.querySelector('.status-dot').classList.add('error');
    }

    render(state) {
        // Update Telemetry Shield
        this.telemetryShield.innerHTML = `
            <div class="metric">LAT: ${state.latency.toFixed(0)}ms</div>
            <div class="metric">RAD: ${state.radiance}%</div>
            <div class="metric">CPU: ${state.metabolism.cpu}%</div>
            <div class="metric">MEM: ${state.metabolism.mem.toFixed(1)}MB</div>
        `;

        // Update Timeline state
        document.querySelectorAll('.timeline-node').forEach(node => {
            const id = node.querySelector('p').textContent.toLowerCase();
            node.classList.toggle('active', id === state.currentPhase);
        });
    }
}

window.aperture = new OcularAperture();
