import { useState } from "react";
import PreferenceForm from "./components/PreferenceForm";
import ItineraryDisplay from "./components/ItineraryDisplay";
import "./App.css";

function App() {
  const [itinerary, setItinerary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate(preferences) {
    setLoading(true);
    setError("");
    setItinerary("");

    try {
      const response = await fetch("http://localhost:8000/generate-itinerary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(preferences),
      });

      if (!response.ok) {
        throw new Error("Server error. Please try again.");
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
    <div className="app">
      <header className="app-header">
        <h1>Sri Lanka AI Travel Planner</h1>
        <p>Tell us your preferences and we'll build your perfect itinerary</p>
      </header>

      <main className="app-main">
        <PreferenceForm onGenerate={handleGenerate} loading={loading} />
        <ItineraryDisplay
          itinerary={itinerary}
          loading={loading}
          error={error}
        />
      </main>
    </div>
  );
}

export default App;
