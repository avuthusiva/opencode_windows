"""
export_to_js.py - run the Python sudoku logic and save the result for the page

Why this file exists:
    A page in a browser can only run JavaScript, it cannot call Python.
    So this small script does the Python work once, writes everything into
    a plain file called puzzles.js, and sudoku.html reads that file and
    shows it on the page.

Run it again any time you want fresh puzzles:
    python export_to_js.py

What it writes into puzzles.js:
    window.PYTHON_PUZZLES = [ {name, source, clues, puzzle, solution,
                               answers, solve_ms}, ... ]
"""

import json
import os
import time

import sudoku

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, "puzzles.js")


def describe(grid):
    """Small dictionary of facts about one puzzle, written into the js file."""
    clues = sum(1 for row in grid for value in row if value != sudoku.EMPTY)
    return {"clues": clues, "puzzle": sudoku.grid_to_text(grid)}


def solve_item(text, name, source):
    """
    Take 81 characters, solve them with sudoku.py, and return one record
    for the page. Nothing here is new logic, it only calls sudoku.py.
    """
    grid = sudoku.parse_grid(text)
    item = {"name": name, "source": source, "answers": 0,
            "solution": None, "solve_ms": None}
    item.update(describe(grid))

    if not sudoku.is_valid_grid(grid):
        item["note"] = "breaks a Sudoku rule, so it cannot be played"
        return item

    start = time.perf_counter()
    answer = sudoku.solve_copy(grid)
    item["solve_ms"] = round((time.perf_counter() - start) * 1000, 2)
    item["answers"] = sudoku.count_solutions(sudoku.copy_grid(grid), limit=3)

    if answer is not None:
        item["solution"] = sudoku.grid_to_text(answer)
    return item


def generated_item(clues, name):
    """Ask the Python generator for a fresh puzzle with the given clues."""
    start = time.perf_counter()
    puzzle, solution = sudoku.generate_puzzle(clues=clues)
    item = {"name": name, "source": "made by sudoku.py just now",
            "answers": 1, "solve_ms": None, "solution": None}
    item.update(describe(puzzle))
    item["solution"] = sudoku.grid_to_text(solution)
    item["answers"] = sudoku.count_solutions(sudoku.copy_grid(puzzle), limit=2)
    item["generate_ms"] = round((time.perf_counter() - start) * 1000, 2)
    return item


def main():
    items = []

    # 1. the puzzles from puzzles.txt, solved by Python
    path = os.path.join(HERE, "puzzles.txt")
    if os.path.exists(path):
        for line_number, text, grid in sudoku.read_puzzles(path):
            item = solve_item(text, "Puzzle from the text file",
                              "puzzles.txt line %d" % line_number)
            if item["answers"] == 1:
                items.append(item)
            elif item["answers"] == 0:
                print("Skipped line %d, it breaks a Sudoku rule."
                      % line_number)
            else:
                print("Skipped line %d, it has %d answers (stopping at 3)."
                      % (line_number, item["answers"]))

    # 2. a few fresh puzzles from the Python generator
    for clues in (34, 30, 26):
        item = generated_item(clues, "Puzzle made by Python")
        items.append(item)
        print("Generated a puzzle with %d clues in %s ms."
              % (item["clues"], item["generate_ms"]))

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "// puzzles.js",
        "// Written by export_to_js.py on %s." % now,
        "// sudoku.html reads this file, so open the page after running:",
        "//     python export_to_js.py",
        "// Every entry below came out of the Python code in sudoku.py.",
        "",
        "window.PYTHON_PUZZLES = " + json.dumps(items, indent=2) + ";",
        "",
    ]

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    print("Wrote %d puzzles to %s" % (len(items), OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
