/**
 * Main application controller for the Election Process Assistant.
 */

class StateManager {
    constructor() {
        this.state = {
            currentPhase: 'registration',
            session_id: null,
            isHydrated: false,
            latency: 0
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

class OcularAperture {
    constructor() {
        this.chatConduit = document.getElementById('chat-conduit');
        this.timelineConduit = document.getElementById('timeline-conduit');
        this.inputForm = document.getElementById('input-form');
        this.queryInput = document.getElementById('user-query');
        this.statusText = document.getElementById('status-text');
        
        this.init();
    }

    async init() {
        this.inputForm.addEventListener('submit', (e) => this.handleTransmission(e));
        Store.subscribe((state) => this.render(state));
        
        await this.hydrateSubstrate();
    }

    /**
     * Real-time data hydration.
     */
    async hydrateSubstrate() {
        try {
            const response = await fetch('http://127.0.0.1:8080/data');
            const { data, checksum } = await response.json();
            this.renderTimeline(data.phases);
            Store.update({ isHydrated: true, checksum });
            this.logTelemetry("SUBSTRATE_SYNC", { checksum });
        } catch (error) {
            this.handleSystemicFault("Hydration Failure", error);
        }
    }

    /**
     * System metrics and logging.
     */
    logTelemetry(event, details) {
        console.log(`[TELEMETRY] ${event}`, details);
        const shield = document.getElementById('telemetry-shield');
        shield.textContent = `Event: ${event} Status: Stable`;
    }

    renderTimeline(phases) {
        this.timelineConduit.innerHTML = phases.map(phase => `
            <div class="timeline-node ${Store.state.currentPhase === phase.id ? 'active' : ''}" 
                 onclick="window.aperture.jumpToPhase('${phase.id}')"
                 role="button"
                 aria-pressed="${Store.state.currentPhase === phase.id}">
                <strong>${phase.title}</strong>
                <p style="font-size: 0.75rem; color: var(--radiance-text-secondary);">${phase.id}</p>
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

        // Resilience and retry logic
        const transmit = async (retries = 3) => {
            try {
                const response = await fetch('http://127.0.0.1:8080/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        query: sanitizedQuery, 
                        session_id: Store.state.session_id 
                    })
                });
                if (!response.ok) throw new Error(`HTTP_${response.status}`);
                return await response.json();
            } catch (err) {
                if (retries > 0) {
                    this.logTelemetry("RETRANSMISSION_ATTEMPT", { remaining: retries });
                    await new Promise(r => setTimeout(r, 1000));
                    return transmit(retries - 1);
                }
                throw err;
            }
        };

        const showProcessing = () => {
            const indicator = document.createElement('div');
            indicator.id = 'processing-indicator';
            indicator.className = 'message ai processing';
            indicator.textContent = 'Processing...';
            this.chatConduit.appendChild(indicator);
            this.chatConduit.scrollTop = this.chatConduit.scrollHeight;
        };

        const hideProcessing = () => {
            const indicator = document.getElementById('processing-indicator');
            if (indicator) indicator.remove();
        };

        try {
            showProcessing();
            const result = await transmit();
            hideProcessing();
            const latency = performance.now() - startTime;
            
            this.appendMessage('ai', result.response);
            Store.update({ 
                currentPhase: result.phase, 
                session_id: result.session_id,
                latency: latency
            });
            this.logTelemetry("MODEL_RESPONSE_PULSE", { latency: latency.toFixed(2) });
            
        } catch (error) {
            this.appendMessage('ai', "Systemic interruption detected after re-transmission attempts. Please check your connection.");
            this.handleSystemicFault("Transmission Failure", error);
        } finally {
            this.queryInput.disabled = false;
            this.queryInput.focus();
        }
    }

    appendMessage(role, text) {
        const msg = document.createElement('div');
        msg.className = `message ${role}`;
        msg.textContent = text;
        this.chatConduit.appendChild(msg);
        this.chatConduit.scrollTop = this.chatConduit.scrollHeight;
    }

    jumpToPhase(phaseId) {
        Store.update({ currentPhase: phaseId });
        this.appendMessage('ai', `Navigating to ${phaseId} module. What specific information do you require?`);
        this.hydrateSubstrate(); // Refresh to ensure sync
    }

    handleSystemicFault(type, error) {
        console.error(`[FAULT] ${type}:`, error);
        this.statusText.textContent = `Status: ${type}`;
        this.statusText.parentElement.querySelector('.status-dot').style.background = '#ef4444';
    }

    render(state) {
        // Granular re-rendering logic to reduce metabolic overhead
        const timelineActive = document.querySelector('.timeline-node.active');
        const activeId = timelineActive ? timelineActive.querySelector('p').textContent : null;
        
        if (state.currentPhase !== activeId) {
            this.hydrateSubstrate(); 
        }
    }
}

// Global exposure for event handlers
window.aperture = new OcularAperture();
