document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const clearBtn = document.getElementById("clearBtn");
    const themeToggle = document.getElementById("themeToggle");
    const chatBox = document.getElementById("chatBox");

    // Welcoming Default Message HTML
    const initialWelcomeHTML = `
        <div class="message bot-message">
            <div class="bot-avatar" title="WasitBot">👮‍♂️</div>
            <div class="message-content">
                Halo! Saya WasitBot. Ceritakan insiden atau pertanyaan seputar aturan permainan (Offside, Handball, VAR, dll.), dan saya akan jelaskan berdasarkan regulasi resmi IFAB.
            </div>
        </div>
    `;

    // 1. Initial Theme Settings (Cek LocalStorage)
    const savedTheme = localStorage.getItem("wasitbot_theme") || "dark";
    if (savedTheme === "light") {
        document.documentElement.setAttribute("data-theme", "light");
    }

    // Toggle Theme Handler
    themeToggle.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        if (currentTheme === "light") {
            document.documentElement.removeAttribute("data-theme");
            localStorage.setItem("wasitbot_theme", "dark");
        } else {
            document.documentElement.setAttribute("data-theme", "light");
            localStorage.setItem("wasitbot_theme", "light");
        }
    });

    // 2. Clear Chat Handler
    clearBtn.addEventListener("click", async () => {
        chatBox.innerHTML = initialWelcomeHTML;
        try {
            await fetch("/api/reset", { method: "POST" });
        } catch (e) {
            console.warn("Gagal mereset sesi server:", e);
        }
    });

    // 3. Send Message Handlers
    sendBtn.addEventListener("click", sendMessage);
    inputField.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = inputField.value.trim();
        if (!message) return;

        // Render User Message (Tanpa Avatar)
        chatBox.innerHTML += `
            <div class="message user-message">
                <div class="message-content">${escapeHtml(message)}</div>
            </div>`;
        
        inputField.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;

        // Render Loading State (Dengan Bot Avatar)
        const loadingId = "loading-" + Date.now();
        chatBox.innerHTML += `
            <div class="message bot-message" id="${loadingId}">
                <div class="bot-avatar" title="WasitBot">👮‍♂️</div>
                <div class="message-content loading-state">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
            </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            const loadingElem = document.getElementById(loadingId);
            if (loadingElem) loadingElem.remove();

            // Format baris baru & teks tebal sederhana
            let formattedResponse = escapeHtml(data.response || "")
                .replace(/\n/g, '<br>');

            // Badge persentase pemahaman bot
            let badgeHTML = "";
            let extraClass = "";
            if (data.confidence !== undefined && data.confidence !== null) {
                badgeHTML = `<span class="confidence-badge" title="Tingkat pemahaman bot terhadap pertanyaan">Akurasi ${data.confidence}%</span>`;
                extraClass = " has-badge";
            }

            // Render Bot Message
            chatBox.innerHTML += `
                <div class="message bot-message">
                    <div class="bot-avatar" title="WasitBot">👮‍♂️</div>
                    <div class="message-content${extraClass}">
                        ${badgeHTML}
                        ${formattedResponse}
                    </div>
                </div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

        } catch (error) {
            const loadingElem = document.getElementById(loadingId);
            if (loadingElem) loadingElem.remove();

            chatBox.innerHTML += `
                <div class="message bot-message error">
                    <div class="bot-avatar" title="WasitBot">👮‍♂️</div>
                    <div class="message-content">Gagal terhubung ke server. Pastikan server Flask berjalan.</div>
                </div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    // Helper untuk cegah XSS Injection
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.innerText = text;
        return div.innerHTML;
    }
});