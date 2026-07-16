from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import sqlite3
import os
import json
from functools import wraps
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "app.db"
RED_VS_BLUE_DIR = Path("/opt/red_vs_blue")
CSS_MDO_FILE = Path("/opt/css_mdo/css_mdo.json")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")

TEAMS = [
    {"id": "cavour", "name": "Cavour", "code": "Cavour", "accent": "#63d6ff"},
    {"id": "garibaldi", "name": "Garibaldi", "code": "Garibaldi", "accent": "#f2c76b"},
    {"id": "trieste", "name": "Trieste", "code": "Trieste", "accent": "#7ce7a7"},
    {"id": "vespucci", "name": "Vespucci", "code": "Vespucci", "accent": "#ff7d9b"},
]

SHIP_COMPONENT_ORDER = ["radar", "sails", "compass", "rudder"]

SHIP_COMPONENT_META = {
    "radar": {"label": "Radar", "mark": "RD"},
    "sails": {"label": "Comunicazioni", "mark": "CM"},
    "compass": {"label": "Bussola", "mark": "BS"},
    "rudder": {"label": "Timone", "mark": "TM"},
}

USERS = [
    {"username": "admin", "password": "admin123!", "role": "admin", "team_id": None, "display_name": "Direzione CTF"},
    {"username": "gruppo1", "password": "gruppo1", "role": "team", "team_id": "cavour", "display_name": "Gruppo Nave 1"},
    {"username": "gruppo2", "password": "gruppo2", "role": "team", "team_id": "garibaldi", "display_name": "Gruppo Nave 2"},
    {"username": "gruppo3", "password": "gruppo3", "role": "team", "team_id": "trieste", "display_name": "Gruppo Nave 3"},
    {"username": "gruppo4", "password": "gruppo4", "role": "team", "team_id": "vespucci", "display_name": "Gruppo Nave 4"},
]

