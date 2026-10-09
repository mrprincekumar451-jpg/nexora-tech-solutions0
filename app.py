
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import io
import qrcode
from urllib.parse import quote
from flask import send_file

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "nexora-dev-secret-change-before-deployment"
)

COMPANY_NAME = "NEXORA TECH SOLUTIONS"


@app.context_processor
def inject_company():
    return {"company_name": COMPANY_NAME}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/skills")
def skills():
    return render_template("skills.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please complete all fields.", "error")
            return redirect(url_for("contact"))

        # Replace with your real WhatsApp number, including country code.
        whatsapp_number = os.environ.get("WHATSAPP_NUMBER", "7081489690")

        if not whatsapp_number.isdigit():
            flash("Please configure the WhatsApp number first.", "error")
            return redirect(url_for("contact"))

        text = (
            f"Hello {COMPANY_NAME}!\n"
            f"Name: {name}\nEmail: {email}\nMessage: {message}"
        )
        return redirect(
            f"https://wa.me/{whatsapp_number}?text={quote(text)}"
        )

    return render_template("contact.html")


@app.route("/qr")
def qr_code():
    website_url = os.environ.get(
        "PUBLIC_URL", request.url_root
    ).rstrip("/")

    qr = qrcode.make(website_url)
    image_bytes = io.BytesIO()
    qr.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return send_file(image_bytes, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)