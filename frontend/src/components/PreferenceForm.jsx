import { useState } from "react";

const INTERESTS = ["beach", "culture", "wildlife", "hiking", "history", "food"];
const CITIES = ["Colombo", "Kandy", "Galle", "Negombo"];
const BUDGETS = [
  { value: "budget", label: "Budget — hostels & street food" },
  { value: "mid-range", label: "Mid-range — guesthouses & local restaurants" },
  { value: "luxury", label: "Luxury — boutique hotels & fine dining" },
];

function PreferenceForm({ onGenerate, loading }) {
  const [days, setDays] = useState(5);
  const [interests, setInterests] = useState(["beach"]);
  const [budget, setBudget] = useState("mid-range");
  const [startCity, setStartCity] = useState("Colombo");

  function toggleInterest(interest) {
    setInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((i) => i !== interest)
        : [...prev, interest],
    );
  }

  function handleSubmit() {
    if (interests.length === 0) {
      alert("Please select at least one interest.");
      return;
    }
    onGenerate({ days, interests, budget, start_city: startCity });
  }

  return (
    <div className="form-card">
      <div className="form-group">
        <label>Number of days</label>
        <input
          type="number"
          min="1"
          max="14"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        />
      </div>

      <div className="form-group">
        <label>Interests</label>
        <div className="checkbox-group">
          {INTERESTS.map((interest) => (
            <label
              key={interest}
              className={`pill ${interests.includes(interest) ? "pill-active" : ""}`}
            >
              <input
                type="checkbox"
                checked={interests.includes(interest)}
                onChange={() => toggleInterest(interest)}
                style={{ display: "none" }}
              />
              {interest}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Budget</label>
        <select value={budget} onChange={(e) => setBudget(e.target.value)}>
          {BUDGETS.map((b) => (
            <option key={b.value} value={b.value}>
              {b.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Starting city</label>
        <select
          value={startCity}
          onChange={(e) => setStartCity(e.target.value)}
        >
          {CITIES.map((city) => (
            <option key={city} value={city}>
              {city}
            </option>
          ))}
        </select>
      </div>

      <button
        className="generate-btn"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Generating..." : "Generate Itinerary"}
      </button>
    </div>
  );
}

export default PreferenceForm;
