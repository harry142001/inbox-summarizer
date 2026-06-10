import { useState, useEffect } from "react";
import axios from "axios";
import EmailCard from "./components/EmailCard";
import "./App.css";

const API = "http://localhost:8000";

function App() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const res = await axios.get(`${API}/auth/status`);
      setAuthenticated(res.data.authenticated);
    } catch (err) {
      setAuthenticated(false);
    }
  };

  const handleLogin = async () => {
    try {
      window.location.href = `${API}/auth/login`;
    } catch (err) {
      setError("Login failed. Make sure your backend is running.");
    }
  };

  const fetchEmails = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API}/emails/summarize`);
      setEmails(res.data.emails);
    } catch (err) {
      setError("Failed to fetch emails. Try logging in again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>📬 Inbox Summarizer</h1>
        <p>Your AI-powered email digest</p>
      </header>

      <main className="main">
        {!authenticated ? (
          <div className="auth-box">
            <h2>Connect your Gmail</h2>
            <p>Sign in to let AI summarize your inbox</p>
            <button className="btn-primary" onClick={handleLogin}>
              Login with Google
            </button>
          </div>
        ) : (
          <div>
            <div className="controls">
              <button
                className="btn-primary"
                onClick={fetchEmails}
                disabled={loading}
              >
                {loading ? "Summarizing..." : "Summarize My Inbox"}
              </button>
            </div>

            {error && <p className="error">{error}</p>}

            <div className="email-list">
              {emails.map((email) => (
                <EmailCard key={email.id} email={email} />
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
