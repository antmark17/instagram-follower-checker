from flask import Flask, render_template, request, send_file, flash, redirect
import json
import io
import algorithm
import os
from dotenv import load_dotenv
import secrets
import logging
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = Flask(__name__)

# -------------------------------
# CONFIG DI BASE
# -------------------------------

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Limite 5MB

# SECRET KEY
secret = os.getenv("SECRET_KEY")
if not secret:
    secret = secrets.token_hex(32)
    print("⚠ Nessuna SECRET_KEY trovata nel .env → generata automaticamente!")
app.secret_key = secret

app.config["SESSION_COOKIE_HTTPONLY"] = True

logging.basicConfig(level=logging.INFO)

# CSRF
csrf = CSRFProtect(app)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[]
)

# -------------------------------
# HANDLER ERRORI
# -------------------------------

@app.errorhandler(RequestEntityTooLarge)
def file_troppo_grande(e):
    flash("Il file che hai caricato supera il limite massimo consentito (5MB).")
    return redirect("/")


# -------------------------------
# NO CACHE HEADERS
# -------------------------------

@app.after_request
def no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# -------------------------------
# VALIDAZIONE FILE JSON
# -------------------------------

def extract_href(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "href" and isinstance(value, str) and value.strip():
                return value
            found = extract_href(value)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = extract_href(item)
            if found:
                return found
    return None


def validate_followers_structure(file_stream):
    try:
        data = json.load(file_stream)
    except Exception as e:
        logging.error(f"Errore parsing followers.json: {e}")
        return False, "followers_1.json non è un file JSON valido o risulta corrotto."

    if not isinstance(data, list) or not data:
        return False, "followers_1.json risulta vuoto o non formattato correttamente."

    href = extract_href(data)

    if href:
        return True, ""

    logging.warning("Formato followers_1.json non riconosciuto: possibile modifica da parte di Instagram.")
    return False, (
        "Il formato di followers_1.json non è riconosciuto. "
        "Instagram potrebbe aver aggiornato la struttura del file."
    )


def validate_following_structure(file_stream):
    try:
        data = json.load(file_stream)
    except Exception as e:
        logging.error(f"Errore parsing following.json: {e}")
        return False, "following.json non è un file JSON valido o risulta corrotto."

    if not isinstance(data, dict):
        return False, "following.json ha una struttura non valida."

    href = extract_href(data)

    if href:
        return True, ""

    logging.warning("Formato following.json non riconosciuto: possibile modifica da parte di Instagram.")
    return False, (
        "Il formato di following.json non è riconosciuto. "
        "Instagram potrebbe aver aggiornato la struttura del file."
    )


# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/analizza", methods=["POST"])
@limiter.limit("10 per minuto")
def analizza():

    if "followers" not in request.files or "following" not in request.files:
        flash("Devi caricare entrambi i file richiesti (followers e following).")
        return redirect("/")

    followers_file = request.files["followers"]
    following_file = request.files["following"]

    if followers_file.filename == "" or following_file.filename == "":
        flash("Assicurati di caricare entrambi i file JSON richiesti.")
        return redirect("/")

    followers_name = secure_filename(followers_file.filename)
    following_name = secure_filename(following_file.filename)

    if not followers_name.lower().endswith(".json"):
        flash("Il file followers deve essere in formato .json.")
        return redirect("/")

    if not following_name.lower().endswith(".json"):
        flash("Il file following deve essere in formato .json.")
        return redirect("/")

    followers_bytes = followers_file.read()
    following_bytes = following_file.read()

    if not followers_bytes or not following_bytes:
        flash("Uno dei file risulta vuoto.")
        return redirect("/")

    if b"\x00" in followers_bytes[:200] or b"\x00" in following_bytes[:200]:
        flash("Uno dei file sembra corrotto o non è un vero JSON.")
        return redirect("/")

    ok, msg = validate_followers_structure(io.BytesIO(followers_bytes))
    if not ok:
        flash(msg)
        return redirect("/")

    ok, msg = validate_following_structure(io.BytesIO(following_bytes))
    if not ok:
        flash(msg)
        return redirect("/")

    utenti = algorithm.analyze(
        io.BytesIO(followers_bytes),
        io.BytesIO(following_bytes)
    )

    result_text = "\n".join(utenti)

    return render_template("result.html", utenti=utenti, raw_result=result_text)


@app.route("/download", methods=["POST"])
@limiter.limit("30 per minuto")
def download():
    result_text = request.form.get("raw_result", "")

    buffer = io.BytesIO(result_text.encode("utf-8"))
    buffer.seek(0)

    filename = f"Result_{secrets.token_hex(4)}.txt"

    return send_file(
        buffer,
        mimetype="text/plain",
        as_attachment=True,
        download_name=filename
    )


@app.route("/info")
def info():
    return render_template("info.html")


if __name__ == "__main__":
    app.run(debug=True)
