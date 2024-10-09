CREATE TABLE IF NOT EXISTS users (
    id uuid DEFAULT gen_random_uuid(),
    name VARCHAR(56),
    surname VARCHAR(56),
    email VARCHAR(56),
    plan VARCHAR(16),
    PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS portfolios (
    id uuid DEFAULT gen_random_uuid(),
    type VARCHAR(16),
    user_id uuid,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES "users" (id)
);
