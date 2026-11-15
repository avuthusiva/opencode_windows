"""
sudoku.py - Sudoku solver and puzzle generator (learning version)

Only the standard library is used (random, sys). No install needed.

What is in this file, top to bottom:
    1. Helpers      - read a puzzle from text, print a grid
    2. Rule check   - which digits are still allowed in one cell?
    3. Solver       - backtracking search
    4. Counter      - count how many answers a puzzle has (used by generator)
    5. Generator    - build a full grid, then remove cells
    6. Command line - run this file to see it work

How to run:
    python sudoku.py                    generate one puzzle and solve it
    python sudoku.py puzzles.txt        solve every puzzle in a file
    python sudoku.py --clues 28         generate a puzzle with 28 clues
"""

import random
import sys

SIZE = 9          # the grid is 9 x 9
BOX = 3           # each small box is 3 x 3
EMPTY = 0         # 0 means "this cell has no digit yet"
DIGITS = set(range(1, 10))   # the allowed digits 1..9


# ---------------------------------------------------------------- 1. helpers

def parse_grid(text):
    """
    Turn 81 characters into a 9 x 9 list of lists.

    Digits 1..9 are kept as numbers. '0' and '.' mean an empty cell.
    Anything else is an error, so a bad file fails loudly instead of
    giving a wrong answer quietly.
    """
    cleaned = []
    for ch in text:
        if ch.isdigit():
            cleaned.append(int(ch))
        elif ch == ".":
            cleaned.append(EMPTY)
        else:
            raise ValueError("Unexpected character %r in puzzle text" % ch)

    if len(cleaned) != SIZE * SIZE:
        raise ValueError("A puzzle must have exactly 81 cells, found %d"
                         % len(cleaned))

    # Cut the flat list of 81 items into 9 rows of 9 items.
    return [cleaned[row * SIZE:(row + 1) * SIZE] for row in range(SIZE)]


def grid_to_text(grid):
    """Turn the grid back into 81 characters, using '.' for empty cells."""
    parts = []
    for row in range(SIZE):
        for col in range(SIZE):
            value = grid[row][col]
            parts.append("." if value == EMPTY else str(value))
    return "".join(parts)


def print_grid(grid):
    """Print the grid with lines between the boxes, so it is easy to read."""
    for row in range(SIZE):
        if row != 0 and row % BOX == 0:
            print("------+-------+------")
        line = []
        for col in range(SIZE):
            if col != 0 and col % BOX == 0:
                line.append("|")
            value = grid[row][col]
            line.append("." if value == EMPTY else str(value))
        print(" ".join(line))
    print()


def copy_grid(grid):
    """A real copy. Without this, both names would point to the same rows."""
    return [row[:] for row in grid]


def empty_grid():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


# ------------------------------------------------------------ 2. rule check

