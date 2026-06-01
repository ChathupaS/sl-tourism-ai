import { useState } from "react";
import ReactMarkdown from "react-markdown";

function ItineraryDisplay({ itinerary, meta, loading, error }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(itinerary);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
  
    }
  }

  if (loading) {
    return (
      <section className="itin-card itin-card--busy" aria-busy="true">
        <div className="busy-head">
          <div className="spinner" aria-hidden="true" />
          <div>
            <p className="busy-title">Crafting your itinerary…</p>
            <p className="busy-sub">
              Mapping routes, matching your interests and picking stays
            </p>
          </div>
        </div>
        <div className="skeleton" aria-hidden="true">
          {[90, 75, 96, 60, 88, 70, 94, 52].map((w, i) => (
            <span key={i} style={{ width: `${w}%` }} />
          ))}
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="itin-card itin-card--state">
        <div className="state-icon state-icon--error" aria-hidden="true">
          ⚠️
        </div>
        <h3>Something went wrong</h3>
        <p className="state-text">{error}</p>
        <p className="state-hint">
          Make sure the backend is running at localhost:8000, then try again.
        </p>
      </section>
    );
  }

  if (!itinerary) {
    return (
      <section className="itin-card itin-card--state">
        <div className="state-icon" aria-hidden="true">
          🧭
        </div>
        <h3>Your itinerary awaits</h3>
        <p className="state-text">
          Set your preferences and hit{" "}
          <strong>Generate itinerary</strong> — your custom Sri Lanka plan will
          appear right here.
        </p>
      </section>
    );
  }

  return (
    <section className="itin-card">
      <header className="itin-head">
        <div>
          <h2>Your Sri Lanka itinerary</h2>
          {meta && (
            <p className="itin-meta">
              <span>🗓️ {meta.days} {meta.days === 1 ? "day" : "days"}</span>
              <span>📍 from {meta.start_city}</span>
              <span className="cap">💼 {meta.budget}</span>
            </p>
          )}
        </div>
        <div className="itin-actions">
          <button type="button" className="ghost-btn" onClick={handleCopy}>
            {copied ? "✓ Copied" : "Copy"}
          </button>
          <button
            type="button"
            className="ghost-btn"
            onClick={() => window.print()}
          >
            Print
          </button>
        </div>
      </header>

      <div className="prose">
        <ReactMarkdown>{itinerary}</ReactMarkdown>
      </div>
    </section>
  );
}

export default ItineraryDisplay;
