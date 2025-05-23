from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route("/download-report", methods=["GET"])
def download_report():
    file_path = os.path.join("output", "Instagram_Report.pdf")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "Report not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # different port to avoid conflicts
  