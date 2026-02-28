"""
Chat UI Components — Dark theme with neon yellow accents.
Inspired by Tharun Speaks: dark bg, bold italic display fonts, neon highlights.
"""

import streamlit as st


def apply_chat_styles():
    """Apply dark theme with neon yellow accents."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700;1,900&family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

        /* ── Global Dark ─── */
        .stApp {
            background: #0c0c14 !important;
            font-family: 'Space Grotesk', 'Inter', sans-serif !important;
            color: #e8e8e8 !important;
        }

        .main .block-container,
        [data-testid="stAppViewBlockContainer"],
        [data-testid="stVerticalBlock"],
        .block-container {
            max-width: 100% !important;
            width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 0 !important;
        }
        .main { padding: 0 !important; }
        .stApp > header + div { padding-top: 0 !important; }
        section[data-testid="stSidebar"] + div .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .stMainBlockContainer {
            max-width: 100% !important;
            padding: 0 1rem !important;
        }

        /* Hide Streamlit chrome */
        [data-testid="collapsedControl"], header, footer,
        [data-testid="stSidebar"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Kill input wrapper defaults */
        .stTextInput > div,
        .stTextInput div[data-baseweb="base-input"],
        .stTextInput div[data-baseweb="input"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        .stForm { border: none !important; padding: 0 !important; }

        /* Hide 'Press Enter to submit form' and fix alignment */
        .stForm [data-testid="stFormSubmitButton"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        .stForm .stElementContainer {
            margin-bottom: 0 !important;
        }
        .stForm [kind="formSubmit"] {
            height: 48px !important;
        }
        div[data-testid="InputInstructions"] {
            display: none !important;
        }
        /* Align search row */
        .stForm [data-testid="stHorizontalBlock"] {
            align-items: center !important;
            gap: 8px !important;
        }

        /* ── Chat Bubbles ─── */
        [data-testid="stChatMessage"] {
            background: #161622 !important;
            border: 1px solid rgba(184, 157, 0, 0.12) !important;
            border-radius: 14px !important;
            padding: 16px 20px !important;
            margin: 10px 0 !important;
            box-shadow: none !important;
        }

        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] span,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] div,
        [data-testid="stChatMessage"] strong,
        [data-testid="stChatMessage"] b {
            color: #e0e0e0 !important;
            font-size: 15px !important;
            line-height: 1.7 !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }

        [data-testid="stChatMessage"] strong,
        [data-testid="stChatMessage"] b {
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        /* ── Product Card ─── */
        .product-card {
            background: #1a1a2e;
            border: 1px solid rgba(184, 157, 0, 0.15);
            border-radius: 14px;
            padding: 20px 24px;
            margin: 12px 0;
            transition: border-color 0.2s ease;
        }
        .product-card:hover {
            border-color: rgba(184, 157, 0, 0.35);
        }
        .product-card h4 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 17px;
            font-weight: 600;
            color: #ffffff;
            margin: 0 0 10px 0;
        }
        .product-card .price-tag {
            color: #b89d00;
            font-weight: 700;
            font-size: 17px;
        }
        .product-card .detail {
            font-size: 14px;
            color: #9ca3af;
            margin: 5px 0;
            font-family: 'Space Grotesk', sans-serif;
        }
        .product-card .detail b {
            color: #d1d5db;
        }
        .product-card .location-chip {
            margin-top: 14px;
            background: #b89d00;
            color: #0c0c14;
            font-weight: 600;
            font-size: 13px;
            padding: 6px 16px;
            border-radius: 100px;
            display: inline-block;
            font-family: 'Space Grotesk', sans-serif;
        }

        /* ── Direction Badge ─── */
        .direction-badge {
            background: rgba(184, 157, 0, 0.12);
            color: #b89d00;
            padding: 10px 18px;
            border-radius: 100px;
            font-size: 13px;
            font-weight: 500;
            margin: 8px 0;
            display: inline-block;
            border: 1px solid rgba(184, 157, 0, 0.2);
            font-family: 'Space Grotesk', sans-serif;
        }

        /* ── Search Bar ─── */
        .stTextInput input {
            border: 1px solid #2a2a3d !important;
            border-radius: 100px !important;
            padding: 14px 24px !important;
            font-size: 15px !important;
            background: #161622 !important;
            color: #e8e8e8 !important;
            box-shadow: none !important;
            font-family: 'Space Grotesk', sans-serif !important;
            transition: border-color 0.2s !important;
        }
        .stTextInput input:hover {
            border-color: #3a3a50 !important;
        }
        .stTextInput input:focus {
            border-color: #b89d00 !important;
            box-shadow: 0 0 0 3px rgba(184, 157, 0, 0.12) !important;
        }
        .stTextInput input::placeholder {
            color: #5a5a70 !important;
        }

        /* ── Buttons ─── */
        .stButton button, .stFormSubmitButton button {
            background: #b89d00 !important;
            color: #0c0c14 !important;
            border: none !important;
            border-radius: 100px !important;
            padding: 10px 28px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            transition: all 0.2s !important;
        }
        .stButton button:hover, .stFormSubmitButton button:hover {
            background: #c9a800 !important;
            box-shadow: 0 0 20px rgba(184, 157, 0, 0.25) !important;
        }

        /* ── Status Pills ─── */
        .status-pill {
            padding: 4px 12px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 500;
            margin: 2px 4px;
            display: inline-block;
            font-family: 'Space Grotesk', sans-serif;
        }
        .status-online { background: rgba(184, 157, 0, 0.12); color: #b89d00; }
        .status-warn { background: rgba(184, 157, 0, 0.08); color: #9a8400; }
        .status-offline { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

        /* Expander — Store Map */
        .streamlit-expanderHeader,
        [data-testid="stExpander"] summary {
            background: #161622 !important;
            border-radius: 12px !important;
            border: 1px solid #2a2a3d !important;
            color: #e8e8e8 !important;
            padding: 12px 16px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            gap: 8px !important;
        }
        .streamlit-expanderContent,
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            background: #0e0e1a !important;
            border: 1px solid #2a2a3d !important;
            border-top: none !important;
            border-radius: 0 0 12px 12px !important;
            padding: 12px !important;
        }
        [data-testid="stExpander"] {
            border: none !important;
            background: transparent !important;
        }
        [data-testid="stExpander"] summary span {
            color: #e8e8e8 !important;
        }
        [data-testid="stExpander"] svg {
            color: #b89d00 !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0c0c14; }
        ::-webkit-scrollbar-thumb { background: #2a2a3d; border-radius: 3px; }

        /* ── Header ─── */
        .ag-header {
            text-align: center;
            padding: 15px 0 10px 0;
        }
        /* Hide Streamlit auto-generated anchor link icon on headers */
        .ag-header h1 a,
        [data-testid="stHeaderActionElements"],
        .ag-header h1 .header-anchor,
        a.header-link { display: none !important; }
        h1 a[href] { display: none !important; }
        .ag-header .tagline {
            font-family: 'Playfair Display', serif;
            font-style: italic;
            font-weight: 400;
            font-size: 20px;
            color: #9ca3af;
            margin-bottom: 4px;
        }
        .ag-header h1 {
            font-family: 'Playfair Display', serif;
            font-weight: 900;
            font-style: italic;
            font-size: 52px;
            color: #b89d00;
            letter-spacing: -1px;
            line-height: 1.1;
            margin: 0 0 16px 0;
            text-shadow: 0 0 40px rgba(184, 157, 0, 0.2);
        }
        .ag-header p {
            color: #6b7280;
            font-size: 15px;
            font-weight: 400;
            font-family: 'Space Grotesk', sans-serif;
            margin: 0;
        }
    </style>
    """, unsafe_allow_html=True)


def render_product_card(product):
    """Render a product card — dark theme with neon accents."""
    variants = ", ".join(product.get("variants", [])) if product.get("variants") else "—"
    brand = product.get("brand", "") or "—"
    location = f"Aisle {product.get('aisle_name', '?')}, Shelf {product.get('shelf', '?')}"
    section = product.get("section", "")
    price = product.get("price", 0)
    quantity = product.get("quantity", "")

    price_html = f'<span class="price-tag">₹{price:.0f}</span>' if price else ""
    qty_html = f' <span style="color:#6b7280;font-size:13px;">/ {quantity}</span>' if quantity else ""

    st.markdown(f"""
    <div class="product-card">
        <h4>🛍️ {product['name']} {price_html}{qty_html}</h4>
        <div class="detail"><b>Brand:</b> &nbsp; {brand}</div>
        <div class="detail"><b>Category:</b> &nbsp; {product.get('category', '—')}</div>
        <div class="detail"><b>Available in:</b> &nbsp; {variants}</div>
        <div class="location-chip">📍 {location} ({section})</div>
    </div>
    """, unsafe_allow_html=True)


def render_directions(directions_info):
    """Render walking directions badge."""
    if directions_info and directions_info.get("found"):
        import re
        text = directions_info["directions"]
        # Convert markdown **bold** to HTML <b>bold</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        st.markdown(
            f'<div class="direction-badge">🚶 {text}</div>',
            unsafe_allow_html=True
        )


def render_header(store_name="My Supermarket"):
    """Render the app header — bold italic display style."""
    st.markdown(f"""
    <div class="ag-header">
        <div class="tagline">your personal</div>
        <h1>Shopping Assistant</h1>
        <p>Search anything — I'll find it and guide you to the right aisle.</p>
    </div>
    """, unsafe_allow_html=True)
