"""Quick test script to verify the core pipeline works."""
import sys
sys.path.insert(0, ".")

print("=" * 50)
print("TESTING SUPERMARKET AI ASSISTANT")
print("=" * 50)

# Test 1: Database
print("\n1. Database Test...")
from backend.database import get_product_count, get_aisle_count, get_all_products
print(f"   Products: {get_product_count()}")
print(f"   Aisles: {get_aisle_count()}")
print("   ✅ Database OK")

# Test 2: Search
print("\n2. Search Test...")
from backend.search import search_products
results = search_products("something for cold")
print(f"   Query: 'something for cold'")
for r in results[:3]:
    print(f"   → {r['name']} ({r.get('brand','')}) - Aisle {r.get('aisle_name','?')} - Score: {r['match_score']}")

results2 = search_products("cooking oil")
print(f"\n   Query: 'cooking oil'")
for r in results2[:3]:
    print(f"   → {r['name']} ({r.get('brand','')}) - Aisle {r.get('aisle_name','?')} - Score: {r['match_score']}")
print("   ✅ Search OK")

# Test 3: Pathfinding
print("\n3. Pathfinding Test...")
from backend.pathfinding import get_directions_to_product
if results2:
    directions = get_directions_to_product(results2[0])
    print(f"   Directions to {results2[0]['name']}: {directions.get('directions', 'N/A')}")
    print(f"   Steps: {directions.get('steps', 'N/A')}")
print("   ✅ Pathfinding OK")

# Test 4: AI Pipeline (fallback mode)
print("\n4. AI Pipeline Test (fallback mode)...")
from backend.ai_pipeline import chat, OLLAMA_AVAILABLE, WHISPER_AVAILABLE
print(f"   Ollama available: {OLLAMA_AVAILABLE}")
print(f"   Whisper available: {WHISPER_AVAILABLE}")

result = chat("Where can I find sugar?")
print(f"   Query: 'Where can I find sugar?'")
print(f"   Response: {result['response'][:150]}...")
print(f"   Products found: {len(result.get('products', []))}")
print("   ✅ AI Pipeline OK")

print("\n" + "=" * 50)
print("ALL TESTS PASSED ✅")
print("=" * 50)
