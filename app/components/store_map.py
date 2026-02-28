"""
Store Map Component — Renders the store grid with aisles and product highlights.
Uses matplotlib to generate a visual store layout.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import io


# Color scheme
COLORS = {
    "walkway": "#1a1a2e",        # Dark background
    "aisle": "#16213e",           # Dark blue for aisles
    "entrance": "#00d2ff",        # Cyan for entrance
    "target": "#00ff88",          # Green for target aisle
    "path": "#ffd700",            # Gold for path
    "grid_line": "#2a2a4a",       # Subtle grid lines
    "text": "#ffffff",            # White text
    "text_dim": "#888888",        # Dimmed text
}

SECTION_COLORS = {
    "Grocery & Staples": "#e74c3c",
    "Dairy & Frozen": "#3498db",
    "Snacks & Beverages": "#f39c12",
    "Personal Care": "#9b59b6",
    "Medicine & Health": "#2ecc71",
    "Fruits & Vegetables": "#1abc9c",
}


def render_store_map(aisles, target_aisle=None, path=None, entrance=(0, 0),
                     grid_rows=6, grid_cols=5, figsize=(10, 8)):
    """
    Render the store map as a matplotlib figure.

    Args:
        aisles: List of aisle dicts from the database
        target_aisle: Name of the aisle to highlight (e.g., "A2")
        path: List of (x, y) tuples from BFS pathfinding
        entrance: (x, y) tuple for store entrance
        grid_rows: Number of rows in the grid
        grid_cols: Number of columns in the grid
        figsize: Figure size tuple

    Returns:
        matplotlib figure object
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    fig.patch.set_facecolor(COLORS["walkway"])
    ax.set_facecolor(COLORS["walkway"])

    # Draw grid
    for i in range(grid_rows + 1):
        ax.axhline(y=i, color=COLORS["grid_line"], linewidth=0.5, alpha=0.5)
    for j in range(grid_cols + 1):
        ax.axvline(x=j, color=COLORS["grid_line"], linewidth=0.5, alpha=0.5)

    # Draw path (if provided)
    if path and len(path) > 1:
        for px, py in path:
            rect = mpatches.FancyBboxPatch(
                (py, grid_rows - 1 - px), 1, 1,
                boxstyle="round,pad=0.05",
                facecolor=COLORS["path"], alpha=0.3,
                edgecolor=COLORS["path"], linewidth=1
            )
            ax.add_patch(rect)

        # Draw path line
        path_y = [py + 0.5 for px, py in path]
        path_x = [grid_rows - 1 - px + 0.5 for px, py in path]
        ax.plot(path_y, path_x, color=COLORS["path"], linewidth=3, alpha=0.7,
                linestyle="--", marker="", zorder=5)

    # Draw aisles
    aisle_map = {}
    for aisle in aisles:
        x, y = aisle["grid_x"], aisle["grid_y"]
        name = aisle["name"]
        section = aisle.get("section", "")
        aisle_map[name] = (x, y)

        # Determine color
        if name == target_aisle:
            color = COLORS["target"]
            alpha = 0.9
            edge_width = 3
        else:
            color = SECTION_COLORS.get(section, COLORS["aisle"])
            alpha = 0.6
            edge_width = 1

        # Draw aisle block
        rect = mpatches.FancyBboxPatch(
            (y, grid_rows - 1 - x), 1, 1,
            boxstyle="round,pad=0.08",
            facecolor=color, alpha=alpha,
            edgecolor="#ffffff" if name == target_aisle else color,
            linewidth=edge_width
        )
        ax.add_patch(rect)

        # Aisle label
        ax.text(y + 0.5, grid_rows - 1 - x + 0.6, name,
                ha="center", va="center", fontsize=14, fontweight="bold",
                color=COLORS["text"], zorder=10)

        # Section label (smaller)
        if section:
            short_section = section.split("&")[0].strip()[:12]
            ax.text(y + 0.5, grid_rows - 1 - x + 0.3, short_section,
                    ha="center", va="center", fontsize=7,
                    color=COLORS["text_dim"], zorder=10)

    # Draw entrance marker
    ex, ey = entrance
    ax.text(ey + 0.5, grid_rows - 1 - ex + 0.5, "🚪\nENTER",
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=COLORS["entrance"], zorder=10)

    # Draw target marker
    if target_aisle and target_aisle in aisle_map:
        tx, ty = aisle_map[target_aisle]
        ax.text(ty + 0.5, grid_rows - 1 - tx + 0.05, "📍 HERE",
                ha="center", va="center", fontsize=8, fontweight="bold",
                color=COLORS["target"], zorder=11)

    # Configure axes
    ax.set_xlim(0, grid_cols)
    ax.set_ylim(0, grid_rows)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Title
    title = "🛒 Store Map"
    if target_aisle:
        title += f"  —  Go to Aisle {target_aisle}"
    ax.set_title(title, fontsize=16, fontweight="bold",
                 color=COLORS["text"], pad=15)

    # Legend
    legend_elements = []
    for section_name, color in SECTION_COLORS.items():
        legend_elements.append(
            mpatches.Patch(facecolor=color, alpha=0.6, label=section_name)
        )
    if target_aisle:
        legend_elements.append(
            mpatches.Patch(facecolor=COLORS["target"], alpha=0.9, label="Target Aisle")
        )
    if path:
        legend_elements.append(
            mpatches.Patch(facecolor=COLORS["path"], alpha=0.4, label="Walking Path")
        )

    ax.legend(handles=legend_elements, loc="upper right", fontsize=7,
              facecolor=COLORS["walkway"], edgecolor=COLORS["grid_line"],
              labelcolor=COLORS["text"])

    plt.tight_layout()
    return fig


def render_store_map_simple(aisles, target_aisle=None, grid_rows=6, grid_cols=5):
    """Simplified map without pathfinding — for the admin panel."""
    return render_store_map(aisles, target_aisle=target_aisle,
                           grid_rows=grid_rows, grid_cols=grid_cols,
                           figsize=(8, 6))
