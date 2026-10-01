from flask import Flask, render_template, request, jsonify
from translator import Translator
import time


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# LOAD TRANSLATOR ONCE
# =========================================================

try:
    translator = Translator()

    print("=" * 60)
    print("HAUSATRANSLATORAI")
    print("=" * 60)

    print(
        f"Loaded {translator.get_dataset_size():,} "
        "English-Hausa translations."
    )

    print()
    print("Web application starting...")
    print("Open your browser at:")
    print("http://127.0.0.1:5000")
    print()
    print("Press CTRL+C to stop the server.")
    print("=" * 60)


except Exception as error:

    print("ERROR loading translator:")
    print(error)

    translator = None


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    dataset_size = 0

    if translator:
        dataset_size = translator.get_dataset_size()

    return render_template(
        "index.html",
        dataset_size=dataset_size
    )


# =========================================================
# TRANSLATION API
# =========================================================

@app.route("/translate", methods=["POST"])
def translate():

    if translator is None:

        return jsonify({
            "translation": "",
            "status": "Translation engine is unavailable.",
            "time": 0
        }), 500


    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({
            "translation": "",
            "status": "No input received.",
            "time": 0
        }), 400


    text = data.get(
        "text",
        ""
    )


    if not isinstance(text, str):

        return jsonify({
            "translation": "",
            "status": "Invalid input.",
            "time": 0
        }), 400


    text = text.strip()


    if not text:

        return jsonify({
            "translation": "",
            "status": "Please enter English text.",
            "time": 0
        }), 400


    # =====================================================
    # TRANSLATE
    # =====================================================

    start_time = time.perf_counter()


    result = translator.translate_paragraph(
        text
    )


    elapsed = (
        time.perf_counter()
        - start_time
    )


    # =====================================================
    # STATUS MESSAGE
    # =====================================================

    total = result["total_sentences"]

    translated = result[
        "translated_sentences"
    ]

    not_found = result[
        "not_found_sentences"
    ]

    coverage = result[
        "coverage"
    ]


    if not_found == 0:

        status = (
            "✓ Translation completed successfully."
        )

    elif translated > 0:

        status = (
            "⚠ Translation completed with "
            f"{not_found} untranslated sentence(s)."
        )

    else:

        status = (
            "⚠ No matching translation was found."
        )


    # =====================================================
    # RESPONSE
    # =====================================================

    return jsonify({

        "translation":
            result["translation"],

        "status":
            status,

        "total_sentences":
            total,

        "translated_sentences":
            translated,

        "not_found_sentences":
            not_found,

        "coverage":
            coverage,

        "time":
            elapsed,

        "not_found":
            result["not_found"]

    })


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )