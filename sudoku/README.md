# Sudoku in Python - learning notes

This folder has the logic and a small web page. The point is to see how
a small set of rules becomes a working program.

## What is in the folder

```
sudoku/
├── README.md          these notes
├── src/               the Python code
│   ├── sudoku.py      all the logic, rule check, solver, generator, command line
│   └── export_to_js.py  runs sudoku.py and writes data/puzzles.js
├── tests/
│   └── test_sudoku.py 20 small checks, so you can see the code really works
├── data/
│   ├── puzzles.txt    sample puzzles in a simple text format
│   └── puzzles.js     written by export_to_js.py, do not edit by hand
└── web/
    └── sudoku.html    the browser page, same logic in JavaScript
```

## How to run

Open a terminal and go to this folder:

```
cd C:\Users\asvr4\Desktop\work\opencode\sudoku
```

Then:

```
python src/sudoku.py                  # generate one puzzle, then solve it
python src/sudoku.py --clues 28       # same, but ask for 28 clues
python src/sudoku.py data/puzzles.txt # solve every puzzle inside that file
python tests/test_sudoku.py           # run the self checks
```

You need Python 3 only. Nothing to install.

## Running in the browser

Double click `web\sudoku.html`, or right click it and open it with Chrome. That is
all, the page needs no server and no internet.

On the page you can:

* pick a clue count and press **New puzzle** (the page makes it itself, in
  JavaScript, in about 10 milliseconds)
* click an empty cell, then click a number on the number pad next to the board.
  Typing 1 to 9 on the keyboard works too, backspace clears a cell, and the arrow
  keys move around. Cells that came with the puzzle are fixed and cannot be changed.
* press **Check** to see which of your digits are wrong, or **Hint** to get one
  forced cell
* press **Show solution** to fill the whole board

The page is self contained. The old puzzle list was removed, so the page no
longer reads `data/puzzles.js`. That file is still written by the Python code
and kept only as a sample of what Python produced:

```
python src/export_to_js.py
```

The JavaScript functions have the same names and the same jobs as the Python
ones: `parseGrid`, `candidates`, `findBestEmpty`, `solve`, `countSolutions`,
`generatePuzzle`. If you understand one file, you understand the other.

## The whole idea in one line

Sudoku has one rule: a digit may not repeat in its row, its column, or its
3 x 3 box. Everything else in this program is just searching, plus a check
after every guess.

## Step 1 - reading the puzzle

A puzzle is stored as one line of 81 characters. `0` or `.` means empty.

`parse_grid()` walks the text once, then cuts the flat list of 81 numbers into
9 rows of 9. The slice `cleaned[row * 9:(row + 1) * 9]` is the whole trick,
for example for row 2 it takes items 18 to 26.

If the text has a wrong character or the wrong length, the function raises
`ValueError`. Bad input should stop the program, not give a wrong answer.

## Step 2 - candidates

`candidates(grid, row, col)` returns the digits that are still allowed in one
empty cell. It collects every digit already used in the row, the column and the
box, and subtracts that from `{1..9}`:

```python
return DIGITS - used
```

That single line is the entire rule of Sudoku.

One small detail: the empty cell itself holds `0`, and `0` is not inside
`DIGITS`, so we do not have to remove it by hand.

## Step 3 - backtracking

`solve()` works like this:

1. find an empty cell
2. try one allowed digit
3. call `solve()` again for the rest of the grid
4. if the rest failed, put the cell back to `0` and try the next digit

Step 4 is the "backtrack". The program is not smart about Sudoku, it is simply
willing to take a guess back. With the rules in place that is enough to solve
any real puzzle.

In PL/SQL terms: this is a recursive function that changes a global table and
undoes the change when the recursive call returns `FALSE`. The undo line
`grid[row][col] = EMPTY` is the important one. If you forget it, the grid keeps
guesses that were already proven wrong, and the search goes wrong.

## Step 4 - why it is fast: pick the easiest cell first

`find_best_empty()` does not just take the first empty cell. It takes the empty
cell with the fewest options.

Why this matters:

* an empty grid has 9 options in every cell, so guessing there is a coin flip
* a cell with only one option is a forced move, no guessing at all
* a cell with zero options cannot work, so the program can stop that branch at
  once instead of filling in 20 more cells first

This is called MRV (minimum remaining values). It changes the search tree from
huge to small. On this laptop the hardest known puzzle solves in about
1 millisecond, and generating a fresh 30 clue puzzle takes about 20-30
milliseconds.

## Step 5 - counting answers

A Sudoku is only a good puzzle if it has exactly one answer.

`count_solutions()` is the same search, but instead of stopping at the first
answer it counts them, and stops at a limit (normally 2). If it reaches 2 we
already know the puzzle is not unique, so there is no need to keep counting.

Two things to notice in that function:

* it uses `nonlocal count`, because the inner function has to change a variable
  from the outer function
* it undoes every guess, so the grid you pass in comes back unchanged

A small fact worth remembering, and it is checked in `test_sudoku.py`: if you
empty one whole row of a finished grid, the answer is still unique, because
each column is missing exactly one digit. Empty two whole rows and the puzzle
suddenly has many answers.

## Step 6 - generating a puzzle

`generate_puzzle()` does three things:

1. fill an empty grid completely. This is the solver again, only the options
   are shuffled, so each run gives a different finished grid
2. copy that finished grid and try to blank out cells, in random order
3. after each blanking, count the answers. If there is still exactly one
   answer, keep the blank. If there are two or more, put the digit back

The result is a puzzle plus its answer. Because some blankings are refused, you
may end up with a few more clues than you asked for. Asking for 30 usually
gives exactly 30, asking for 22 may stop at 24 or so. That is the honest
behaviour of a greedy method, not a bug.

About clue counts: the proven minimum for a unique Sudoku is 17 clues, and such
puzzles are rare and hard. So do not ask for 17 and expect it to reach 17, and
do not expect it to be quick.

## Step 7 - tests

`test_sudoku.py` checks the parts one by one: reading text, the rule check, the
solver against a known answer, uniqueness counting, generation, and that the
same seed gives the same puzzle.

Run it after any change. A test that fails tells you exactly which idea broke,
which is much faster than staring at a printed grid.

## If you know PL/SQL, think of it like this

| Sudoku idea | PL/SQL idea |
|---|---|
| 9 x 9 list of lists | two dimensional `TYPE ... IS TABLE OF ...` collection |
| `candidates()` | `MINUS` between two small sets, done in memory |
| `solve()` recursion | recursive procedure that returns `BOOLEAN` |
| undo after a guess | rollback of the last change, except we do it by hand |
| `is_valid_grid()` | a check constraint, but checked by the program |

The big difference is the undo. In SQL a failed statement rolls back by itself.
In a Python search you write the undo line yourself, and forgetting it is the
most common bug.

## Things to try next

1. Add a counter for "guesses tried" and print it. You will see MRV makes the
   number drop a lot compared to plain first-empty-cell order.
2. Rate difficulty by the number of guesses the solver needed, then print
   easy / medium / hard for each puzzle in a file.
3. Save generated puzzles to a file with `grid_to_text()`, and read them back
   with `python src/sudoku.py thatfile.txt`.
4. Add a `hint` function: return one cell that currently has only one option.
5. Change `generate_puzzle()` so it keeps trying until it reaches the exact
   clue count you asked for, and see how slow 22 clues becomes.
6. Later, if you want a screen, the same `sudoku.py` can be used from a small
   web page without changing the logic at all.
