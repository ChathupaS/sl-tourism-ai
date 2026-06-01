import { useState } from "react";

const INTERESTS = [
  { id: "beach", label: "Beach", emoji: "🏖️" },
  { id: "culture", label: "Culture", emoji: "🛕" },
  { id: "wildlife", label: "Wildlife", emoji: "🐘" },
  { id: "hiking", label: "Hiking", emoji: "🥾" },
  { id: "history", label: "History", emoji: "🏛️" },
  { id: "food", label: "Food", emoji: "🍛" },
];

const CITIES = ["Colombo", "Kandy", "Galle", "Negombo"];

const BUDGETS = [
  {
    value: "budget",
    label: "Budget",
    desc: "Hostels & street food",
    icon: "💸",
  },
  {
    value: "mid-range",
    label: "Mid-range",
    desc: "Guesthouses & local eats",
    icon: "🏡",
  },
  {
    value: "luxury",
    label: "Luxury",
    desc: "Boutique hotels & fine dining",
    icon: "✨",
  },
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

  function handleSubmit(e) {
    e.preventDefault();
    if (interests.length === 0) return;
    onGenerate({ days, interests, budget, start_city: startCity });
  }

  return (
    <form className="form-card" onSubmit={handleSubmit}>
      <header className="form-card__head">
        <h2>Your trip</h2>
        <p>Set your preferences below</p>
      </header>

      <div className="field">
        <div className="field__label-row">
          <label htmlFor="days">Trip length</label>
          <span className="days-value">
            {days} <small>{days === 1 ? "day" : "days"}</small>
          </span>
        </div>
        <input
          id="days"
          className="slider"
          type="range"
          min="1"
          max="14"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          style={{ "--pct": `${((days - 1) / 13) * 100}%` }}
        />
        <div className="slider__scale">
          <span>1</span>
          <span>14 days</span>
        </div>
      </div>

      <div className="field">
        <span className="field__label">Interests</span>
        <div className="pill-group" role="group" aria-label="Interests">
          {INTERESTS.map(({ id, label, emoji }) => {
            const active = interests.includes(id);
            return (
              <button
                type="button"
                key={id}
                className={`pill ${active ? "pill--active" : ""}`}
                aria-pressed={active}
                onClick={() => toggleInterest(id)}
              >
                <span aria-hidden="true">{emoji}</span>
                {label}
              </button>
            );
          })}
        </div>
        {interests.length === 0 && (
          <p className="field__hint field__hint--warn">
            Pick at least one interest.
          </p>
        )}
      </div>

      <div className="field">
        <span className="field__label">Budget</span>
        <div className="budget-group" role="radiogroup" aria-label="Budget">
          {BUDGETS.map(({ value, label, desc, icon }) => {
            const active = budget === value;
            return (
              <button
                type="button"
                key={value}
                className={`budget ${active ? "budget--active" : ""}`}
                role="radio"
                aria-checked={active}
                onClick={() => setBudget(value)}
              >
                <span className="budget__icon" aria-hidden="true">
                  {icon}
                </span>
                <span className="budget__text">
                  <strong>{label}</strong>
                  <small>{desc}</small>
                </span>
                <span className="budget__check" aria-hidden="true" />
              </button>
            );
          })}
        </div>
      </div>

      <div className="field">
        <span className="field__label">Starting city</span>
        <div
          className="city-group"
          role="radiogroup"
          aria-label="Starting city"
        >
          {CITIES.map((city) => {
            const active = startCity === city;
            return (
              <button
                type="button"
                key={city}
                className={`city ${active ? "city--active" : ""}`}
                role="radio"
                aria-checked={active}
                onClick={() => setStartCity(city)}
              >
                <span aria-hidden="true">📍</span>
                {city}
              </button>
            );
          })}
        </div>
      </div>

      <button
        className="generate-btn"
        type="submit"
        disabled={loading || interests.length === 0}
      >
        {loading ? (
          <>
            <span className="btn-spinner" aria-hidden="true" />
            Generating…
          </>
        ) : (
          <>Generate itinerary →</>
        )}
      </button>
    </form>
  );
}

export default PreferenceForm;
