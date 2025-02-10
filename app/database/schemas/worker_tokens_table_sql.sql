CREATE TABLE IF NOT EXISTS worker_tokens (
    worker_id INTEGER NOT NULL,
    token_id INTEGER NOT NULL,
    PRIMARY KEY (worker_id, token_id),
    FOREIGN KEY (worker_id) REFERENCES worker (id) ON DELETE CASCADE,
    FOREIGN KEY (token_id) REFERENCES tokens (id) ON DELETE CASCADE
);