CREATE TABLE office_entries (
    id BIGSERIAL PRIMARY KEY,
    author_id TEXT NOT NULL,
    message_id TEXT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    UNIQUE (author_id, date),
    CONSTRAINT fk_message FOREIGN KEY (message_id, author_id)
        REFERENCES public.message (message_id, author_id)
        ON DELETE CASCADE
);