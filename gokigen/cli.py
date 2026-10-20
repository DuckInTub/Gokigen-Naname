import argparse
from pathlib import Path
import sys
from typing import final
from .asp import parse_asp_solution, puzzle_to_asp
from .draw import draw_board
from .models import Puzzle
from .solver import solve

# pyright: reportUnusedCallResult = false


@final
class _Args(argparse.Namespace):
    """Strongly-typed namespace for argparse attributes."""

    subcommand: str = ""
    file: str = "-"
    asp_action: str | None = None
    size: int | None = None
    puzzle_file: str = ""
    solution_file: str = "-"
    draw_file: str | None = None


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gokigen",
        description="Gokigen Naname solver, ASP transformer, and visualizer toolkit.",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # 1. solve
    solve_parser = subparsers.add_parser(
        "solve", help="Solve a puzzle from file or stdin."
    )
    _ = solve_parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Path to constraints file (default: stdin).",
    )

    # 2. asp
    asp_parser = subparsers.add_parser(
        "asp", help="Answer Set Programming (ASP) utilities."
    )
    asp_sub = asp_parser.add_subparsers(dest="asp_action", required=True)

    asp_gen = asp_sub.add_parser("gen", help="Convert puzzle to ASP facts.")
    asp_gen.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Path to constraints file (default: stdin).",
    )

    asp_parse = asp_sub.add_parser(
        "parse", help="Convert ASP output to a solution grid."
    )
    asp_parse.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Path to clingo output file (default: stdin).",
    )
    asp_parse.add_argument(
        "-s",
        "--size",
        type=int,
        default=None,
        help="Explicit board dimension N (optional).",
    )

    # 3. draw
    draw_parser = subparsers.add_parser("draw", help="Plot the board and solution.")
    draw_parser.add_argument("puzzle_file", help="Path to puzzle constraints file.")
    draw_parser.add_argument(
        "solution_file",
        nargs="?",
        default="-",
        help="Path to solution file (default: stdin).",
    )
    draw_parser.add_argument(
        "-o",
        "--draw_file",
        type=str,
        default=None,
        help="Output a .png-file instead of showing the drawing.")

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args(namespace=_Args())

    try:
        if args.subcommand == "solve":
            puzzle = Puzzle.load(args.file)
            solution = solve(puzzle)
            for i in range(puzzle.size):
                print("".join(solution[i*puzzle.size:(i+1)*puzzle.size]))

        elif args.subcommand == "asp":
            if args.asp_action == "gen":
                puzzle = Puzzle.load(args.file)
                print(puzzle_to_asp(puzzle))
            elif args.asp_action == "parse":
                raw_text = (
                    Path(args.file).read_text(encoding="utf-8")
                    if args.file != "-"
                    else sys.stdin.read()
                )
                board = parse_asp_solution(raw_text, size=args.size)
                for row in board:
                    print(row)

        elif args.subcommand == "draw":
            puzzle = Puzzle.load(args.puzzle_file)
            sol_text = (
                Path(args.solution_file).read_text(encoding="utf-8")
                if args.solution_file != "-"
                else sys.stdin.read()
            )
            solution_rows = [
                line.strip() for line in sol_text.strip().splitlines() if line.strip()
            ]
            draw_board(puzzle, solution_rows, out_file=args.draw_file)

    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
