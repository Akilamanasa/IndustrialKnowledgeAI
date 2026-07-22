from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from ai.pdf_reader import extract_text
from ai.gemini import ask_gemini

app = Flask(__name__)
app.secret_key = "hackathon-secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        file = request.files.get("document")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            pdf_text = extract_text(filepath)

            session["document_text"] = pdf_text

            # Clear previous results
            session.pop("answer", None)
            session.pop("search_results", None)
            session.pop("insights", None)

            flash(f"{filename} uploaded successfully!")

        return redirect(url_for("home"))

    return render_template(
        "index.html",
        answer=session.get("answer"),
        search_results=session.get("search_results"),
        insights=session.get("insights")
    )


# ---------------- AI CHAT ----------------
@app.route("/ask", methods=["POST"])
def ask():

    question = request.form.get("question")
    document_text = session.get("document_text", "")

    if not document_text:
        flash("Please upload a PDF first.")
        return redirect(url_for("home"))

    answer = ask_gemini(document_text, question)

    session["answer"] = answer

    return render_template(
        "index.html",
        answer=session.get("answer"),
        search_results=session.get("search_results"),
        insights=session.get("insights")
    )


# ---------------- SMART SEARCH ----------------
@app.route("/search", methods=["POST"])
def search():

    keyword = request.form.get("keyword", "").strip().lower()
    document = session.get("document_text", "")

    if not document:
        flash("Please upload a PDF first.")
        return redirect(url_for("home"))

    lines = document.split("\n")
    results = []

    for i, line in enumerate(lines):
        if keyword in line.lower():
            results.append(f"Line {i+1}: {line}")

    if results:
        result_text = "\n\n".join(results)
    else:
        result_text = "No matching results found."

    session["search_results"] = result_text

    return render_template(
        "index.html",
        answer=session.get("answer"),
        search_results=session.get("search_results"),
        insights=session.get("insights")
    )


# ---------------- KNOWLEDGE INSIGHTS ----------------
@app.route("/insights", methods=["POST"])
def insights():

    document_text = session.get("document_text", "")

    if not document_text:
        flash("Please upload a PDF first.")
        return redirect(url_for("home"))

    prompt = f"""
Analyze the uploaded document and return ONLY HTML.

Use this format:

<h3>📄 Summary</h3>
<p>...</p>

<h3>⭐ Key Points</h3>
<ul>
<li>...</li>
</ul>

<h3>⚠ Risks</h3>
<ul>
<li>...</li>
</ul>

<h3>✅ Recommendations</h3>
<ul>
<li>...</li>
</ul>

Document:

{document_text}
"""

    insights = ask_gemini("", prompt)

    session["insights"] = insights

    return render_template(
        "index.html",
        answer=session.get("answer"),
        search_results=session.get("search_results"),
        insights=session.get("insights")
    )


if __name__ == "__main__":
    app.run(debug=True)