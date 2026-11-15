"""
db.py - small DuckDB layer for the sudoku app

The database file is data/sudock.duckdb. The tables come from schema.sql.

Run:
    python src/db.py --init      create the file, tables and sequences
    python src/db.py --tables    list every table and its columns
    python src/db.py --show      show a few rows from every table

Every table has created_at and updated_at. This file always sets updated_at
by hand when it changes a row, because DuckDB has no triggers.
"""

import os
import sys

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
DB_PATH = os.path.join(DATA, "sudock.duckdb")
SCHEMA_PATH = os.path.join(HERE, "schema.sql")


def connect(path=DB_PATH):
    """Open the database, creating the data folder if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return duckdb.connect(path)


def init_db(path=DB_PATH):
    """Create the database file and every table in schema.sql."""
    con = connect(path)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as handle:
        con.execute(handle.read())
    return con


def find_puzzle(con, puzzle_text):
    """Return the puzzle_id for this exact puzzle text, or None."""
    row = con.execute(
        "SELECT puzzle_id FROM puzzles WHERE puzzle = ? LIMIT 1",
        [puzzle_text],
    ).fetchone()
    return row[0] if row else None


def save_puzzle(con, puzzle, solution, source, difficulty=None):
    """
    Add one puzzle. If the same 81 characters are already stored, return the
    existing id instead of adding a duplicate.
    """
    existing = find_puzzle(con, puzzle)
    if existing is not None:
        return existing

    clues = sum(1 for ch in puzzle if ch not in ".0")
    row = con.execute(
        """
        INSERT INTO puzzles (puzzle, solution, clues, difficulty, source)
        VALUES (?, ?, ?, ?, ?)
        RETURNING puzzle_id
        """,
        [puzzle, solution, clues, difficulty, source],
    ).fetchone()
    return row[0]


def start_game(con, puzzle_id):
    """Begin a game for a puzzle and return the new game_id."""
    row = con.execute(
        """
        INSERT INTO games (puzzle_id) VALUES (?) RETURNING game_id
        """,
        [puzzle_id],
    ).fetchone()
    return row[0]


def record_move(con, game_id, row_no, col_no, value, is_correct=True):
    """Store one digit the player put in a cell and return the move_id."""
    row = con.execute(
        """
        INSERT INTO moves (game_id, row_no, col_no, value, is_correct)
        VALUES (?, ?, ?, ?, ?) RETURNING move_id
        """,
        [game_id, row_no, col_no, value, is_correct],
    ).fetchone()
    return row[0]


def finish_game(con, game_id, elapsed_ms, mistakes=0, status="finished"):
    """Close a game and stamp finished_at and updated_at."""
    con.execute(
        """
        UPDATE games
           SET status = ?,
               finished_at = current_timestamp,
               elapsed_ms = ?,
               mistakes = ?,
               updated_at = current_timestamp
         WHERE game_id = ?
        """,
        [status, elapsed_ms, mistakes, game_id],
    )


def set_setting(con, key, value):
    """Add or change one setting, keeping created_at and moving updated_at."""
    con.execute(
        """
        INSERT INTO settings (setting_key, setting_value)
        VALUES (?, ?)
        ON CONFLICT (setting_key) DO UPDATE
           SET setting_value = excluded.setting_value,
               updated_at = now()
        """,
        [key, value],
    )


def get_setting(con, key):
    """Return one setting value, or None."""
    row = con.execute(
        "SELECT setting_value FROM settings WHERE setting_key = ?",
        [key],
    ).fetchone()
    return row[0] if row else None


def table_names(con):
    """All user tables, in alphabetical order."""
    rows = con.execute(
        """
        SELECT table_name
          FROM information_schema.tables
         WHERE table_schema = 'main'
         ORDER BY table_name
        """
    ).fetchall()
    return [row[0] for row in rows]


def table_columns(con):
    """Every column of every table, with its type."""
    return con.execute(
        """
        SELECT table_name, column_name, data_type
          FROM information_schema.columns
         WHERE table_schema = 'main'
         ORDER BY table_name, ordinal_position
        """
    ).fetchall()


def show(con):
    """Print the tables, their columns, and a few rows from each."""
    print("Tables in %s" % DB_PATH)
    print()

    for name in table_names(con):
        print("%s" % name)
        columns = con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = ? ORDER BY ordinal_position",
            [name],
        ).fetchall()
        print("  " + ", ".join("%s %s" % (col, kind) for col, kind in columns))
        count = con.execute("SELECT count(*) FROM %s" % name).fetchone()[0]
        print("  rows: %d" % count)
        print()

    print("Rows in puzzles (first 5):")
    rows = con.execute(
        "SELECT puzzle_id, clues, difficulty, source, created_at FROM puzzles "
        "ORDER BY puzzle_id LIMIT 5"
    ).fetchall()
    if not rows:
        print("  none")
    for row in rows:
        print("  %s" % (row,))
    print()


def main(argv):
    if "--init" in argv:
        con = init_db()
        print("Created %s" % DB_PATH)
        print("Tables: %s" % ", ".join(table_names(con)))
        return 0

    con = init_db()
    if "--tables" in argv:
        for name in table_names(con):
            print(name)
        return 0

    show(con)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
