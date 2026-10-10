
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    Response
)
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

PUBLIC_URL = os.environ.get(
    "PUBLIC_URL",
    "https://nexora-tech-solutions0.onrender.com"
).rstrip("/")


# Share company information with templates
@app.context_processor
def inject_company():
    return {"company_name": COMPANY_NAME}


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# About page
@app.route("/about")
def about():
    return render_template("about.html")


# Services page
@app.route("/services")
def services():
    return render_template("services.html")


# Skills page
@app.route("/skills")
def skills():
    return render_template("skills.html")


# Contact, Feedback and Rating
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

        # Validate input lengths
        if len(name) > 100 or len(email) > 254 or len(message) > 3000:
            flash("One or more fields exceed the allowed length.", "error")
            return redirect(url_for("contact"))

        # Basic email validation
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("contact"))

        # Validate star rating
        if rating not in {"1", "2", "3", "4", "5"}:
            flash("Please select a valid rating.", "error")
            return redirect(url_for("contact"))

        # WhatsApp number must include country code, digits only
        whatsapp_number = os.environ.get(
            "WHATSAPP_NUMBER",
            "917081489690"
        )
        whatsapp_number = re.sub(r"[\s+\-()]", "", whatsapp_number)

        if not whatsapp_number.isdigit():
            flash(
                "Please configure the WhatsApp number correctly.",
                "error"
            )
            return redirect(url_for("contact"))

        stars = "★" * int(rating) + "☆" * (5 - int(rating))

        # Prepare WhatsApp message
        whatsapp_message = (
            f"Hello {COMPANY_NAME}!\n\n"
            f"New Contact / Feedback\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Rating: {stars} ({rating}/5)\n"
            f"Message / Feedback: {message}\n\n"
            f"Received through the company website."
        )

        whatsapp_url = (
            f"https://wa.me/{whatsapp_number}"
            f"?text={quote(whatsapp_message)}"
        )

        return redirect(whatsapp_url)

    return render_template("contact.html")


# Website QR Code
@app.route("/qr")
def qr_code():

    qr = qrcode.make(PUBLIC_URL)

    image_bytes = io.BytesIO()
    qr.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return send_file(
        image_bytes,
        mimetype="image/png",
        download_name="nexora-website-qr.png"
    )


# XML Sitemap for search engines
@app.route("/sitemap.xml")
def sitemap():

    pages = [
        "",
        "/about",
        "/services",
        "/skills",
        "/contact"
    ]

    urls = "".join(
        f"<url><loc>{PUBLIC_URL}{page}</loc></url>"
        for page in pages
    )

    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}"
        "</urlset>"
    )

    return Response(
        sitemap_xml,
        mimetype="application/xml"
    )


if __name__ == "__main__":
    app.run(debug=True)
