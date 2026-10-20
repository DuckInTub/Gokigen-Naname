from typing import TypedDict
from .dsu import DisjointSets
from .models import Puzzle


class CellEdges(TypedDict):
    slash: tuple[int, int]
    backslash: tuple[int, int]
    finished: list[int]


def solve(puzzle: Puzzle) -> list[str]:
    size = puzzle.size
    nr_cells = size * size
    ints = size + 1
    constraints = puzzle.to_flat_constraints()

    # DSU
    dsu: DisjointSets = DisjointSets((ints) ** 2)
    union = dsu.union
    same = dsu.same
    rollback = dsu.rollback

    deg: list[int] = [0] * ((ints) ** 2)
    cell_to_nodes: list[dict[str, list[int] | tuple[int, int]]] = []

    for i in range(nr_cells):
        r, c = divmod(i, size)

        top_left = r * (ints) + c
        top_right = r * (ints) + c + 1
        bottom_left = (r + 1) * (ints) + c
        bottom_right = (r + 1) * (ints) + c + 1

        on_bottom_row = r == size - 1
        on_last_col = c == size - 1
        finished_nodes: list[int] = []
        if top_left in constraints:
            finished_nodes.append(top_left)
        if on_last_col and top_right in constraints:
            finished_nodes.append(top_right)
        if on_bottom_row and bottom_left in constraints:
            finished_nodes.append(bottom_left)
        if on_bottom_row and on_last_col and bottom_right in constraints:
            finished_nodes.append(bottom_right)

        cell_to_nodes.append(
            {
                "/": (bottom_left, top_right),
                "\\": (top_left, bottom_right),
                "finished": finished_nodes,
            }
        )

    def backtracker(idx: int, assignment: list[str]):
        # Check constraints of all finished nodes.
        if idx > 0:
            for prev in cell_to_nodes[idx - 1]["finished"]:
                if deg[prev] != constraints[prev]:
                    return False

        # If all cells are filled and all nodes meet their constraints,
        # we have found a solutoin.
        if idx == nr_cells:
            return True

        data = cell_to_nodes[idx]
        for choice in "/\\":
            u, v = data[choice]

            def full(n: int):
                return n in constraints and deg[n] + 1 > constraints[n]

            # Able to increase degree?
            if full(u) or full(v):
                continue

            # Don't create a loop?
            if same(u, v):
                continue

            # Apply the slant.
            union(u, v)
            deg[u] += 1
            deg[v] += 1
            assignment.append(choice)

            # Check if the board can be solved.
            if backtracker(idx + 1, assignment):
                return True

            # If not, revert the slant.
            _ = assignment.pop()
            deg[u] -= 1
            deg[v] -= 1
            rollback()

        return False

    final_assignment: list[str] = []
    if backtracker(0, final_assignment):
        return final_assignment

    raise ValueError("No solution.")
