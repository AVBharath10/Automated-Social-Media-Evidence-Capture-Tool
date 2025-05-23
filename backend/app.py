from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import sys

app = Flask(__name__)
CORS(app)

OUTPUT_FOLDER = "output"
PLATFORM_SCRIPTS = {
    "instagram": "insta_viewer.py",
    "twitter": "twitter_viewer.py"
}

@app.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.get_json()
    platform = data.get("platform")  # "instagram" or "twitter"
    username = data.get("username")
    password = data.get("password")

    if platform not in PLATFORM_SCRIPTS:
        return jsonify({"error": "Unsupported platform"}), 400
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    script = PLATFORM_SCRIPTS[platform]

    try:
        result = subprocess.run(
            [sys.executable, script, username, password],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        pdf_name = f"{platform.capitalize()}_Report.pdf"
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_name)

        if os.path.exists(pdf_path):
            return jsonify({"pdf_url": f"http://localhost:5000/output/{pdf_name}"}), 200
        else:
            return jsonify({"error": "PDF not generated"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    app.run(debug=True, port=5000)
