CREATE TABLE IF NOT EXISTS shipment_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL,
    count_cur INTEGER NOT NULL,
    count_all INTEGER NOT NULL,
    worker_id INTEGER REFERENCES worker(id),
    created_date DATE DEFAULT (DATE('now')),
    created_time TIME DEFAULT (TIME('now')),
    is_active TEXT DEFAULT 'RECEIVED' CHECK (is_active IN ('SHIPPED', 'RECEIVED','POSTPONED'))
);

CREATE INDEX IF NOT EXISTS idx_shipment_item_article ON shipment_item (article);