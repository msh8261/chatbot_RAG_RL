document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const feedbackButtons = document.getElementById("feedback-buttons");

    let sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem("session_id", sessionId);
    }

    chatForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        addMessageToChat("You", message);
        userInput.value = "";

        try {
            const response = await fetch("/chat/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_input: message, session_id: sessionId })
            });

            const data = await response.json();
            addMessageToChat("Bot", data.response);

            if (data.response.includes("Note: This response may need improvement.")) {
                showFeedbackButtons();
            } else {
                feedbackButtons.style.display = "none";
            }
        } catch (error) {
            console.error("Error:", error);
            addMessageToChat("Bot", "An error occurred. Please try again.");
        }
    });

    function addMessageToChat(sender, message) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add(sender === "You" ? "user-message" : "bot-message");
        messageDiv.innerText = `${sender}: ${message}`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showFeedbackButtons() {
        feedbackButtons.style.display = "block";
        document.getElementById("positive-feedback").onclick = () => sendFeedback(1);
        document.getElementById("negative-feedback").onclick = () => sendFeedback(-1);
    }

    async function sendFeedback(reward) {
        feedbackButtons.style.display = "none";
        try {
            await fetch("/feedback/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId, reward: reward })
            });
            addMessageToChat("System", "Feedback received. Thank you!");
        } catch (error) {
            console.error("Feedback error:", error);
        }
    }

    function generateSessionId() {
        return "sess_" + Math.random().toString(36).substr(2, 9);
    }
});
