import ReactMarkdown from "react-markdown";

function ItineraryDisplay({ itinerary, loading, error }) {
  if (loading) {
    return (
      <div className="itinerary-card center">
        <div className="spinner"></div>
        <p>Building your Sri Lanka itinerary...</p>
        <p className="sub">This usually takes 10–20 seconds</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="itinerary-card center">
        <p style={{ color: "#dc2626" }}>Something went wrong: {error}</p>
      </div>
    );
  }

  if (!itinerary) {
    return (
      <div className="itinerary-card center">
        <p style={{ color: "#9ca3af" }}>Your itinerary will appear here</p>
      </div>
    );
  }

  return (
    <div className="itinerary-card">
      <h2>Your Itinerary</h2>
      <ReactMarkdown>{itinerary}</ReactMarkdown>
    </div>
  );
}

export default ItineraryDisplay;
