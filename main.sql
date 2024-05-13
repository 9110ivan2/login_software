\c login_info

CREATE TABLE login_table (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE,
    address VARCHAR(50),
    registration TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT password CHECK (
        LENGTH(password) >= 8)
);