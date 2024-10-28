DROP TABLE IF EXISTS item;

CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT UNIQUE NOT NULL,
    count INTEGER DEFAULT 0
);

CREATE INDEX idx_item_article ON item (article);