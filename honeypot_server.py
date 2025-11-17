from flask import Flask, request
import os
import time
import orjson
from pathlib import Path

app = Flask(__name__)

LOG_DIR = Path("/root/llm-honeypot/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "honeypot.jsonl"


def write_json_log(attacker_ip, method, path, data, is_ai):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "src_ip": attacker_ip,
        "eventid": "cowrie.command.input",
        "method": method,
        "path": path,
        "input": data,
        "ai_attack": is_ai          # ⭐ ADD THIS ⭐
    }

    with open(LOG_FILE, "ab") as f:
        f.write(orjson.dumps(log_entry))
        f.write(b"\n")

    print("[LOG]", log_entry)


@app.route("/", methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path="root"):
    attacker_ip = request.remote_addr
    method = request.method

    data = request.args.to_dict() if method == "GET" else request.form.to_dict()

    # ⭐ Detect AI attack parameter
    ai_flag = request.args.get("ai_attack", "false").lower() == "true"

    write_json_log(attacker_ip, method, path, data, ai_flag)

    return "Honeypot Active", 200


if __name__ == "__main__":
    print("🚀 Honeypot running on http://localhost:8080")
    app.run(host="0.0.0.0", port=8080)
