"""
Flask REST API — Bridge between the UI and the AI pipeline + Database.
All endpoints are JSON-based.
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import (
    get_all_products, add_product, update_product, delete_product,
    get_product_by_id, get_all_aisles, add_aisle, update_aisle, delete_aisle,
    get_all_config, set_config, get_product_count, get_aisle_count,
    get_category_list, seed_sample_data
)
from backend.ai_pipeline import chat, voice_chat
from backend.search import search_products

app = Flask(__name__)
CORS(app)

# Seed sample data on first run
seed_sample_data()


# ── Health Check ──────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "products": get_product_count(), "aisles": get_aisle_count()})


# ── Chat Endpoints ────────────────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """Process a text chat query."""
    data = request.get_json()
    query = data.get("query", "").strip()
    history = data.get("history", [])

    if not query:
        return jsonify({"error": "No query provided"}), 400

    result = chat(query, history)
    return jsonify(result)


@app.route("/voice", methods=["POST"])
def voice_endpoint():
    """Process a voice query. Expects audio file in form data."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    audio_bytes = audio_file.read()
    history = json.loads(request.form.get("history", "[]"))

    result = voice_chat(audio_bytes, history)
    return jsonify(result)


@app.route("/search", methods=["GET"])
def search_endpoint():
    """Quick product search without LLM response."""
    query = request.args.get("q", "").strip()
    top_n = int(request.args.get("n", 5))

    if not query:
        return jsonify({"error": "No query provided"}), 400

    results = search_products(query, top_n=top_n)
    return jsonify({"results": results, "query": query})


# ── Product CRUD ──────────────────────────────────────────────────────

@app.route("/products", methods=["GET"])
def list_products():
    products = get_all_products()
    return jsonify({"products": products, "count": len(products)})


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()
    required = ["name"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    product_id = add_product(
        name=data["name"],
        brand=data.get("brand", ""),
        category=data.get("category", ""),
        variants=data.get("variants", []),
        aisle_id=data.get("aisle_id"),
        shelf=data.get("shelf", 1),
        keywords=data.get("keywords", "")
    )
    return jsonify({"id": product_id, "message": "Product added successfully"}), 201


@app.route("/products/<int:product_id>", methods=["PUT"])
def edit_product(product_id):
    data = request.get_json()
    existing = get_product_by_id(product_id)
    if not existing:
        return jsonify({"error": "Product not found"}), 404

    update_product(
        product_id=product_id,
        name=data.get("name", existing["name"]),
        brand=data.get("brand", existing["brand"]),
        category=data.get("category", existing["category"]),
        variants=data.get("variants", existing["variants"]),
        aisle_id=data.get("aisle_id", existing["aisle_id"]),
        shelf=data.get("shelf", existing["shelf"]),
        keywords=data.get("keywords", existing["keywords"])
    )
    return jsonify({"message": "Product updated successfully"})


@app.route("/products/<int:product_id>", methods=["DELETE"])
def remove_product(product_id):
    existing = get_product_by_id(product_id)
    if not existing:
        return jsonify({"error": "Product not found"}), 404
    delete_product(product_id)
    return jsonify({"message": "Product deleted successfully"})


# ── Aisle CRUD ────────────────────────────────────────────────────────

@app.route("/aisles", methods=["GET"])
def list_aisles():
    aisles = get_all_aisles()
    return jsonify({"aisles": aisles, "count": len(aisles)})


@app.route("/aisles", methods=["POST"])
def create_aisle():
    data = request.get_json()
    required = ["name", "grid_x", "grid_y"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    aisle_id = add_aisle(
        name=data["name"],
        section=data.get("section", ""),
        grid_x=data["grid_x"],
        grid_y=data["grid_y"]
    )
    return jsonify({"id": aisle_id, "message": "Aisle added successfully"}), 201


@app.route("/aisles/<int:aisle_id>", methods=["PUT"])
def edit_aisle(aisle_id):
    data = request.get_json()
    update_aisle(
        aisle_id=aisle_id,
        name=data.get("name", ""),
        section=data.get("section", ""),
        grid_x=data.get("grid_x", 0),
        grid_y=data.get("grid_y", 0)
    )
    return jsonify({"message": "Aisle updated successfully"})


@app.route("/aisles/<int:aisle_id>", methods=["DELETE"])
def remove_aisle(aisle_id):
    delete_aisle(aisle_id)
    return jsonify({"message": "Aisle deleted successfully"})


# ── Store Config ──────────────────────────────────────────────────────

@app.route("/config", methods=["GET"])
def get_store_config():
    config = get_all_config()
    return jsonify(config)


@app.route("/config", methods=["POST"])
def update_store_config():
    data = request.get_json()
    for key, value in data.items():
        set_config(key, value)
    return jsonify({"message": "Configuration updated successfully"})


# ── Dashboard Stats ───────────────────────────────────────────────────

@app.route("/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "products": get_product_count(),
        "aisles": get_aisle_count(),
        "categories": get_category_list()
    })


# ── Run Server ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🛒 Supermarket AI Assistant — API Server")
    print("=" * 45)
    print(f"📦 Products: {get_product_count()}")
    print(f"🏪 Aisles:   {get_aisle_count()}")
    print("=" * 45)
    print("🚀 Starting server on http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
