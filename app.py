import os
import requests
import hashlib
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "changeme")
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "png", "jpg", "jpeg", "txt", "zip", "doc", "docx"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

VT_API_KEY = os.getenv("VT_API_KEY")
VT_UPLOAD_URL = "https://www.virustotal.com/api/v3/files"
VT_ANALYSIS_URL = "https://www.virustotal.com/api/v3/analyses/"

# Utility

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

# Routes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            flash("No file selected.", "warning")
            return redirect(url_for("index"))

        if not allowed_file(file.filename):
            flash("Invalid file type.", "danger")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        headers = {"x-apikey": VT_API_KEY}
        with open(filepath, "rb") as f:
            response = requests.post(VT_UPLOAD_URL, files={"file": f}, headers=headers)

        if response.status_code != 200:
            flash("Failed to upload file to VirusTotal.", "danger")
            return redirect(url_for("index"))

        analysis_id = response.json().get("data", {}).get("id")
        if not analysis_id:
            flash("Error retrieving analysis ID.", "danger")
            return redirect(url_for("index"))

        analysis_url = f"{VT_ANALYSIS_URL}{analysis_id}"
        for _ in range(10):
            time.sleep(2)
            res = requests.get(analysis_url, headers=headers)
            if res.status_code == 200 and res.json()["data"]["attributes"]["status"] == "completed":
                session["scan"] = res.json()
                session["filename"] = filename
                session["hash"] = sha256_file(filepath)
                break
        else:
            flash("Analysis timed out.", "warning")
            return redirect(url_for("index"))

        os.remove(filepath)
        return redirect(url_for("results"))

    return render_template("index.html", allowed=app.config["ALLOWED_EXTENSIONS"])

@app.route("/results")
def results():
    if "scan" not in session:
        flash("No results found. Upload a file first.", "warning")
        return redirect(url_for("index"))

    return render_template("results.html", result=session["scan"], filename=session["filename"], filehash=session["hash"])

@app.errorhandler(413)
def file_too_large(error):
    flash("File too large. Max allowed size is 16MB.", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
