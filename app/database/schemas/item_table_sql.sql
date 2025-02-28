CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL,
    qrcode TEXT UNIQUE NOT NULL,
    created_date DATE DEFAULT (DATE('now')),
    created_time TIME DEFAULT (TIME('now')),
    status TEXT NOT NULL,
    worker_id INTEGER,
    FOREIGN KEY (worker_id) REFERENCES worker(id)
);

CREATE INDEX IF NOT EXISTS idx_item_article ON item (article);