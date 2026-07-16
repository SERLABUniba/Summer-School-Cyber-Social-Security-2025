CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    excerpt TEXT NOT NULL,
    body TEXT NOT NULL,
    author VARCHAR(120) NOT NULL,
    published_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- Collegamento all'utente
    author VARCHAR(80) NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO posts (title, excerpt, body, author, published_at) VALUES (
    'Ai nuovi cadetti: il valore del giuramento',
    'Messaggio di incoraggiamento rivolto ai cadetti che hanno concluso il giuramento.',
    'Cadetti,

il giuramento non è soltanto una formula: rappresenta la scelta quotidiana di servire con disciplina, responsabilità e spirito di squadra.

Il Comando Marittimo Tirreno vi rivolge un sincero augurio per l''inizio del vostro percorso. Studiate, collaborate e mantenete sempre saldo il legame con il vostro equipaggio.

Buon vento.

Ammiraglio Valerio Bartoli',
    'Ammiraglio Valerio Bartoli',
    NOW()
);

INSERT INTO posts (title, excerpt, body, author, published_at) VALUES (
    'Aggiornamento addestrativo del primo trimestre',
    'Indicazioni generali sulle attività formative e sulle esercitazioni pianificate.',
    'Le unità formative inizieranno il ciclo addestrativo del primo trimestre secondo la pianificazione comunicata ai reparti.

Ulteriori avvisi verranno pubblicati nella sezione documentale.',
    'Ufficio Addestramento',
    NOW() - INTERVAL '3 days'
);

INSERT INTO users (username, password) VALUES
  ('admin', 'vitabarchetta');

INSERT INTO comments (post_id, author, body, user_id) VALUES
  (1, 'Luca R.', 'Onorato di iniziare questo percorso. Buon vento a tutti!', 1),
  (1, 'Giulia M.', 'Grazie per il messaggio di incoraggiamento.', 1);