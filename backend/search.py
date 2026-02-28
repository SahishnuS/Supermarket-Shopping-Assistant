"""
Smart Product Search Engine.
Uses Groq LLM (Llama 3.1 8B) for intelligent query understanding.
Falls back to rapidfuzz fuzzy matching when Groq is unavailable.
"""

import os
import json
import re
from rapidfuzz import fuzz
from spellchecker import SpellChecker
from backend.database import get_all_products

# ── Groq LLM Setup ──────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Try loading from .env file if not set
if not GROQ_API_KEY:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    GROQ_API_KEY = line.strip().split("=", 1)[1]

_groq_client = None

def _get_groq_client():
    """Lazy-init Groq client."""
    global _groq_client
    if _groq_client is None and GROQ_API_KEY:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=GROQ_API_KEY)
        except Exception:
            pass
    return _groq_client


# ── Spell Checker (fallback) ─────────────────────────────────────────
_spell = SpellChecker()
_product_vocab_loaded = False


def _load_product_vocab():
    """Add all product names, brands, categories to the spell checker dictionary."""
    global _product_vocab_loaded
    if _product_vocab_loaded:
        return
    products = get_all_products()
    custom_words = set()
    for p in products:
        for word in p["name"].lower().split():
            custom_words.add(word)
        if p.get("brand"):
            for word in p["brand"].lower().split():
                custom_words.add(word)
        if p.get("category"):
            for word in p["category"].lower().split():
                custom_words.add(word)
        if p.get("keywords"):
            for word in p["keywords"].lower().split(","):
                custom_words.add(word.strip())
    _spell.word_frequency.load_words(custom_words)
    _product_vocab_loaded = True


def correct_query(query):
    """Auto-correct misspelled words using product vocabulary.
    Only corrects words unknown in BOTH English and product vocab."""
    _load_product_vocab()
    english_only = SpellChecker()
    words = query.lower().split()
    corrected = []
    for word in words:
        if _spell.unknown([word]) and english_only.unknown([word]):
            correction = _spell.correction(word)
            corrected.append(correction if correction else word)
        else:
            corrected.append(word)
    return " ".join(corrected)


# ── Intent Map (fallback) ────────────────────────────────────────────
INTENT_MAP = {
    "cold": ["cold", "flu", "fever", "cough", "sardi", "khansi", "bukhar", "paracetamol"],
    "headache": ["headache", "pain relief", "paracetamol", "fever"],
    "fever": ["fever", "paracetamol", "bukhar", "cold"],
    "hungry": ["snack", "biscuit", "chips", "namkeen", "chocolate"],
    "thirsty": ["water", "juice", "cold drink", "soda", "paani"],
    "breakfast": ["milk", "bread", "butter", "tea", "biscuit", "chai"],
    "cooking": ["oil", "spice", "masala", "salt", "rice", "atta"],
    "cleaning": ["soap", "hand wash", "sanitizer", "dettol"],
    "hair": ["shampoo", "hair care", "hair wash", "conditioner"],
    "teeth": ["toothpaste", "dental", "dant manjan"],
    "skin": ["face wash", "cream", "soap", "skin care"],
    "baby": ["diaper", "baby food", "milk", "powder"],
    "sweet": ["chocolate", "biscuit", "ice cream", "candy", "mithai", "sugar"],
    "spicy": ["chili", "masala", "mirch", "garam masala"],
    "drink": ["cold drink", "juice", "soda", "water", "coke", "pepsi"],
    "fruit": ["banana", "apple", "mango", "fruit", "kela", "seb"],
    "vegetable": ["tomato", "onion", "peas", "sabji", "tamatar", "pyaaz"],
}


def expand_query(query):
    """Expand a vague query into relevant product keywords."""
    query_lower = query.lower()
    expanded_terms = [query_lower]
    for intent, keywords in INTENT_MAP.items():
        if intent in query_lower:
            expanded_terms.extend(keywords)
    return list(set(expanded_terms))


# ── LLM-Powered Search (Primary) ────────────────────────────────────

