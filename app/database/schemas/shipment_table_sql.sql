CREATE TABLE IF NOT EXISTS shipment_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL,
    count_cur INTEGER NOT NULL,
    count_all INTEGER NOT NULL,
    worker_id INTEGER REFERENCES worker(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_shipment_item_article ON shipment_item (article);