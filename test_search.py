"""Seed database and test search."""
import sys
sys.path.insert(0, ".")

from backend.database import seed_sample_data, get_product_count, get_aisle_count
seed_sample_data()
print(f"Products: {get_product_count()}, Aisles: {get_aisle_count()}")

from backend.search import search_products

queries = ["wheat flour", "milk", "shampoo", "something for cold", "cooking oil", "chocolate", "chips", "rice"]
for q in queries:
    results = search_products(q)
    print(f"\n--- '{q}' ---")
    for p in results:
        brand = p.get('brand', '') or 'No Brand'
        print(f"  {p['name']} ({brand}) Rs.{p.get('price',0):.0f}/{p.get('quantity','')} - Score:{p['match_score']}")
    if not results:
        print("  (no results)")
