from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
import subprocess

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    endpoint = ""

    if request.method == "POST":
        endpoint = request.form.get("endpoint", "").strip()

        if endpoint:
            try:
                # VULNERABILITÀ INTENZIONALE CTF:
                # input utente concatenato in una shell command.
                cmd = f"ping -c 1 {endpoint}"
                completed = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                result = completed.stdout + completed.stderr
            except subprocess.TimeoutExpired:
                result = "[timeout] Command execution exceeded allowed time."
            except Exception as exc:
                result = f"[error] {exc}"

    return render_template("index.html", result=result, endpoint=endpoint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)