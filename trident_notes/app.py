import os
from flask import Flask, abort, redirect, render_template, request, url_for, make_response, session
from werkzeug.middleware.proxy_fix import ProxyFix
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "maritime_ctf"),
    "user": os.getenv("DB_USER", "ctf_user"),
    "password": os.getenv("DB_PASSWORD", "ctf_password"),
}

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)
app.secret_key = os.getenv("FLASK_SECRET", "change-me")

FLAG = os.getenv("FLAG", "SSCSS{stored_xss_demo_flag}")


def get_db():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def current_user():
    return session.get("user")

def require_login():
    if not session.get("user"):
        return redirect(url_for("login"))
    return None


@app.get("/")
def index():
    # Chiunque può vedere la bacheca dei post
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, excerpt, author, published_at
                FROM posts
                ORDER BY published_at DESC;
            """)
            posts = cur.fetchall()

    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            return "Dati mancanti", 400
                
        with get_db() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        "INSERT INTO users (username, password) VALUES (%s, %s)", 
                        (username, password)
                    )
                    conn.commit()
                    return redirect(url_for("login"))
                except psycopg2.IntegrityError:
                    return "Username già in uso", 400
                    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                
                if user and user['password'] == password:
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    return redirect(url_for("index"))
                    
        return "Credenziali non valide", 401
        
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/post/<int:post_id>")
def post(post_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            # I dettagli del post sono pubblici
            cur.execute("""
                SELECT id, title, body, excerpt, author, published_at
                FROM posts
                WHERE id = %s;
            """, (post_id,))
            article = cur.fetchone()

            if not article:
                abort(404)

            # Mostriamo i commenti solo se l'utente è loggato, filtrandoli per il suo ID
            user_id = session.get("user_id")
            if user_id:
                cur.execute("""
                    SELECT id, author, body, created_at
                    FROM comments
                    WHERE post_id = %s AND user_id = %s
                    ORDER BY created_at ASC;
                """, (post_id, user_id))
                comments = cur.fetchall()
            else:
                comments = []

    response = make_response(render_template(
        "post.html",
        article=article,
        comments=comments
    ))

    # Il flag viene comunque impostato nel cookie (ottimo per la sfida XSS)
    response.set_cookie(
        "session_token",
        FLAG,
        httponly=False,
        samesite="Lax"
    )

    return response


@app.post("/post/<int:post_id>/comment")
def add_comment(post_id):
    # Impediamo l'inserimento di commenti ad utenti non autenticati
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    # Usiamo lo username dell'utente loggato come autore del commento
    author = session.get("username", "Cadetto")
    body = request.form.get("body", "").strip()[:2000]

    if not body:
        return redirect(url_for("post", post_id=post_id))

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO comments (post_id, user_id, author, body)
                VALUES (%s, %s, %s, %s);
            """, (post_id, user_id, author, body))
            conn.commit()

    return redirect(url_for("post", post_id=post_id))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
