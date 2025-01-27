CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL,
    qrcode TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    worker_id INTEGER REFERENCES worker(id)
);

CREATE INDEX IF NOT EXISTS idx_item_article ON item (article);