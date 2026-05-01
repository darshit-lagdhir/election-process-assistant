const API_BASE = "http://localhost:8000";
let sessionId = null;
let electionData = null;
let currentPhase = 'registration';

// Systemic Victory Log
const logStatus = (msg) => {
    const statusEl = document.getElementById('system-status');
    if (statusEl) statusEl.innerText = msg;
    console.log(`[SYSTEM LOG] ${msg}`);
};

// Sector Epsilon: The Resilient Conduit
async function fetchWithRetry(url, options = {}, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
            return await response.json();
        } catch (err) {
            logStatus(`RECONNECTION ATTEMPT ${i+1}/${retries}...`);
            if (i === retries - 1) throw err;
            await new Promise(r => setTimeout(r, 1000 * (i + 1)));
        }
    }
}

// Sector Gamma: Progressive Disclosure Rendering
function renderTimeline() {
    const container = document.getElementById('timeline-container');
    if (!electionData) return;

    container.innerHTML = electionData.phases.map(phase => `
        <div class="phase-card ${phase.id === currentPhase ? 'active' : ''}" id="phase-${phase.id}" onclick="setPhase('${phase.id}')">
            <h3 class="phase-title">${phase.title}</h3>
            <p class="phase-desc">${phase.description}</p>
            <div class="status-badge status-${phase.status}">${phase.status.toUpperCase()}</div>
        </div>
    `).join('');
    
    logStatus(`TIMELINE TOPOLOGY STABLE | PHASE: ${currentPhase.toUpperCase()}`);
}

function setPhase(phaseId) {
    currentPhase = phaseId;
    renderTimeline();
    addMessage('ai', `Navigated to ${phaseId.toUpperCase()} phase. How can I assist you with this stage?`);
}

// Sector Alpha: Agentic Interaction
async function dispatchQuery() {
    const input = document.getElementById('user-input');
    const query = input.value.trim();
    if (!query) return;

    addMessage('user', query);
    input.value = '';
    
    logStatus("PROCESSING COGNITIVE KERNEL...");

    try {
        const data = await fetchWithRetry(`${API_BASE}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, session_id: sessionId })
        });

        sessionId = data.session_id;
        addMessage('ai', data.response);

        if (data.phase && data.phase !== currentPhase) {
            currentPhase = data.phase;
            renderTimeline();
        }
    } catch (err) {
        addMessage('ai', "SYSTEMIC ALERT: Connection to Hadronic Core lost. Falling back to local knowledge.");
        logStatus("PHALANX ALERT: BACKEND OFFLINE");
    }
}

function addMessage(type, text) {
    const history = document.getElementById('chat-history');
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.innerText = text;
    history.appendChild(msg);
    history.scrollTop = history.scrollHeight;
}

// Sector Delta: Command Palette & Accessibility
document.addEventListener('keydown', (e) => {
    // Ctrl+K for Command Palette
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const cmd = prompt("Enter Command (e.g., 'jump registration', 'status', 'help'):");
        if (cmd) processCommand(cmd.toLowerCase());
    }
});

function processCommand(cmd) {
    if (cmd.startsWith('jump ')) {
        const target = cmd.split(' ')[1];
        if (['registration', 'verification', 'polling', 'results'].includes(target)) {
            setPhase(target);
        } else {
            alert("Invalid phase target.");
        }
    } else if (cmd === 'status') {
        alert(`System Status: GENESIS ACTIVE\nMetabolic Perimeter: STABLE\nPhase: ${currentPhase}`);
    } else {
        alert("Commands: 'jump <phase>', 'status', 'help'");
    }
}

// Initialization
document.getElementById('send-btn').onclick = dispatchQuery;
document.getElementById('user-input').onkeypress = (e) => { if (e.key === 'Enter') dispatchQuery(); };

(async () => {
    try {
        electionData = await fetchWithRetry(`${API_BASE}/data`);
        renderTimeline();
        logStatus("SYSTEMIC GENESIS COMPLETE | SOVEREIGNTY ACHIEVED");
    } catch (err) {
        logStatus("BOOT FAILURE: HADRONIC CORE UNREACHABLE");
        alert("The Hadronic Core is not responding. Ensure the backend is active.");
    }
})();
