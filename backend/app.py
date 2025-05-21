from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import sys

app = Flask(__name__)
CORS(app)

OUTPUT_FOLDER = "output"

@app.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        # Use sys.executable to call the right python interpreter
        result = subprocess.run(
            [sys.executable, "insta_viewer.py", username, password],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        pdf_path = os.path.join(OUTPUT_FOLDER, "Instagram_Report.pdf")
        if os.path.exists(pdf_path):
            return jsonify({"pdf_url": f"http://localhost:5000/output/Instagram_Report.pdf"}), 200
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
