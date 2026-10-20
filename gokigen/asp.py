import re
from .models import Puzzle


def puzzle_to_asp(puzzle: Puzzle) -> str:
    """Generates Clingo / ASP facts for a board."""
    lines: list[str] = [
        "% Dimensions:",
        f"rows({puzzle.size}).",
        f"cols({puzzle.size}).",
        "",
        "% Constraints:",
    ]
    for (r, c), val in sorted(puzzle.constraints.items()):
        lines.append(f"constraint({r}, {c}, {val}).")
    return "\n".join(lines)


def parse_asp_solution(asp_output: str, size: int | None = None) -> list[str]:
    """
    Parses Clingo/ASP solution output.
    Matches predicates like: `slant(slash, 0, 1)` or `slant(backslash, 1, 2)`.
    """
    pattern = re.compile(
        r"\b(?:slant)\((slash|backslash),(\d+),(\d+)\)",
        re.IGNORECASE,
    )
    compact = re.sub(r"\s+", "", asp_output)  # Remove all whitespace.
    matches: list[str] = pattern.findall(compact)
    if not matches:
        raise ValueError("No slants found in ASP output.")

    cells: dict[tuple[int, int], str] = {}
    max_r, max_c = 0, 0
    for slant_str, r_str, c_str in matches:
        r, c = int(r_str), int(c_str)
        cells[(r, c)] = "/" if slant_str.lower() == "slash" else "\\"
        max_r = max(max_r, r)
        max_c = max(max_c, c)

    grid_size = size if size is not None else max(max_r, max_c) + 1
    board: list[str] = []
    for r in range(grid_size):
        row = "".join(cells.get((r, c), "?") for c in range(grid_size))
        board.append(row)

    return board
