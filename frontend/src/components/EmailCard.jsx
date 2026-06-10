import { useState } from "react";
import "./EmailCard.css";

const CATEGORY_COLORS = {
  Work: "#4f46e5",
  Finance: "#059669",
  Personal: "#0891b2",
  Newsletter: "#7c3aed",
  Spam: "#9ca3af",
  Uncategorized: "#6b7280",
};

const PRIORITY_COLORS = {
  high: "#ef4444",
  medium: "#f59e0b",
  low: "#22c55e",
};

function getPriorityLevel(score) {
  if (score >= 7) return "high";
  if (score >= 4) return "medium";
  return "low";
}

function EmailCard({ email }) {
  const [expanded, setExpanded] = useState(false);
  const priorityLevel = getPriorityLevel(email.priority);

  return (
    <div className="card">
      <div className="card-header" onClick={() => setExpanded(!expanded)}>
        <div className="card-left">
          <div className="card-badges">
            <span
              className="badge-category"
              style={{
                background: CATEGORY_COLORS[email.category] || "#6b7280",
              }}
            >
              {email.category}
            </span>
            <span
              className="badge-priority"
              style={{ background: PRIORITY_COLORS[priorityLevel] }}
            >
              P{email.priority}
            </span>
            {email.from_cache && <span className="badge-cache">cached</span>}
          </div>
          <h3 className="card-subject">{email.subject}</h3>
          <p className="card-sender">{email.sender}</p>
        </div>
        <span className="card-arrow">{expanded ? "▲" : "▼"}</span>
      </div>

      {expanded && (
        <div className="card-body">
          <div className="card-section">
            <p className="card-summary">{email.summary}</p>
          </div>

          {email.action_items && email.action_items.length > 0 && (
            <div className="card-section">
              <h4>Action Items</h4>
              <ul className="action-list">
                {email.action_items.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {email.priority_reason && (
            <div className="card-section">
              <h4>Priority Reason</h4>
              <p className="priority-reason">{email.priority_reason}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default EmailCard;
