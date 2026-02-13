# launcher.py
from flask import Flask, jsonify
import subprocess
import os
import sys

app = Flask(__name__)

# ------------------------------------------------
# 현재 venv Python 경로
# launcher.py와 같은 venv에서 실행되므로 sys.executable 사용
# ------------------------------------------------
VENVPYTHON = sys.executable
MAIN_PATH = os.path.join(os.path.dirname(__file__), "main.py")
MAIN_PROC = None  # main.py 프로세스 저장

# -------------------
# Start main.py
# -------------------
@app.route("/start", methods=["POST"])
def start():
    global MAIN_PROC
    if MAIN_PROC is None or MAIN_PROC.poll() is not None:
        # venv Python으로 main.py 실행
        MAIN_PROC = subprocess.Popen([VENVPYTHON, MAIN_PATH])
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already running"})

# -------------------
# Stop main.py
# -------------------
@app.route("/stop", methods=["POST"])
def stop():
    global MAIN_PROC
    if MAIN_PROC is not None and MAIN_PROC.poll() is None:
        MAIN_PROC.terminate()
        MAIN_PROC = None
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not running"})

# -------------------
# Status
# -------------------
@app.route("/status", methods=["GET"])
def status():
    global MAIN_PROC
    if MAIN_PROC is not None and MAIN_PROC.poll() is None:
        return jsonify({"status": "running"})
    else:
        return jsonify({"status": "stopped"})

if __name__ == "__main__":
    print("🚀 Launcher running on http://127.0.0.1:5050")
    app.run(port=5050)