from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import TextIO


@dataclass(frozen=True)
class Puzzle:
    """
    Represents a Gokigen Naname puzzle.

    Attributes:
        size (int): The number of rows and columns cells (containing slants) the solution requires.
        constraints (dict[tuple[int, int], int]): Map of (row, col) intersection coordinates to the value of the degree constraint (0-4).
        raw_lines (list[str]): The raw string lines of the text representation of the puzzle.
    """

    size: int
    constraints: dict[tuple[int, int], int]
    raw_lines: list[str]

    @property
    def num_intersections(self) -> int:
        return self.size + 1

    def to_flat_constraints(self) -> dict[int, int]:
        """Flattens 2D vertex coordinates to 1D indices for graph/DSU solvers."""
        stride = self.size + 1
        return {r * stride + c: val for (r, c), val in self.constraints.items()}

    @classmethod
    def from_text(cls, text: str) -> Puzzle:
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        if not lines:
            raise ValueError("Input puzzle text is empty.")

        try:
            size = int(lines[0])
        except ValueError as err:
            raise ValueError(
                f"First line must be an integer size, got: {lines[0]!r}"
            ) from err

        constraint_lines = lines[1:]
        if len(constraint_lines) != size + 1:
            raise ValueError(
                f"Expected {size + 1} constraint rows for size {size}, got {len(constraint_lines)}."
            )

        constraints: dict[tuple[int, int], int] = {}
        for r, line in enumerate(constraint_lines):
            if len(line) < size + 1:
                raise ValueError(
                    f"Row {r} must have at least {size + 1} columns, got {len(line)}."
                )
            for c, char in enumerate(line[: size + 1]):
                if char != ".":
                    if not char.isdigit() or not (0 <= int(char) <= 4):
                        raise ValueError(f"Invalid constraint '{char}' at ({r}, {c}).")
                    constraints[(r, c)] = int(char)

        return cls(size=size, constraints=constraints, raw_lines=constraint_lines)

    @classmethod
    def load(cls, source: str | Path | TextIO | None = None) -> Puzzle:
        if source is None or source == "-":
            return cls.from_text(sys.stdin.read())
        if isinstance(source, (str, Path)):
            return cls.from_text(Path(source).read_text(encoding="utf-8"))
        return cls.from_text(source.read())
