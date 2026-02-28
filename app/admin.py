"""
Admin Panel — Streamlit app for store owners to manage inventory and store layout.
Run: streamlit run app/admin.py
"""

import streamlit as st
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import (
    get_all_products, add_product, update_product, delete_product,
    get_all_aisles, add_aisle, update_aisle, delete_aisle,
    get_all_config, set_config, get_product_count, get_aisle_count,
    get_category_list, seed_sample_data, init_db
)
from app.components.store_map import render_store_map_simple

# Initialize DB
init_db()

# ── Page Config ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="Store Admin Panel",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .admin-header {
        text-align: center;
        padding: 20px 0;
       background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #2a2a4a;
    }

    .admin-header h1 {
        font-size: 28px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stat-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    .stat-card h2 {
        font-size: 36px;
        color: #667eea;
        margin: 0;
    }

    .stat-card p {
        color: #888;
        margin: 4px 0 0 0;
        font-size: 14px;
    }

    .success-msg {
        background: #00ff8820;
        border: 1px solid #00ff8840;
        color: #00ff88;
        padding: 10px 16px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


# ── Login Page ────────────────────────────────────────────────────────

def login_page():
    st.markdown("""
    <div class="admin-header">
        <h1>🏪 Store Admin Panel</h1>
        <p style="color: #888;">Enter your admin password to manage your store</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            password = st.text_input("Admin Password", type="password", placeholder="Enter password...")
            submitted = st.form_submit_button("🔓 Login", use_container_width=True)

            if submitted:
                stored_password = get_all_config().get("admin_password", "admin123")
                if password == stored_password:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Default is: admin123")


# ── Sidebar ───────────────────────────────────────────────────────────

def admin_sidebar():
    with st.sidebar:
        st.markdown("### 🏪 Admin Panel")
        st.divider()

        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        if st.button("📦 Manage Products", use_container_width=True):
            st.session_state.page = "products"
            st.rerun()
        if st.button("🗺️ Manage Aisles", use_container_width=True):
            st.session_state.page = "aisles"
            st.rerun()
        if st.button("🗄️ Store Layout", use_container_width=True):
            st.session_state.page = "layout"
            st.rerun()
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()
        if st.button("📥 Import / Export", use_container_width=True):
            st.session_state.page = "import_export"
            st.rerun()

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()


# ── Dashboard Page ────────────────────────────────────────────────────

def dashboard_page():
    st.markdown("""
    <div class="admin-header">
        <h1>📊 Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{get_product_count()}</h2>
            <p>📦 Total Products</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{get_aisle_count()}</h2>
            <p>🏪 Total Aisles</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        categories = get_category_list()
        st.markdown(f"""
        <div class="stat-card">
            <h2>{len(categories)}</h2>
            <p>🏷️ Categories</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Recent products
    st.subheader("📦 Product Overview")
    products = get_all_products()
    if products:
        for cat in get_category_list():
            cat_products = [p for p in products if p["category"] == cat]
            if cat_products:
                with st.expander(f"**{cat}** ({len(cat_products)} items)"):
                    for p in cat_products:
                        aisle = p.get("aisle_name", "?")
                        st.write(f"• **{p['name']}** ({p.get('brand', '—')}) — Aisle {aisle}, Shelf {p.get('shelf', '?')}")
    else:
        st.info("No products yet. Go to **Manage Products** to add some, or use **Import** to load sample data.")


# ── Product Management Page ───────────────────────────────────────────

def products_page():
    st.markdown("""
    <div class="admin-header">
        <h1>📦 Manage Products</h1>
    </div>
    """, unsafe_allow_html=True)

    aisles = get_all_aisles()
    aisle_names = {a["id"]: f"{a['name']} ({a.get('section', '')})" for a in aisles}
    aisle_ids = {f"{a['name']} ({a.get('section', '')})": a["id"] for a in aisles}

    tab1, tab2 = st.tabs(["➕ Add Product", "📋 All Products"])

    with tab1:
        with st.form("add_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name *", placeholder="e.g., Sugar")
                brand = st.text_input("Brand", placeholder="e.g., Tata")
                category = st.text_input("Category", placeholder="e.g., Grocery")
            with col2:
                aisle_options = list(aisle_ids.keys())
                selected_aisle = st.selectbox("Aisle", options=["(None)"] + aisle_options)
                shelf = st.number_input("Shelf Number", min_value=1, max_value=10, value=1)
                keywords = st.text_input("Keywords (comma-separated)", placeholder="e.g., sweet,white sugar,cheeni")

            variants = st.text_input("Variants (comma-separated)", placeholder="e.g., 1kg, 5kg")

            submitted = st.form_submit_button("✅ Add Product", use_container_width=True)
            if submitted and name:
                aisle_id = aisle_ids.get(selected_aisle) if selected_aisle != "(None)" else None
                variant_list = [v.strip() for v in variants.split(",") if v.strip()] if variants else []
                add_product(name, brand, category, variant_list, aisle_id, shelf, keywords)
                st.success(f"✅ Added **{name}** successfully!")
                st.rerun()

    with tab2:
        products = get_all_products()
        if not products:
            st.info("No products yet.")
            return

        # Search filter
        search = st.text_input("🔍 Filter products...", placeholder="Type to filter...")
        if search:
            products = [p for p in products if search.lower() in p["name"].lower()
                       or search.lower() in p.get("category", "").lower()
                       or search.lower() in p.get("brand", "").lower()]

        for p in products:
            with st.expander(f"**{p['name']}** — {p.get('brand', '—')} | Aisle {p.get('aisle_name', '?')}"):
                col1, col2, col3 = st.columns([3, 3, 1])
                with col1:
                    st.write(f"**Category:** {p.get('category', '—')}")
                    st.write(f"**Brand:** {p.get('brand', '—')}")
                    st.write(f"**Variants:** {', '.join(p.get('variants', [])) or '—'}")
                with col2:
                    st.write(f"**Aisle:** {p.get('aisle_name', '—')}")
                    st.write(f"**Shelf:** {p.get('shelf', '—')}")
                    st.write(f"**Keywords:** {p.get('keywords', '—')}")
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{p['id']}"):
                        delete_product(p["id"])
                        st.rerun()


# ── Aisle Management Page ─────────────────────────────────────────────

def aisles_page():
    st.markdown("""
    <div class="admin-header">
        <h1>🗺️ Manage Aisles</h1>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ Add Aisle", "📋 All Aisles"])

    with tab1:
        with st.form("add_aisle_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Aisle Name *", placeholder="e.g., A1")
                section = st.text_input("Section", placeholder="e.g., Grocery & Staples")
            with col2:
                grid_x = st.number_input("Grid Row (X)", min_value=0, max_value=20, value=0)
                grid_y = st.number_input("Grid Column (Y)", min_value=0, max_value=20, value=0)

            submitted = st.form_submit_button("✅ Add Aisle", use_container_width=True)
            if submitted and name:
                add_aisle(name, section, grid_x, grid_y)
                st.success(f"✅ Added aisle **{name}** successfully!")
                st.rerun()

    with tab2:
        aisles = get_all_aisles()
        if not aisles:
            st.info("No aisles yet.")
            return

        for a in aisles:
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.write(f"**{a['name']}** — {a.get('section', '—')}")
            with col2:
                st.write(f"Grid: ({a['grid_x']}, {a['grid_y']})")
            with col3:
                if st.button("🗑️", key=f"del_aisle_{a['id']}"):
                    delete_aisle(a["id"])
                    st.rerun()


# ── Store Layout Page ─────────────────────────────────────────────────

def layout_page():
    st.markdown("""
    <div class="admin-header">
        <h1>🗄️ Store Layout</h1>
    </div>
    """, unsafe_allow_html=True)

    config = get_all_config()
    aisles = get_all_aisles()

    if aisles:
        grid_rows = int(config.get("grid_rows", 6))
        grid_cols = int(config.get("grid_cols", 5))
        fig = render_store_map_simple(aisles, grid_rows=grid_rows, grid_cols=grid_cols)
        st.pyplot(fig)
    else:
        st.info("No aisles configured. Add aisles first to see the store map.")


# ── Settings Page ─────────────────────────────────────────────────────

def settings_page():
    st.markdown("""
    <div class="admin-header">
        <h1>⚙️ Settings</h1>
    </div>
    """, unsafe_allow_html=True)

    config = get_all_config()

    with st.form("settings_form"):
        store_name = st.text_input("Store Name", value=config.get("store_name", "My Supermarket"))
        col1, col2 = st.columns(2)
        with col1:
            grid_rows = st.number_input("Grid Rows", min_value=2, max_value=20,
                                        value=int(config.get("grid_rows", 6)))
            entrance_x = st.number_input("Entrance Row (X)", min_value=0, max_value=20,
                                         value=int(config.get("entrance_x", 0)))
        with col2:
            grid_cols = st.number_input("Grid Columns", min_value=2, max_value=20,
                                        value=int(config.get("grid_cols", 5)))
            entrance_y = st.number_input("Entrance Column (Y)", min_value=0, max_value=20,
                                         value=int(config.get("entrance_y", 0)))

        new_password = st.text_input("Change Admin Password", type="password",
                                     placeholder="Leave empty to keep current")

        submitted = st.form_submit_button("💾 Save Settings", use_container_width=True)
        if submitted:
            set_config("store_name", store_name)
            set_config("grid_rows", grid_rows)
            set_config("grid_cols", grid_cols)
            set_config("entrance_x", entrance_x)
            set_config("entrance_y", entrance_y)
            if new_password:
                set_config("admin_password", new_password)
            st.success("✅ Settings saved!")


# ── Import/Export Page ────────────────────────────────────────────────

def import_export_page():
    st.markdown("""
    <div class="admin-header">
        <h1>📥 Import / Export</h1>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📥 Import", "📤 Export"])

    with tab1:
        st.write("Upload a JSON file to bulk-import products and aisles.")
        uploaded = st.file_uploader("Choose JSON file", type=["json"])
        if uploaded:
            try:
                data = json.loads(uploaded.read().decode("utf-8"))
                st.json(data)
                if st.button("✅ Import This Data", use_container_width=True):
                    # Import aisles
                    aisle_map = {}
                    for aisle in data.get("aisles", []):
                        try:
                            aid = add_aisle(
                                aisle["name"], aisle.get("section", ""),
                                aisle["grid_x"], aisle["grid_y"]
                            )
                            aisle_map[aisle["name"]] = aid
                        except Exception:
                            existing_aisles = get_all_aisles()
                            for ea in existing_aisles:
                                if ea["name"] == aisle["name"]:
                                    aisle_map[aisle["name"]] = ea["id"]
                                    break

                    # Import products
                    count = 0
                    for product in data.get("products", []):
                        aisle_id = aisle_map.get(product.get("aisle"), None)
                        add_product(
                            name=product["name"],
                            brand=product.get("brand", ""),
                            category=product.get("category", ""),
                            variants=product.get("variants", []),
                            aisle_id=aisle_id,
                            shelf=product.get("shelf", 1),
                            keywords=product.get("keywords", "")
                        )
                        count += 1
                    st.success(f"✅ Imported {count} products!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading JSON: {e}")

        st.divider()
        st.write("Or load the built-in sample data:")
        if st.button("📦 Load Sample Data", use_container_width=True):
            seed_sample_data()
            st.success("✅ Sample data loaded!")
            st.rerun()

    with tab2:
        st.write("Export your current store data as JSON.")
        if st.button("📤 Generate Export", use_container_width=True):
            products = get_all_products()
            aisles = get_all_aisles()
            export_data = {
                "aisles": [{"name": a["name"], "section": a.get("section", ""),
                           "grid_x": a["grid_x"], "grid_y": a["grid_y"]} for a in aisles],
                "products": [{"name": p["name"], "brand": p.get("brand", ""),
                             "category": p.get("category", ""),
                             "aisle": p.get("aisle_name", ""),
                             "shelf": p.get("shelf", 1),
                             "keywords": p.get("keywords", ""),
                             "variants": p.get("variants", [])} for p in products]
            }
            json_str = json.dumps(export_data, indent=2)
            st.download_button("⬇️ Download JSON", json_str,
                              file_name="store_data.json", mime="application/json",
                              use_container_width=True)


# ── Main Router ───────────────────────────────────────────────────────

def main():
    if not st.session_state.admin_logged_in:
        login_page()
        return

    admin_sidebar()

    page = st.session_state.page
    if page == "dashboard":
        dashboard_page()
    elif page == "products":
        products_page()
    elif page == "aisles":
        aisles_page()
    elif page == "layout":
        layout_page()
    elif page == "settings":
        settings_page()
    elif page == "import_export":
        import_export_page()


if __name__ == "__main__":
    main()
