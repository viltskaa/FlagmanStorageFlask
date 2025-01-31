CREATE TABLE IF NOT EXISTS on_shipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id INTEGER NOT NULL REFERENCES shipment_item(id) ON DELETE CASCADE,
    qrcode TEXT UNIQUE NOT NULL REFERENCES item(qrcode) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_on_shipment_qrcode ON on_shipment (qrcode);