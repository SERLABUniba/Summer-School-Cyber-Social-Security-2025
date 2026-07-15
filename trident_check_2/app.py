from flask import Flask, render_template, request
import subprocess
from werkzeug.middleware.proxy_fix import ProxyFix


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
                cmd = f"ping -c 1 {endpoint}"
                completed = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if completed.returncode == 0:
                    result = "Communications OK"
                else:
                    result = "Communications failure"

            except subprocess.TimeoutExpired:
                result = "Communications timeout"
            except Exception:
                result = "Communications failure"

    return render_template("index.html", result=result, endpoint=endpoint)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)