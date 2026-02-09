/* =========================================
   PART 4: DASHBOARD LOGIC (Chat & UI)
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const chatStream = document.getElementById('chat-stream');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const routeCard = document.getElementById('route-card');
    const routeTimeline = document.getElementById('route-timeline');
    const clearBtn = document.querySelector('button[title="Clear Chat"]');
    const themeToggle = document.getElementById('theme-toggle');

    // --- Theme Logic ---
    const html = document.documentElement;
    const themeIcon = themeToggle.querySelector('i');

    if (localStorage.getItem('theme') === 'dark') {
        html.setAttribute('data-theme', 'dark');
        themeIcon.className = 'ri-sun-line';
    }

    themeToggle.addEventListener('click', () => {
        const isDark = html.getAttribute('data-theme') === 'dark';
        if (isDark) {
            html.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
            themeIcon.className = 'ri-moon-line';
        } else {
            html.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeIcon.className = 'ri-sun-line';
        }
    });

    // --- State ---
    let isProcessing = false;

    // --- Event Listeners ---
    sendBtn.addEventListener('click', handleSend);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            chatStream.innerHTML = '';
            addBotMessage("Chat cleared. Where would you like to go?");
            routeCard.classList.add('hidden');
        });
    }

    // Expose Quick Chip handler to global scope for HTML onclick attributes
    window.sendQuick = (text) => {
        userInput.value = text;
        handleSend();
    };

    // --- Core Functions ---

    async function handleSend() {
        const text = userInput.value.trim();
        if (!text || isProcessing) return;

        // 1. Add User Message
        addUserMessage(text);
        userInput.value = '';
        isProcessing = true;

        // 2. Show Loading Indicator
        const loadingId = addLoadingIndicator();

        try {
            // 3. Call Backend API (To be connected in Part 5)
            // We expect the backend to be at /api/chat
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) throw new Error("Network response was not ok");

            const data = await response.json();

            // 4. Handle Response
            removeMessage(loadingId);
            
            // Display Bot Response
            if (data.response) {
                addBotMessage(data.response);
            }

            // Update Route Panel if route data exists
            if (data.route_info) {
                updateRoutePanel(data.route_info);
            }

        } catch (error) {
            console.error("Chat Error:", error);
            removeMessage(loadingId);
            addBotMessage("⚠️ I'm having trouble connecting to the server. Please ensure the backend (Part 5) is running.");
        } finally {
            isProcessing = false;
            scrollToBottom();
        }
    }

    // --- UI Helpers ---

    function addUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user';
        msgDiv.innerHTML = `
            <div class="bubble">
                <p>${escapeHtml(text)}</p>
            </div>
            <span class="time">Just now</span>
        `;
        chatStream.appendChild(msgDiv);
        scrollToBottom();
    }

    function addBotMessage(htmlContent) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot';
        
        // Allow HTML in bot responses (for bolding, etc.)
        msgDiv.innerHTML = `
            <div class="avatar"><i class="ri-robot-line"></i></div>
            <div class="bubble">
                <p>${formatBotText(htmlContent)}</p>
            </div>
            <span class="time">Just now</span>
        `;
        chatStream.appendChild(msgDiv);
        scrollToBottom();
    }

    function addLoadingIndicator() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.id = id;
        msgDiv.className = 'message bot';
        msgDiv.innerHTML = `
            <div class="avatar"><i class="ri-robot-line"></i></div>
            <div class="bubble">
                <p><i class="ri-loader-4-line"></i> Thinking...</p>
            </div>
        `;
        chatStream.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatBotText(text) {
        // Convert **bold** to <strong> and newlines to <br>
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
    }

    // --- Route Panel Logic ---

    function updateRoutePanel(route) {
        if (!route) return;

        // Show Card
        routeCard.classList.remove('hidden');

        // Update Stats
        document.getElementById('stat-stations').innerText = route.total_stations;
        document.getElementById('stat-changes').innerText = route.interchanges;
        
        // Estimate Time (2 mins per station + 5 mins per interchange)
        const time = (route.total_stations * 2) + (route.interchanges * 5);
        document.getElementById('route-time').innerText = `${time} min`;

        // Build Timeline
        routeTimeline.innerHTML = '';
        
        if (route.steps && route.steps.length > 0) {
            route.steps.forEach((step, index) => {
                const isStart = index === 0;
                const isEnd = index === route.steps.length - 1;
                
                const stepDiv = document.createElement('div');
                stepDiv.className = 'timeline-step';
                if (isStart) stepDiv.classList.add('start');
                if (isEnd) stepDiv.classList.add('end');
                if (step.line !== route.steps[Math.max(0, index-1)].line && !isStart) stepDiv.classList.add('change');
                
                const lineColor = getLineColor(step.line);
                
                stepDiv.innerHTML = `
                    <div class="step-content">
                        <span class="step-line" style="background-color: ${lineColor}">${step.line}</span>
                        <div class="step-station">${step.start}</div>
                        <div class="step-detail">
                            <i class="ri-arrow-down-line"></i> Ride ${step.stops} stops to ${step.end}
                        </div>
                    </div>
                `;
                routeTimeline.appendChild(stepDiv);
            });
        }
    }

    function getLineColor(lineName) {
        const colors = {
            'Red Line': '#DC143C',
            'Yellow Line': '#FFD700',
            'Blue Line': '#4169E1',
            'Blue Line Branch': '#4169E1',
            'Green Line': '#228B22',
            'Violet Line': '#8B00FF',
            'Pink Line': '#FF69B4',
            'Magenta Line': '#FF00FF',
            'Grey Line': '#808080',
            'Airport Express': '#FF6347'
        };
        return colors[lineName] || '#333';
    }
});