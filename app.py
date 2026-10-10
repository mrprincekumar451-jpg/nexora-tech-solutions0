
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import io
import re
import qrcode
from urllib.parse import quote

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "nexora-dev-secret-change-before-deployment"
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
        rating = request.form.get("rating", "").strip()

        # Validate required fields
        if not name or not email or not message or not rating:
            flash(
                "Please complete all fields and select a rating.",
                "error"
            )
            return redirect(url_for("contact"))

        # Basic email validation
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("contact"))

        # Validate rating
        if rating not in {"1", "2", "3", "4", "5"}:
            flash("Please select a valid rating.", "error")
            return redirect(url_for("contact"))

        # Get WhatsApp number from Render environment variables
        whatsapp_number = os.environ.get(
            "WHATSAPP_NUMBER",
            "917081489690"
        )

        # Remove an optional leading plus or spaces
        whatsapp_number = re.sub(r"[\s+\-()]", "", whatsapp_number)

        if not whatsapp_number.isdigit():
            flash(
                "WhatsApp number is not configured correctly.",
                "error"
            )
            return redirect(url_for("contact"))

        stars = "★" * int(rating) + "☆" * (5 - int(rating))

        # Build WhatsApp message
        text = (
            f"Hello {COMPANY_NAME}!\n\n"
            f"New Contact / Feedback Received\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Rating: {stars} ({rating}/5)\n"
            f"Message / Feedback: {message}\n\n"
            f"Received through the company website."
        )

        whatsapp_url = (
            f"https://wa.me/{whatsapp_number}"
            f"?text={quote(text)}"
        )

        return redirect(whatsapp_url)

    return render_template("contact.html")


@app.route("/qr")
def qr_code():

    website_url = os.environ.get(
        "PUBLIC_URL",
        request.url_root
    ).rstrip("/")

    qr = qrcode.make(website_url)

    image_bytes = io.BytesIO()
    qr.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return send_file(
        image_bytes,
        mimetype="image/png",
        download_name="nexora-website-qr.png"
    )


if __name__ == "__main__":
    app.run(debug=True)
