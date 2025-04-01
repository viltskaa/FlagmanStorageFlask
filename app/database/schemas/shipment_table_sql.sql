CREATE TABLE IF NOT EXISTS shipment_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL, #тут юник
    article TEXT NOT NULL,
    orderUid TEXT NOT NULL,
    worker_id INTEGER,
    created_date DATE DEFAULT (DATE('now')),
    created_time TIME DEFAULT (TIME('now')),
    action_time TIME DEFAULT NULL,
    is_active TEXT DEFAULT 'RECEIVED' CHECK (is_active IN ('SHIPPED', 'RECEIVED', 'POSTPONED','TO_SHIP')),
    scanned TEXT DEFAULT 'NOTSCANNED' CHECK (scanned IN ('NOTSCANNED','SCANNED')),
    scanned_time DATETIME NOT NULL DEFAULT '0000-12-31 00:00:00',
    for_this TEXT NOT NULL,
    supply_id TEXT NOT NULL,
    FOREIGN KEY (for_this) REFERENCES tokens(name)
    FOREIGN KEY (worker_id) REFERENCES worker(id)
);

CREATE INDEX IF NOT EXISTS idx_shipment_item_article ON shipment_item (article);