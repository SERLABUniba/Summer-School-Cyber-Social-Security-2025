CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    role VARCHAR(80) NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, full_name, role, is_staff) VALUES
    ('stato.maggiore', 'vita_barbetta', 'Stato Maggiore', 'Autorità di comando', TRUE);
