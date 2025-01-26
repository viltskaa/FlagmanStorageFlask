DROP TABLE IF EXISTS item;

CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL,
    qrcode TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL
);

CREATE INDEX idx_item_article ON item (article);