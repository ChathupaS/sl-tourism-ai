import { useState } from "react";
import PreferenceForm from "./components/PreferenceForm";
import ItineraryDisplay from "./components/ItineraryDisplay";
import "./App.css";

function App() {
  const [itinerary, setItinerary] = useState("");
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate(preferences) {
    setLoading(true);
    setError("");
    setItinerary("");
    setMeta(preferences);

    try {
      const response = await fetch("http://localhost:8000/generate-itinerary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(preferences),
      });

      if (!response.ok) {
        let detail = "Server error. Please try again.";
        try {
          const body = await response.json();
          if (body?.detail) detail = body.detail;
        } catch {
        }
        throw new Error(detail);
      }

      const data = await response.json();
      setItinerary(data.itinerary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <nav className="nav">
        <a className="brand" href="/" aria-label="Ceylon Compass home">
          <span className="brand__mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.7" />
              <path d="M15.8 8.2 13.4 13.4 8.2 15.8l2.4-5.2z" fill="currentColor" />
            </svg>
          </span>
          <span className="brand__text">
            Ceylon<span>Compass</span>
          </span>
        </a>
        <span className="nav__tag">AI Travel Planner</span>
      </nav>

      <header className="hero">
        <div className="hero__glow" aria-hidden="true" />
        <div className="hero__inner">
          <span className="badge">✦ Powered by AI</span>
          <h1 className="hero__title">
            Plan your perfect <span>Sri&nbsp;Lanka</span> adventure
          </h1>
          <p className="hero__subtitle">
            Tell us how you like to travel and we'll craft a personalized,
            day-by-day itinerary across the island — beaches, ancient cities,
            wildlife and all.
          </p>
          <ul className="hero__chips">
            <li>🗺️ Day-by-day plan</li>
            <li>🎯 Tailored to you</li>
            <li>⚡ Ready in seconds</li>
          </ul>
        </div>
      </header>

      <main className="planner">
        <PreferenceForm onGenerate={handleGenerate} loading={loading} />
        <ItineraryDisplay
          itinerary={itinerary}
          meta={meta}
          loading={loading}
          error={error}
        />
      </main>

      <footer className="footer">
        <p>
          Crafted for explorers of Sri Lanka · Itineraries are AI-generated —
          double-check key details before you travel.
        </p>
      </footer>
    </div>
  );
}

export default App;
