from .models import Puzzle

def draw_board(puzzle: Puzzle, solution: list[str], title: str = "Gokigen Naname", out_file = None) -> None:
    try:
        import matplotlib.patches as patches
        import matplotlib.pyplot as plt
    except ImportError as err:
        raise ImportError(
            "Visualizer requires 'matplotlib'. Install it with: pip install matplotlib"
        ) from err

    n = puzzle.size
    if len(solution) != n:
        raise ValueError(f"Expected {n} solution rows, got {len(solution)}.")
    if any(len(row) < n for row in solution):
        raise ValueError(f"All solution rows must have length at least {n}.")

    _, ax = plt.subplots(figsize=(8, 8))

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, pad=15)

    # 1. Draw Grid
    for i in range(n + 1):
        lw = 2 if i in (0, n) else 1.0
        ax.plot((0, n), (i, i), color="black", linewidth=lw, zorder=2)
        ax.plot((i, i), (0, n), color="black", linewidth=lw, zorder=2)

    # 2. Draw Slants
    for r in range(n):
        for c in range(n):
            char = solution[r][c]
            top_y = n - r
            bot_y = n - r - 1
            left_x = c
            right_x = c + 1

            if char == "/":
                slant, = ax.plot((left_x, right_x), (bot_y, top_y), color="blue", linewidth=2, solid_capstyle="butt", zorder=1)
            else:
                slant, = ax.plot((left_x, right_x), (top_y, bot_y), color="blue", linewidth=2, solid_capstyle="butt", zorder=1)

            clipped = patches.Rectangle((left_x, bot_y), 1, 1, transform=ax.transData)
            slant.set_clip_path(clipped)

    # 3. Draw Constraints
    for (r, c), val in puzzle.constraints.items():
        y = n - r
        x = c
        circle = patches.Circle(
            (x, y), radius=0.20, edgecolor="black", facecolor="white", linewidth=1, zorder=3
        )
        ax.add_patch(circle)
        ax.text(x, y, str(val), ha="center", va="center", fontsize=12, zorder=4)

    plt.tight_layout()
    if out_file:
        plt.savefig(out_file, dpi=300)
    else:
        plt.show()