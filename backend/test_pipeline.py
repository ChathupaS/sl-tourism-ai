from rag_pipeline import generate_itinerary

print("⏳ Generating itinerary — this takes 10-20 seconds...\n")

try:
    result = generate_itinerary(
        days=5,
        interests=["beach", "culture", "wildlife"],
        budget="mid-range",
        start_city="Colombo",
    )
except RuntimeError as exc:
    # Missing vector store or API key — show the guidance, not a stack trace.
    raise SystemExit(f"❌ {exc}")

print("🌴 Generated Itinerary:")
print("=" * 60)
print(result)
