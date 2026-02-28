"""
BFS Pathfinding for Store Navigation.
Finds shortest path on the store grid and generates human-readable directions.
"""

from collections import deque
from backend.database import get_all_aisles, get_config


def build_store_grid():
    """Build a grid representation of the store from the database."""
    rows = int(get_config("grid_rows") or 6)
    cols = int(get_config("grid_cols") or 5)

    # Initialize grid: 0 = walkable, 1 = aisle (obstacle/destination)
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    aisle_positions = {}

    aisles = get_all_aisles()
    for aisle in aisles:
        x, y = aisle["grid_x"], aisle["grid_y"]
        if 0 <= x < rows and 0 <= y < cols:
            grid[x][y] = 1
            aisle_positions[aisle["name"]] = (x, y)

    return grid, rows, cols, aisle_positions


def bfs_path(grid, start, end, rows, cols):
    """
    BFS to find shortest path from start to end on the store grid.
    Can walk through aisle cells (they are destinations, not true walls).
    """
    if start == end:
        return [start]

    visited = set()
    visited.add(start)
    queue = deque([(start, [start])])

    # 4-directional movement
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        (x, y), path = queue.popleft()

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                visited.add((nx, ny))
                new_path = path + [(nx, ny)]

                if (nx, ny) == end:
                    return new_path

                queue.append(((nx, ny), new_path))

    return None  # No path found


def path_to_directions(path):
    """Convert a list of grid coordinates into human-readable step-by-step directions."""
    if not path or len(path) < 2:
        return "You're already there!"

    directions = []
    direction_names = {
        (0, 1): "right",
        (0, -1): "left",
        (1, 0): "forward",
        (-1, 0): "back"
    }

    i = 0
    while i < len(path) - 1:
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        direction = direction_names.get((dx, dy), "forward")

        # Count consecutive steps in the same direction
        steps = 1
        while (i + steps < len(path) - 1):
            next_dx = path[i + steps + 1][0] - path[i + steps][0]
            next_dy = path[i + steps + 1][1] - path[i + steps][1]
            if (next_dx, next_dy) == (dx, dy):
                steps += 1
            else:
                break

        if steps == 1:
            directions.append(f"Go {direction}")
        else:
            directions.append(f"Go {direction} for {steps} sections")

        i += steps

    return " → ".join(directions)


def get_directions_to_product(product):
    """
    Get walking directions from the store entrance to a product's aisle.

    Args:
        product: Product dict with aisle_name, grid_x, grid_y

    Returns:
        Dictionary with path info and human-readable directions
    """
    grid, rows, cols, aisle_positions = build_store_grid()

    entrance_x = int(get_config("entrance_x") or 0)
    entrance_y = int(get_config("entrance_y") or 0)
    start = (entrance_x, entrance_y)

    aisle_name = product.get("aisle_name", "")
    if aisle_name not in aisle_positions:
        return {
            "found": False,
            "directions": f"Sorry, I couldn't find the location for aisle {aisle_name}.",
            "path": [],
            "target": None,
            "entrance": start,
        }

    target = aisle_positions[aisle_name]
    path = bfs_path(grid, start, target, rows, cols)

    if path is None:
        return {
            "found": False,
            "directions": f"Sorry, I couldn't find a path to aisle {aisle_name}.",
            "path": [],
            "target": target,
            "entrance": start,
        }

    directions_text = path_to_directions(path)

    return {
        "found": True,
        "directions": f"Head to **Aisle {aisle_name}** ({product.get('section', '')}): {directions_text}",
        "path": path,
        "target": target,
        "entrance": start,
        "steps": len(path) - 1,
    }
