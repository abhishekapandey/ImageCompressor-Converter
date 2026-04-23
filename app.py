#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, render_template, request, send_file
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_size_kb(path):
    return os.path.getsize(path) / 1024


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    file = request.files["image"]
    target_kb = int(request.form["target_kb"])
    action = request.form["action"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    original_size = get_size_kb(path)

    img = Image.open(path)

    output_path = os.path.join(UPLOAD_FOLDER, "output.jpg")

    if action == "pdf":
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        output_pdf = os.path.join(UPLOAD_FOLDER, "output.pdf")
        img.save(output_pdf, "PDF")

        return send_file(output_pdf, as_attachment=True)

    # ---------- Compression ----------
    img = img.convert("RGB")
    w, h = img.size

    final_size = None

    for scale in [1, 0.8, 0.6, 0.4, 0.3]:
        resized = img.resize((int(w * scale), int(h * scale)))

        low, high = 5, 95
        best = 10

        while low <= high:
            mid = (low + high) // 2
            resized.save(output_path, "JPEG", quality=mid, optimize=True)

            size = get_size_kb(output_path)

            if size > target_kb:
                high = mid - 1
            else:
                best = mid
                low = mid + 1

        resized.save(output_path, "JPEG", quality=best, optimize=True)
        final_size = get_size_kb(output_path)

        if final_size <= target_kb:
            break

    return render_template(
        "index.html",
        original=f"{original_size:.2f}",
        compressed=f"{final_size:.2f}",
        file="output.jpg"
    )


if __name__ == "__main__":
    app.run(debug=True)

