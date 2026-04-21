const API_URL = "http://127.0.0.1:5000";

async function sendMessage() {
    const inputBox = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");

    const input = inputBox.value;

    if (!input) return;

    chatBox.innerHTML += `<p><b>You:</b> ${input}</p>`;

    inputBox.value = "";

    const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: input })
    });

    const data = await response.json();

    chatBox.innerHTML += `
        <p><b>Future You:</b> ${data.response}</p>
        <small>⏱ ${data.response_time}s</small>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;
}

async function resetChat() {
    await fetch(`${API_URL}/reset`, { method: "POST" });
    document.getElementById("chatBox").innerHTML = "";
}
