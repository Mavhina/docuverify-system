from flask import Blueprint, render_template, request, redirect, flash
import os
from werkzeug.utils import secure_filename
from .verifier import analyze_document
import os
print("Current working directory:", os.getcwd())


main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("document")
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join("uploads", filename)
            file.save(filepath)

            result = analyze_document(filepath)
            return render_template("result.html", result=result)

        flash("No file uploaded.")
        return redirect("/")
    return render_template("index.html")