def search_with_llm(query, products, top_n=5):
    """
    Use Groq LLM to intelligently match products to user query.
    Returns list of matching products sorted by relevance.
    """
    client = _get_groq_client()
    if not client or not products:
        return None  # Signal to fall back to fuzzy

    # Build compact product list for the LLM
    product_lines = []
    for i, p in enumerate(products):
        line = f"{i+1}. {p['name']}"
        if p.get("category"):
            line += f" [{p['category']}]"
        if p.get("brand"):
            line += f" ({p['brand']})"
        if p.get("keywords"):
            line += f" — {p['keywords']}"
        product_lines.append(line)

    product_text = "\n".join(product_lines)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a supermarket product search engine. "
                        "Given a numbered product list and a customer's search query, "
                        "return ONLY a JSON array of the product numbers that genuinely match. "
                        "Be smart about matching:\n"
                        "- 'diary' is NOT 'dairy' — diary is a notebook, dairy is milk products\n"
                        "- 'tomato' should match tomato products, NOT potato\n"
                        "- Match by intent: 'breakfast' → bread, milk, butter, etc.\n"
                        "- Include relevant variants but exclude unrelated products\n"
                        "- Return at most 5 best matches, ordered by relevance\n"
                        "- Return ONLY the JSON array, nothing else. Example: [3, 7, 1]"
                    )
                },
                {
                    "role": "user",
                    "content": f"Products:\n{product_text}\n\nCustomer query: \"{query}\"\n\nMatching product numbers (JSON array):"
                }
            ],
            temperature=0,
            max_tokens=50,
        )

        raw = response.choices[0].message.content.strip()
        # Extract JSON array from response
        match = re.search(r'\[[\d\s,]*\]', raw)
        if match:
            indices = json.loads(match.group())
            results = []
            for idx in indices:
                if 1 <= idx <= len(products):
                    product = products[idx - 1].copy()
                    # Higher rank = higher relevance
                    product["match_score"] = round(100 - (len(results) * 5), 1)
                    results.append(product)
            return results[:top_n] if results else None

    except Exception as e:
        print(f"[Groq Search] Error: {e}")

    return None  # Fall back to fuzzy


# ── Fuzzy Search (Fallback) ──────────────────────────────────────────

def search_products_fuzzy(query, products, top_n=5, score_threshold=50):
    """Fuzzy matching fallback when LLM is unavailable."""
    corrected_query = correct_query(query)
    query_lower = corrected_query.strip()
    expanded_terms = expand_query(corrected_query)
    scored_products = []

    for product in products:
        name = product["name"].lower()
        brand = product.get("brand", "").lower()
        category = product.get("category", "").lower()
        keywords = product.get("keywords", "").lower()

        best_score = 0
        for term in expanded_terms:
            name_score = max(fuzz.WRatio(term, name), fuzz.partial_ratio(term, name))
            brand_score = fuzz.WRatio(term, brand)
            category_score = fuzz.WRatio(term, category)
            keyword_score = fuzz.token_set_ratio(term, keywords)

            weighted = (name_score * 0.50
                       + keyword_score * 0.25
                       + category_score * 0.15
                       + brand_score * 0.10)

            if term in name:
                weighted = max(weighted, 95)
            elif name.startswith(term) or name.endswith(term):
                weighted = max(weighted, 92)
            elif term in keywords:
                weighted = max(weighted, 75)

            best_score = max(best_score, weighted)

        if best_score >= score_threshold:
            scored_products.append({**product, "match_score": round(best_score, 1)})

    scored_products.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return scored_products[:top_n]


# ── Main Search Function ─────────────────────────────────────────────

def search_products(query, top_n=5, score_threshold=50):
    """
    Smart product search — tries Groq LLM first, falls back to fuzzy matching.

    Args:
        query: User's search query
        top_n: Maximum results to return
        score_threshold: Minimum score for fuzzy fallback

    Returns:
        List of matching products sorted by relevance
    """
    products = get_all_products()
    if not products:
        return []

    # Try LLM search first (fast with Groq)
    llm_results = search_with_llm(query, products, top_n)
    if llm_results:
        return llm_results

    # Fallback to fuzzy matching
    return search_products_fuzzy(query, products, top_n, score_threshold)


# ── LLM Context Formatters ───────────────────────────────────────────

def format_product_for_llm(product):
    """Format a product result into a text string suitable for the LLM context."""
    parts = [f"- **{product['name']}**"]
    if product.get("brand"):
        parts[0] += f" (Brand: {product['brand']})"
    if product.get("price"):
        parts.append(f"  Price: ₹{product['price']:.0f}")
    if product.get("quantity"):
        parts[-1] += f" / {product['quantity']}"
    if product.get("category"):
        parts.append(f"  Category: {product['category']}")
    if product.get("aisle_name"):
        parts.append(f"  Location: Aisle {product['aisle_name']}, Shelf {product.get('shelf', '?')}")
    if product.get("section"):
        parts.append(f"  Section: {product['section']}")
    if product.get("variants"):
        parts.append(f"  Available in: {', '.join(product['variants'])}")
    return "\n".join(parts)


def format_search_results_for_llm(products):
    """Format all search results into a text block for LLM context injection."""
    if not products:
        return "No matching products found in the store inventory."

    lines = ["Here are the matching products from the store inventory:\n"]
    for product in products:
        lines.append(format_product_for_llm(product))
        lines.append("")

    return "\n".join(lines)
