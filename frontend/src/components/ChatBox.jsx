
import { useState } from "react";
import { sendMessageToBackend } from "../services/ChatService";
import "./ChatBox.css";

function ChatBox() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    const userMessage = message.trim();

    if (!userMessage || loading) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", text: userMessage },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await sendMessageToBackend(userMessage);

      console.log("Backend Response:", response);

      // Extract the result object from backend response
      const result = response.result || {};

      // Handle both NOTE and QUERY responses
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          title: result.title || "",
          text: result.summary || "I couldn't generate a response.",
        },
      ]);

    } catch (error) {
      console.error("Chat Error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          title: "",
          text: error.message || "Something went wrong.",
        },
      ]);

    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    if (loading) return;

    setMessages([]);
    setMessage("");
  };

  return (
    <div className="app-container">

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span>Note Assistant</span>
        </div>

        <button
          className="new-chat-button"
          onClick={handleNewChat}
          disabled={loading}
        >
          <span>＋</span> New chat
        </button>

        <div className="sidebar-section">
          <p className="sidebar-label">YOUR WORKSPACE</p>

          <div className="sidebar-item active">
            <span>▤</span> Meeting Notes
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="profile-avatar">K</div>

          <div>
            <strong>My Workspace</strong>
            <small>Note Assistant</small>
          </div>
        </div>
      </aside>

      {/* Main Chat */}
      <main className="main-content">

        {/* Header */}
        <header className="top-header">
          <div className="mobile-brand">
            <strong>Note Assistant</strong>
          </div>
        </header>

        {/* Chat Area */}
        <section className="chat-area">

          {messages.length === 0 ? (
            <div className="welcome-screen">
              <h1>What can I help you remember?</h1>

              <p>
                Add your meeting notes and ask questions about them anytime.
              </p>
            </div>
          ) : (
            <div className="messages-list">

              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`chat-message ${msg.role}`}
                >

                  {/* Assistant Icon */}
                  {msg.role === "assistant" && (
                    <div className="assistant-avatar">✦</div>
                  )}

                  {/* Message Content */}
                  <div className="message-content">

                    {msg.role === "assistant" ? (
                      <div className="simple-note-card">
                        {msg.title && <h3>{msg.title}</h3>}
                        <p>{msg.text}</p>
                      </div>
                    ) : (
                      <div className="message-text">
                        {msg.text}
                      </div>
                    )}

                  </div>
                </div>
              ))}

              {/* Loading Indicator */}
              {loading && (
                <div className="chat-message assistant">
                  <div className="assistant-avatar">✦</div>

                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}

            </div>
          )}

        </section>

        {/* Message Composer */}
        <footer className="composer-section">
          <div className="composer">

            <button
              className="composer-tool"
              type="button"
              title="Upload document"
            >
              ＋
            </button>

            <input
              type="text"
              placeholder="Ask anything about your meeting notes..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSend();
              }}
              disabled={loading}
            />

            <button
              className="composer-tool voice-button"
              type="button"
              title="Voice recording"
            >
              🎙
            </button>

            <button
              className="send-button"
              type="button"
              onClick={handleSend}
              disabled={!message.trim() || loading}
              title="Send message"
            >
              ↑
            </button>

          </div>

          <p className="composer-caption">
            Note Assistant can make mistakes. Verify important information.
          </p>
        </footer>

      </main>
    </div>
  );
}

export default ChatBox;
