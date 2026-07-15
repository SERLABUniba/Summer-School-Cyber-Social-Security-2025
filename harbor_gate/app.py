import os
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "ctf-dev-secret-change-me")

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "naval_ctf"),
    "user": os.getenv("DB_USER", "ctf_user"),
    "password": os.getenv("DB_PASSWORD", "ctf_password"),
}

FLAG = os.getenv("FLAG", "flag{demo_flag_sostituiscila_in_produzione}")


def get_db():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


@app.get("/")
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.post("/api/login")
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # VULNERABILITÀ INTENZIONALE PER LA CTF:
    # l'input dell'utente viene concatenato direttamente nella query.
    query = (
    "SELECT id, username, full_name, role, is_staff "
    "FROM users "
    f"WHERE username = '{username}' AND password = '{password}' "
    "ORDER BY is_staff DESC, id ASC "
    "LIMIT 1;"
)

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                user = cur.fetchone()
    except Exception:
        return {"ok": False, "message": "Errore di autenticazione."}, 401

    if not user:
        return {"ok": False, "message": "Credenziali non valide."}, 401

    session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "is_staff": user["is_staff"],
    }

    return {"ok": True, "redirect":  url_for("dashboard")}


@app.get("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("index"))

    flag = FLAG if user["is_staff"] else None
    return render_template("dashboard.html", user=user, flag=flag)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
