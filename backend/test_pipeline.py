from rag_pipeline import generate_itinerary

print("⏳ Generating itinerary — this takes 10-20 seconds...\n")

result = generate_itinerary(
    days=5,
    interests=["beach", "culture", "wildlife"],
    budget="mid-range",
    start_city="Colombo",
)

print("🌴 Generated Itinerary:")
print("=" * 60)
print(result)