MODULES = [
    {
        "id": "m1",
        "title": "Cyber-Social Security in Multi-Domain Operations",
        "mission": "Comprendere dove si propaga l'attacco e costruire la mappa cyber, informational, cognitive e physical.",
        "type": "CTF",
        "challenge_title": "Attack Path Mapping",
        "points": 100,
        "challenges": [
            {"id": "m1-c1", "title": "Attack Path Mapping", "expected_flag": "FLAG{MDO_PATH}", "points": 100},
        ],
    },
    {
        "id": "m2",
        "title": "Cyber Threat Intelligence",
        "mission": "Identificare malware, APT, IOC e TTP MITRE ATT&CK dopo la scoperta dell'attacco.",
        "type": "CTI",
        "challenge_title": "APT Attribution",
        "points": 120,
        "challenges": [
            {"id": "m2-c1", "title": "APT Attribution", "expected_flag": "FLAG{CTI_APT}", "points": 120},
        ],
    },
    {
        "id": "m3",
        "title": "Red Team vs Blue Team",
        "mission": "Simulare phishing, credential theft e lateral movement contro EDR, firewall, SIEM e incident response.",
        "type": "SIM",
        "challenge_title": "Mission Under Pressure",
        "points": 120,
        "challenges": [
            {"id": "m3-c1", "title": "Mission Under Pressure", "expected_flag": "FLAG{RTBT_PRESSURE}", "points": 120},
        ],
    },
    {
        "id": "m4",
        "title": "Malware Analysis",
        "mission": "Analizzare una workstation di bordo compromessa e identificare C2, persistence e payload.",
        "type": "REV",
        "challenge_title": "Reverse Completed",
        "points": 140,
        "challenges": [
            {"id": "m4-c1", "title": "Reverse Completed", "expected_flag": "FLAG{MALWARE_REV}", "points": 140},
        ],
    },
    {
        "id": "m5",
        "title": "Wargaming",
        "mission": "Assumere ruoli decisionali e rispondere a eventi dinamici: satellite offline, deepfake, GPS spoofing.",
        "type": "WAR",
        "challenge_title": "Decision Cycle",
        "points": 110,
        "challenges": [
            {"id": "m5-c1", "title": "Decision Cycle", "expected_flag": "FLAG{WARGAME_CYCLE}", "points": 110},
        ],
    },
    {
        "id": "m6",
        "title": "Hybrid Warfare",
        "mission": "Correlare cyber, droni, propaganda, sabotaggio e social engineering in una campagna ibrida.",
        "type": "HYB",
        "challenge_title": "Hybrid Campaign Reconstruction",
        "points": 140,
        "challenges": [
            {"id": "m6-c1", "title": "Hybrid Campaign Reconstruction", "expected_flag": "FLAG{HYBRID_RECON}", "points": 140},
        ],
    },
    {
        "id": "m7",
        "title": "AI Generativa per la Cyber-Social Security",
        "mission": "Rilevare deepfake, immagini false, audio sintetico e phishing generato da LLM recuperando fiducia nelle fonti.",
        "type": "AI",
        "challenge_title": "Trust Recovery",
        "points": 130,
        "challenges": [
            {"id": "m7-c1", "title": "Trust Recovery", "expected_flag": "FLAG{AI_TRUST}", "points": 130},
        ],
    },
    {
        "id": "final",
        "title": "Grande CTF Finale",
        "mission": "Usare simultaneamente CTI, malware analysis, OSINT, decision making, AI, Cyber-Social Security e MDO.",
        "type": "FINAL",
        "challenge_title": "Blue Team Recovery Operations",
        "points": 250,
        "challenges": [
            {"id": "final-c1", "title": "Blue Team Recovery Operations", "expected_flag": "FLAG{FINAL_BRO}", "points": 250},
        ],
    },
]


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = db()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS module_state (
            team_id TEXT NOT NULL,
            module_id TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (team_id, module_id)
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id TEXT NOT NULL,
            module_id TEXT NOT NULL,
            challenge_id TEXT NOT NULL,
            submitted_flag TEXT NOT NULL,
            is_correct INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    for team in TEAMS:
        for module in MODULES:
            cur.execute(
                """
                INSERT OR IGNORE INTO module_state(team_id, module_id, enabled)
                VALUES (?, ?, ?)
                """,
                (team["id"], module["id"], 1 if module["id"] == "m1" else 0),
            )

    conn.commit()
    conn.close()


def safe_challenge_id(name, folder_name):
    raw = (name or folder_name or "challenge").strip().lower()
    cleaned = []
    for ch in raw:
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in (" ", "-", "_"):
            cleaned.append("-")
    slug = "".join(cleaned).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or folder_name.lower() or "challenge"


def load_red_vs_blue_challenges():
    challenges = []

    if not RED_VS_BLUE_DIR.exists() or not RED_VS_BLUE_DIR.is_dir():
        return challenges

    for challenge_dir in sorted(RED_VS_BLUE_DIR.iterdir()):
        if not challenge_dir.is_dir():
            continue

        challenge_json = challenge_dir / "challenge.json"
        if not challenge_json.exists():
            continue

        try:
            data = json.loads(challenge_json.read_text(encoding="utf-8"))
        except Exception:
            continue

        name = (data.get("name") or challenge_dir.name).strip()
        challenge_id = f"m3-{safe_challenge_id(name, challenge_dir.name)}"

        challenges.append(
            {
                "id": challenge_id,
                "folder": challenge_dir.name,
                "title": name,
                "authors": data.get("autors", ""),
                "description": data.get("description", ""),
                "url": data.get("url", ""),
                "expected_flag": (data.get("flag") or "").strip(),
                "type": "RTB",
                "points": 120,
            }
        )

    return challenges


def get_modules():
    modules = []

    for module in MODULES:
        item = {**module}
        item["challenges"] = [dict(ch) for ch in module.get("challenges", [])]

        if item["id"] == "m1":
            dynamic_challenges = load_css_mdo_challenges()
            if dynamic_challenges:
                item["challenges"] = dynamic_challenges
                item["challenge_title"] = "Cyber-Social Security MDO Dynamic Pack"
                item["points"] = sum(ch.get("points", 0) for ch in dynamic_challenges) or item.get("points", 0)

        if item["id"] == "m3":
            dynamic_challenges = load_red_vs_blue_challenges()
            item["challenges"] = dynamic_challenges
            item["challenge_title"] = "Red Team vs Blue Team Dynamic Pack"
            item["points"] = sum(ch.get("points", 0) for ch in dynamic_challenges) or item.get("points", 0)

        modules.append(item)

    return modules

def load_css_mdo_challenges():
    challenges = []

    if not CSS_MDO_FILE.exists() or not CSS_MDO_FILE.is_file():
        return challenges

    try:
        raw_items = json.loads(CSS_MDO_FILE.read_text(encoding="utf-8"))
    except Exception:
        return challenges

    if not isinstance(raw_items, list):
        return challenges

    for idx, item in enumerate(raw_items, start=1):
        if not isinstance(item, dict):
            continue

        name = (item.get("name") or f"MDO Challenge {idx}").strip()
        challenge_id = f"m1-{safe_challenge_id(name, str(idx))}"

        challenges.append({
            "id": challenge_id,
            "title": name,
            "authors": item.get("autors", ""),
            "description": item.get("description", ""),
            "url": item.get("url", ""),
            "expected_flag": (item.get("flag") or "").strip(),
            "type": "MDO",
            "points": 100
        })

    return challenges


def find_module(modules, module_id):
    return next((m for m in modules if m["id"] == module_id), None)


def find_challenge(modules, module_id, challenge_id):
    module = find_module(modules, module_id)
    if not module:
        return None, None

    challenge = next((c for c in module.get("challenges", []) if c["id"] == challenge_id), None)
    return module, challenge


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("role") != "admin":
            return redirect(url_for("dashboard"))
        return fn(*args, **kwargs)
    return wrapper


def get_user(username, password):
    for user in USERS:
        if user["username"] == username and user["password"] == password:
            return user
    return None


def enabled_modules_for(team_id):
    conn = db()
    rows = conn.execute(
        "SELECT module_id, enabled FROM module_state WHERE team_id = ?",
        (team_id,),
    ).fetchall()
    conn.close()
    return {row["module_id"]: bool(row["enabled"]) for row in rows}


def submissions_for(team_id):
    conn = db()
    rows = conn.execute(
        "SELECT * FROM submissions WHERE team_id = ? ORDER BY created_at DESC",
        (team_id,),
    ).fetchall()
    conn.close()
    return rows


def build_damage_state(enabled_modules, solved_modules):
    enabled_ids = {module_id for module_id, is_enabled in enabled_modules.items() if is_enabled}
    pending = max(0, len(enabled_ids - solved_modules))
    damaged = SHIP_COMPONENT_ORDER[:pending]
    integrity = max(0, 100 - pending * 25)
    return damaged, integrity


def build_team_view(team):
    enabled = enabled_modules_for(team["id"])
    modules = get_modules()

    conn = db()
    solved_rows = conn.execute(
        """
        SELECT DISTINCT module_id, challenge_id
        FROM submissions
        WHERE team_id = ? AND is_correct = 1
        """,
        (team["id"],),
    ).fetchall()
    conn.close()

    solved_pairs = {(row["module_id"], row["challenge_id"]) for row in solved_rows}
    solved_modules = {row["module_id"] for row in solved_rows}

    score = 0
    for module in modules:
        for challenge in module.get("challenges", []):
            if (module["id"], challenge["id"]) in solved_pairs:
                score += int(challenge.get("points", module.get("points", 0)) or 0)

    damaged, integrity = build_damage_state(enabled, solved_modules)

    return {
        **team,
        "enabled_modules": enabled,
        "solved_modules": solved_modules,
        "solved_challenges": solved_pairs,
        "score": score,
        "solved_count": len(solved_pairs),
        "integrity": integrity,
        "damaged": damaged,
    }


@app.context_processor
def inject_globals():
    return {"current_user": session.get("user")}


@app.route("/")
def home():
    teams = [build_team_view(team) for team in TEAMS]
    teams.sort(key=lambda t: (-t["score"], -t["solved_count"], t["name"]))

    return render_template(
        "index.html",
        teams=teams,
        modules=get_modules(),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = get_user(username, password)

        if user:
            session["user"] = {
                "username": user["username"],
                "role": user["role"],
                "team_id": user["team_id"],
                "display_name": user["display_name"],
            }
            return redirect(url_for("dashboard"))

        flash("Credenziali non valide.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = session["user"]
    modules = get_modules()

    if user["role"] == "admin":
        teams = [build_team_view(team) for team in TEAMS]
        teams.sort(key=lambda t: (-t["score"], -t["solved_count"], t["name"]))
        return render_template("admin_dashboard.html", teams=teams, modules=modules)

    team = next((team for team in TEAMS if team["id"] == user.get("team_id")), None)
    if team is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("team_dashboard.html", team=build_team_view(team), modules=modules)


@app.route("/admin/module-toggle", methods=["POST"])
@login_required
@admin_required
def module_toggle():
    team_id = request.form.get("team_id")
    module_id = request.form.get("module_id")
    enabled = 1 if request.form.get("enabled") == "1" else 0

    conn = db()
    conn.execute(
        """
        UPDATE module_state
        SET enabled = ?
        WHERE team_id = ? AND module_id = ?
        """,
        (enabled, team_id, module_id),
    )
    conn.commit()
    conn.close()

    flash("Stato modulo aggiornato.", "ok")
    return redirect(url_for("dashboard"))


@app.route("/submit-flag", methods=["POST"])
@login_required
def submit_flag():
    user = session["user"]
    if user.get("role") != "team":
        return redirect(url_for("dashboard"))

    team_id = user.get("team_id")
    module_id = (request.form.get("module_id") or "").strip()
    challenge_id = (request.form.get("challenge_id") or "").strip()
    submitted_flag = (request.form.get("submitted_flag") or "").strip()

    if not team_id or not module_id or not challenge_id or not submitted_flag:
        flash("Dati invio incompleti.", "error")
        return redirect(url_for("dashboard"))

    module_enabled = enabled_modules_for(team_id).get(module_id, False)
    if not module_enabled:
        flash("Modulo non attivo per il tuo gruppo.", "error")
        return redirect(url_for("dashboard"))

    modules = get_modules()
    module, challenge = find_challenge(modules, module_id, challenge_id)

    if not module or not challenge:
        flash("Challenge non trovata.", "error")
        return redirect(url_for("dashboard"))

    expected = (challenge.get("expected_flag") or "").strip()
    if not expected:
        flash("Flag attesa non configurata per questa challenge.", "error")
        return redirect(url_for("dashboard"))

    is_correct = 1 if submitted_flag.strip() == expected.strip() else 0

    conn = db()
    existing = conn.execute(
        """
        SELECT 1
        FROM submissions
        WHERE team_id = ? AND module_id = ? AND challenge_id = ? AND is_correct = 1
        LIMIT 1
        """,
        (team_id, module_id, challenge_id),
    ).fetchone()

    if existing and is_correct:
        conn.close()
        flash("Challenge già completata.", "error")
        return redirect(url_for("dashboard"))

    conn.execute(
        """
        INSERT INTO submissions (team_id, module_id, challenge_id, submitted_flag, is_correct)
        VALUES (?, ?, ?, ?, ?)
        """,
        (team_id, module_id, challenge_id, submitted_flag, is_correct),
    )
    conn.commit()
    conn.close()

    flash("Flag corretta." if is_correct else "Flag errata.", "ok" if is_correct else "error")
    return redirect(url_for("dashboard"))


@app.route("/inspect/<team_id>")
@login_required
def inspect_team(team_id):
    user = session.get("user", {})
    if user.get("role") != "admin" and user.get("team_id") != team_id:
        abort(403)

    team = next((t for t in TEAMS if t["id"] == team_id), None)
    if not team:
        abort(404)

    return render_template("inspect.html", team=build_team_view(team), modules=get_modules())


@app.route("/scoreboard")
def scoreboard():
    teams = [build_team_view(team) for team in TEAMS]
    teams.sort(key=lambda t: (-t["score"], -t["solved_count"], t["name"]))
    return render_template("scoreboard.html", teams=teams, modules=get_modules())


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)