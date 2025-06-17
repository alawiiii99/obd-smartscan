import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const ChatBox = () => {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! Ask me anything about your car. 🚗" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);

  // Replace this with dynamic user_id from login/session if needed
  const userId = "11111111-1111-1111-1111-111111111111"; // Example user ID, replace with actual user ID logic

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: input,
        user_id: userId
      });
      const aiMessage = { role: "assistant", text: res.data.response };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "⚠️ Sorry, something went wrong while talking to the AI."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [messages]);

  return (
    <div style={{ padding: "1rem", fontFamily: "sans-serif" }}>
      <div
        ref={chatRef}
        style={{
          maxHeight: "500px",
          overflowY: "auto",
          padding: "1rem",
          border: "1px solid #ccc",
          borderRadius: "8px",
          backgroundColor: "#f5f5f5",
          marginBottom: "1rem"
        }}
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              textAlign: msg.role === "user" ? "right" : "left",
              margin: "0.5rem 0"
            }}
          >
            <div
              style={{
                display: "inline-block",
                padding: "0.5rem 1rem",
                borderRadius: "16px",
                backgroundColor: msg.role === "user" ? "#007bff" : "#e0e0e0",
                color: msg.role === "user" ? "#fff" : "#000",
                maxWidth: "80%",
                whiteSpace: "normal"
              }}
              dangerouslySetInnerHTML={{
                __html: msg.text.replace(/\n/g, "<br/>")
              }}
            />
          </div>
        ))}
        {loading && (
          <div
            style={{
              marginTop: "0.5rem",
              fontStyle: "italic",
              color: "#999"
            }}
          >
            Assistant is typing...
          </div>
        )}
      </div>

      <textarea
        rows={2}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message and press Enter..."
        style={{
          width: "100%",
          padding: "0.75rem",
          fontSize: "1rem",
          borderRadius: "6px",
          border: "1px solid #ccc",
          resize: "none"
        }}
      />
      <button
        onClick={handleSend}
        style={{
          marginTop: "0.5rem",
          padding: "0.5rem 1.2rem",
          backgroundColor: "#18181b",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          float: "right"
        }}
      >
        Send
      </button>
    </div>
  );
};

export default ChatBox;
