-- schema.sql - tables for the sudoku app in data/sudock.duckdb
--
-- Every table has created_at and updated_at. Nothing changes a row without
-- also setting updated_at, so you can always tell when a row was last touched.
--
-- Run it with:  python src/db.py --init

CREATE SEQUENCE IF NOT EXISTS puzzle_seq START 1;
CREATE SEQUENCE IF NOT EXISTS game_seq START 1;
CREATE SEQUENCE IF NOT EXISTS move_seq START 1;

-- One row for each puzzle the app knows about.
CREATE TABLE IF NOT EXISTS puzzles (
    puzzle_id   BIGINT PRIMARY KEY DEFAULT nextval('puzzle_seq'),
    puzzle      VARCHAR NOT NULL,
    solution    VARCHAR,
    clues       INTEGER NOT NULL,
    difficulty  VARCHAR,
    source      VARCHAR NOT NULL DEFAULT 'unknown',
    created_at  TIMESTAMP NOT NULL DEFAULT current_timestamp,
    updated_at  TIMESTAMP NOT NULL DEFAULT current_timestamp,
    CHECK (length(puzzle) = 81),
    CHECK (solution IS NULL OR length(solution) = 81)
);

-- One row for each time somebody plays a puzzle.
CREATE TABLE IF NOT EXISTS games (
    game_id     BIGINT PRIMARY KEY DEFAULT nextval('game_seq'),
    puzzle_id   BIGINT REFERENCES puzzles (puzzle_id),
    status      VARCHAR NOT NULL DEFAULT 'playing',
    mistakes    INTEGER NOT NULL DEFAULT 0,
    elapsed_ms  BIGINT,
    started_at  TIMESTAMP NOT NULL DEFAULT current_timestamp,
    finished_at TIMESTAMP,
    created_at  TIMESTAMP NOT NULL DEFAULT current_timestamp,
    updated_at  TIMESTAMP NOT NULL DEFAULT current_timestamp,
    CHECK (status IN ('playing', 'finished', 'abandoned'))
);

-- One row for each digit the player puts in a cell.
CREATE TABLE IF NOT EXISTS moves (
    move_id     BIGINT PRIMARY KEY DEFAULT nextval('move_seq'),
    game_id     BIGINT REFERENCES games (game_id),
    row_no      INTEGER NOT NULL,
    col_no      INTEGER NOT NULL,
    value       INTEGER NOT NULL,
    is_correct  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT current_timestamp,
    updated_at  TIMESTAMP NOT NULL DEFAULT current_timestamp,
    CHECK (row_no BETWEEN 0 AND 8),
    CHECK (col_no BETWEEN 0 AND 8),
    CHECK (value BETWEEN 1 AND 9)
);

-- Small key/value table, for example the chosen theme.
CREATE TABLE IF NOT EXISTS settings (
    setting_key   VARCHAR PRIMARY KEY,
    setting_value VARCHAR NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT current_timestamp,
    updated_at    TIMESTAMP NOT NULL DEFAULT current_timestamp
);