def candidates(grid, row, col):
    """
    Return the set of digits that may legally go in this cell.

    A digit is not allowed if it is already used in the same row,
    the same column, or the same 3 x 3 box.

    This is the only rule Sudoku has, and everything below is built
    on top of it.
    """
    used = set(grid[row])                                  # the whole row

    for r in range(SIZE):
        used.add(grid[r][col])                             # the whole column

    box_row = (row // BOX) * BOX                           # top of the box
    box_col = (col // BOX) * BOX                           # left of the box
    for r in range(box_row, box_row + BOX):
        for c in range(box_col, box_col + BOX):
            used.add(grid[r][c])

    # EMPTY is 0 and 0 is not inside DIGITS, so it is ignored here.
    return DIGITS - used


def _no_repeats(values):
    """True if the filled cells have no duplicate digit."""
    filled = [v for v in values if v != EMPTY]
    return len(filled) == len(set(filled))


def is_valid_grid(grid):
    """
    True if no digit appears twice in any row, column or box.

    This checks the puzzle itself. It does not check that the puzzle
    can be finished, only that it does not already break a rule.
    """
    for row in range(SIZE):
        if not _no_repeats(grid[row]):
            return False

    for col in range(SIZE):
        column = [grid[row][col] for row in range(SIZE)]
        if not _no_repeats(column):
            return False

    for box_row in range(0, SIZE, BOX):
        for box_col in range(0, SIZE, BOX):
            box = [grid[r][c]
                   for r in range(box_row, box_row + BOX)
                   for c in range(box_col, box_col + BOX)]
            if not _no_repeats(box):
                return False

    return True


def is_solved(grid):
    """True if every cell has a digit and the grid is still valid."""
    for row in range(SIZE):
        for col in range(SIZE):
            if grid[row][col] == EMPTY:
                return False
    return is_valid_grid(grid)


# --------------------------------------------------------------- 3. solver

def find_best_empty(grid):
    """
    Find the empty cell that is easiest to fill.

    We look at every empty cell and count its options. The cell with
    the fewest options is returned. If a cell has no option at all we
    return it immediately, because that branch can never work.

    This trick is called "MRV" (minimum remaining values). It is not
    needed for correctness, but it makes the search much faster:
    a normal puzzle is solved in a few milliseconds instead of seconds.

    Returns (row, col), or None when the grid has no empty cell.
    """
    best = None
    best_options = None

    for row in range(SIZE):
        for col in range(SIZE):
            if grid[row][col] != EMPTY:
                continue

            options = candidates(grid, row, col)
            if not options:
                return (row, col)          # dead cell, fail fast
            if best_options is None or len(options) < len(best_options):
                best = (row, col)
                best_options = options
                if len(options) == 1:
                    return best            # cannot do better than one option

    return best


def solve(grid):
    """
    Fill the grid in place. Returns True if it worked, False if not.

    How the recursion works:
        - find the empty cell with the fewest options
        - try each option in turn
        - call solve() again for the rest of the grid
        - if the rest failed, undo the guess and try the next option

    That "undo and try the next one" step is the backtracking part.
    """
    cell = find_best_empty(grid)
    if cell is None:
        return True                        # no empty cell left, we are done

    row, col = cell
    for value in sorted(candidates(grid, row, col)):
        grid[row][col] = value             # guess
        if solve(grid):
            return True                    # guess was fine, keep it
        grid[row][col] = EMPTY             # wrong guess, take it back

    return False                           # every option failed here


# -------------------------------------------------------------- 4. counter

def count_solutions(grid, limit=2):
    """
    Count the answers of this grid, but stop early at 'limit'.

    A good Sudoku has exactly one answer, so the generator only needs
    to know "is it 1, or is it 2 or more?". Stopping at 2 keeps it fast.

    The grid is left exactly as it was found.
    """
    count = 0

    def search(working):
        nonlocal count
        cell = find_best_empty(working)
        if cell is None:
            count += 1                     # a complete grid, that is one answer
            return

        row, col = cell
        for value in candidates(working, row, col):
            working[row][col] = value
            search(working)
            working[row][col] = EMPTY      # undo before the next try
            if count >= limit:
                return

    search(grid)
    return count


def solve_copy(grid):
    """Solve a copy and return it, or None if the puzzle has no answer."""
    work = copy_grid(grid)
    if solve(work):
        return work
    return None


# ------------------------------------------------------------ 5. generator

def fill_grid(grid, rng):
    """
    Fill an empty grid with a complete, valid solution.

    This is the solver again, except the options are shuffled, so every
    call gives a different finished grid.
    """
    cell = find_best_empty(grid)
    if cell is None:
        return True

    row, col = cell
    options = list(candidates(grid, row, col))
    rng.shuffle(options)

    for value in options:
        grid[row][col] = value
        if fill_grid(grid, rng):
            return True
        grid[row][col] = EMPTY

    return False


def generate_puzzle(clues=30, seed=None):
    """
    Make one puzzle and its answer.

    Steps:
        1. fill an empty grid completely  -> that is the answer
        2. copy it, then try to empty cells one by one
        3. after each removal, count the answers
        4. if there is still exactly one answer, keep the removal
           if there are now two or more, put the digit back
        5. stop when we reach the wanted number of clues

    Returns (puzzle, solution). The puzzle may end up with slightly more
    clues than asked, because some removals are refused.
    """
    rng = random.Random(seed)

    solution = empty_grid()
    fill_grid(solution, rng)

    puzzle = copy_grid(solution)

    # Try the cells in random order, so puzzles do not all look the same.
    spots = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    rng.shuffle(spots)

    remaining = SIZE * SIZE
    for (row, col) in spots:
        if remaining <= clues:
            break

        saved = puzzle[row][col]
        puzzle[row][col] = EMPTY

        if count_solutions(puzzle, limit=2) != 1:
            puzzle[row][col] = saved       # removal broke uniqueness, undo it
        else:
            remaining -= 1

    return puzzle, solution


# ------------------------------------------------------------ 6. command line

def read_puzzles(path):
    """
    Read a text file of puzzles. One puzzle per line, 81 characters.
    Lines starting with '#' and blank lines are skipped.
    """
    puzzles = []
    with open(path, "r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                puzzles.append((number, line, parse_grid(line)))
            except ValueError as error:
                print("Line %d skipped: %s" % (number, error))
    return puzzles


def solve_file(path):
    """Solve every puzzle in the file and print the result."""
    puzzles = read_puzzles(path)
    if not puzzles:
        print("No puzzles found in", path)
        return

    for number, text, grid in puzzles:
        print("Line %d, puzzle:" % number)
        print_grid(grid)

        if not is_valid_grid(grid):
            print("This puzzle breaks a Sudoku rule, skipping it.\n")
            continue

        answers = count_solutions(copy_grid(grid), limit=3)
        print("Answers found (counting stops at 3):", answers)

        answer = solve_copy(grid)
        if answer is None:
            print("No answer exists for this puzzle.\n")
            continue

        print("Solved:")
        print_grid(answer)


def generate(clues):
    """Generate one puzzle with the given number of clues, then solve it."""
    puzzle, solution = generate_puzzle(clues=clues)

    given = sum(1 for row in puzzle for value in row if value != EMPTY)
    print("Puzzle with %d clues:" % given)
    print_grid(puzzle)

    answer = solve_copy(puzzle)
    if answer is None:
        print("Bug: the generator made a puzzle with no answer.")
    else:
        print("Solved:")
        print_grid(answer)

    print("Check, answer matches the hidden solution:", answer == solution)
    print()
    print("Puzzle as one line, easy to save and reuse:")
    print(grid_to_text(puzzle))


def main(argv):
    clues = 30
    path = None

    args = argv[1:]
    if args and args[0] == "--clues":
        if len(args) < 2:
            print("Please give a number after --clues, for example --clues 28")
            return 1
        clues = int(args[1])
    elif args:
        path = args[0]

    if path:
        solve_file(path)
    else:
        generate(clues)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
