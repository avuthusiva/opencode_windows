"""
test_sudoku.py - small self-check for sudoku.py

Run it with:
    python test_sudoku.py

It prints PASS for every check and stops at the first failure.
No test framework is needed, just plain asserts and if statements.
"""

import time

import sudoku


def check(name, condition):
    """Print one result line, and stop everything if it failed."""
    if condition:
        print("PASS -", name)
    else:
        print("FAIL -", name)
        raise SystemExit(1)


def main():
    # ---- 1. reading text ------------------------------------------------
    grid = sudoku.parse_grid(
        "530070000600195000098000060800060003400803001700020006"
        "060000280000419005000080079")
    check("81 characters become 9 rows", len(grid) == 9)
    check("every row has 9 cells", all(len(row) == 9 for row in grid))
    check("first row is read correctly", grid[0] == [5, 3, 0, 0, 7, 0, 0, 0, 0])
    check("dots are read as empty",
          sudoku.parse_grid("." * 81)[0][0] == sudoku.EMPTY)

    try:
        sudoku.parse_grid("123")
        check("too few cells is an error", False)
    except ValueError:
        check("too few cells is an error", True)

    # ---- 2. the rules ---------------------------------------------------
    small = sudoku.parse_grid(
        "530070000600195000098000060800060003400803001700020006"
        "060000280000419005000080079")
    check("a normal puzzle passes the rule check",
          sudoku.is_valid_grid(small))
    check("an empty cell in row 0 gets no new options from its row",
          5 not in sudoku.candidates(small, 0, 2))
    check("digit 4 is allowed in cell row 0 col 2",
          4 in sudoku.candidates(small, 0, 2))

    broken = sudoku.parse_grid("11" + "0" * 79)
    check("two 1s in one row are caught", sudoku.is_valid_grid(broken) is False)

    # ---- 3. solving a known puzzle --------------------------------------
    known_answer = (
        "534678912672195348198342567859761423426853791"
        "713924856961537284287419635345286179")

    start = time.perf_counter()
    answer = sudoku.solve_copy(small)
    took = (time.perf_counter() - start) * 1000

    check("the puzzle gets solved", answer is not None)
    check("the answer is the expected one",
          sudoku.grid_to_text(answer) == known_answer)
    check("the answer is a complete valid grid", sudoku.is_solved(answer))
    print("       solved in %.1f milliseconds" % took)

    # ---- 4. counting answers --------------------------------------------
    check("the puzzle has exactly one answer",
          sudoku.count_solutions(sudoku.copy_grid(small), limit=2) == 1)

    one_row = sudoku.copy_grid(answer)
    for col in range(9):
        one_row[0][col] = sudoku.EMPTY
    check("one empty row alone is still forced by the columns",
          sudoku.count_solutions(one_row, limit=2) == 1)

    many = sudoku.copy_grid(answer)
    for row in (0, 1):
        for col in range(9):
            many[row][col] = sudoku.EMPTY   # wipe two whole rows of clues
    check("removing many clues gives more than one answer",
          sudoku.count_solutions(many, limit=2) >= 2)

    check("counting does not change the grid", many[0][0] == sudoku.EMPTY)

    # ---- 5. generating ---------------------------------------------------
    start = time.perf_counter()
    puzzle, solution = sudoku.generate_puzzle(clues=30, seed=7)
    took = (time.perf_counter() - start) * 1000

    given = sum(1 for row in puzzle for value in row if value != sudoku.EMPTY)
    check("the generated puzzle is valid", sudoku.is_valid_grid(puzzle))
    check("the generated puzzle has one answer",
          sudoku.count_solutions(sudoku.copy_grid(puzzle), limit=2) == 1)
    check("the generated puzzle solves back to its own solution",
          sudoku.solve_copy(puzzle) == solution)
    check("the solution is complete", sudoku.is_solved(solution))
    print("       generated with %d clues in %.0f milliseconds" % (given, took))

    # ---- 6. same seed, same puzzle --------------------------------------
    again, _ = sudoku.generate_puzzle(clues=30, seed=7)
    check("the same seed gives the same puzzle", again == puzzle)

    print()
    print("All checks passed.")


if __name__ == "__main__":
    main()
