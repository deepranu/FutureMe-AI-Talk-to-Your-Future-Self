const API_URL = "http://127.0.0.1:5000";

async function sendMessage() {
    const inputBox = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");

    const input = inputBox.value.trim();
    if (!input) return;

    chatBox.innerHTML += `<div class="user-msg">You: ${input}</div>`;
    inputBox.value = "";

    const loadingId = Date.now();
    chatBox.innerHTML += `<div id="${loadingId}" class="ai-msg">Thinking...</div>`;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: input })
        });

        const data = await response.json();

        document.getElementById(loadingId).innerHTML =
            `Future You:<br>${data.response}<br><small>⏱ ${data.response_time}s</small>`;

    } catch (error) {
        document.getElementById(loadingId).innerHTML =
            "⚠️ Error getting response";
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

// Enter key support
document.getElementById("userInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMessage();
});

async function resetChat() {
    await fetch(`${API_URL}/reset`, { method: "POST" });
    document.getElementById("chatBox").innerHTML = "";
}
