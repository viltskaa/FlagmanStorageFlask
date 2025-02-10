CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    token TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tokens_name ON tokens (name);

INSERT INTO tokens (name, token) VALUES ('АЛИСА2', '');
INSERT INTO tokens (name, token) VALUES ('СЕВЕРНОЕ', '');
