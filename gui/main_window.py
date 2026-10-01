import customtkinter as ctk
import time
from translator import Translator


class TranslatorGUI(ctk.CTk):
    """Main English-to-Hausa Translator application."""

    def __init__(self):
        super().__init__()

        # -----------------------------
        # Window configuration
        # -----------------------------
        self.title("English → Hausa Translator")
        self.geometry("1000x700")
        self.minsize(850, 600)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # -----------------------------
        # Load translation engine
        # -----------------------------
        try:
            self.translator = Translator()
            self.dataset_size = self.translator.get_dataset_size()
            self.load_error = None

        except Exception as error:
            self.translator = None
            self.dataset_size = 0
            self.load_error = str(error)

        # Translation history
        self.history = []

        self.create_interface()

    # =========================================================
    # CREATE INTERFACE
    # =========================================================

    def create_interface(self):

        # Main container
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=0
        )
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # -----------------------------
        # Header
        # -----------------------------

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="ENGLISH ↔ HAUSA TRANSLATOR",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )
        self.title_label.pack(pady=(25, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Offline English–Hausa Translation System",
            font=ctk.CTkFont(size=15)
        )
        self.subtitle_label.pack(pady=(0, 20))

        # -----------------------------
        # English label
        # -----------------------------

        self.english_label = ctk.CTkLabel(
            self.main_frame,
            text="English Input",
            anchor="w",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            )
        )
        self.english_label.pack(
            fill="x",
            padx=35,
            pady=(5, 5)
        )

        # -----------------------------
        # English text box
        # -----------------------------

        self.english_text = ctk.CTkTextbox(
            self.main_frame,
            height=150,
            font=ctk.CTkFont(size=16),
            wrap="word"
        )
        self.english_text.pack(
            fill="x",
            padx=35,
            pady=(0, 15)
        )

        # -----------------------------
        # Translate button
        # -----------------------------

        self.translate_button = ctk.CTkButton(
            self.main_frame,
            text="TRANSLATE",
            height=45,
            width=180,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            command=self.translate_text
        )
        self.translate_button.pack(
            pady=(0, 20)
        )

        # -----------------------------
        # Hausa label
        # -----------------------------

        self.hausa_label = ctk.CTkLabel(
            self.main_frame,
            text="Hausa Translation",
            anchor="w",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            )
        )
        self.hausa_label.pack(
            fill="x",
            padx=35,
            pady=(0, 5)
        )

        # -----------------------------
        # Hausa output
        # -----------------------------

        self.hausa_text = ctk.CTkTextbox(
            self.main_frame,
            height=150,
            font=ctk.CTkFont(size=16),
            wrap="word"
        )
        self.hausa_text.pack(
            fill="x",
            padx=35,
            pady=(0, 15)
        )

        self.hausa_text.configure(
            state="disabled"
        )

        # -----------------------------
        # Status
        # -----------------------------

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready",
            anchor="w",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(
            fill="x",
            padx=35,
            pady=(0, 5)
        )

        # -----------------------------
        # Translation time
        # -----------------------------

        self.time_label = ctk.CTkLabel(
            self.main_frame,
            text="Translation time: --",
            anchor="w",
            font=ctk.CTkFont(size=13)
        )
        self.time_label.pack(
            fill="x",
            padx=35
        )

        # -----------------------------
        # Buttons
        # -----------------------------

        self.button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.button_frame.pack(
            pady=15
        )

        self.copy_button = ctk.CTkButton(
            self.button_frame,
            text="Copy",
            width=120,
            command=self.copy_translation
        )
        self.copy_button.grid(
            row=0,
            column=0,
            padx=8
        )

        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="Clear",
            width=120,
            command=self.clear_text
        )
        self.clear_button.grid(
            row=0,
            column=1,
            padx=8
        )

        # -----------------------------
        # Dataset information
        # -----------------------------

        self.dataset_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Translation database: {self.dataset_size:,} sentence pairs",
            font=ctk.CTkFont(size=13)
        )
        self.dataset_label.pack(
            pady=(5, 10)
        )

        # -----------------------------
        # Keyboard shortcuts
        # -----------------------------

        self.bind(
            "<Control-Return>",
            lambda event: self.translate_text()
        )

    # =========================================================
    # TRANSLATION
    # =========================================================

    def translate_text(self):

        english = self.english_text.get(
            "1.0",
            "end"
        ).strip()

        if not english:
            self.set_status(
                "Please enter an English sentence.",
                "warning"
            )
            return

        if self.translator is None:
            self.set_status(
                "Dataset could not be loaded.",
                "error"
            )

            self.set_output(
                f"Error: {self.load_error}"
            )

            return

        start_time = time.perf_counter()

        # -------------------------------------------------
        # First try the complete input.
        # -------------------------------------------------

        translation = self.translator.translate(
            english
        )

        # -------------------------------------------------
        # If the complete input is not found,
        # try paragraph/sentence-by-sentence translation.
        # -------------------------------------------------

        if translation:

            output = translation

            status = "✓ Exact translation found"

        else:

            output, translated_count, total_count = (
                self.translate_paragraph(english)
            )

            if translated_count == total_count:

                status = (
                    f"✓ Paragraph translated "
                    f"({total_count} sentences)"
                )

            elif translated_count > 0:

                status = (
                    f"⚠ Partial translation: "
                    f"{translated_count}/{total_count} "
                    f"sentences found"
                )

            else:

                status = "⚠ Translation not found"

        end_time = time.perf_counter()

        elapsed = end_time - start_time

        self.set_output(output)

        self.set_status(
            status,
            "success" if translation else "warning"
        )

        self.time_label.configure(
            text=f"Translation time: {elapsed:.6f} seconds"
        )

        # Save history
        self.history.append({
            "english": english,
            "hausa": output,
            "time": elapsed
        })

    # =========================================================
    # PARAGRAPH TRANSLATION
    # =========================================================

    def translate_paragraph(self, text):

        import re

        # Split text into sentences while preserving punctuation.
        sentences = re.split(
            r"(?<=[.!?])\s+",
            text.strip()
        )

        # Remove empty entries
        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        translated_sentences = []

        translated_count = 0

        for sentence in sentences:

            translation = self.translator.translate(
                sentence
            )

            if translation:

                translated_sentences.append(
                    translation
                )

                translated_count += 1

            else:

                # Keep unknown sentence visible.
                translated_sentences.append(
                    f"[Translation not found: {sentence}]"
                )

        return (
            " ".join(translated_sentences),
            translated_count,
            len(sentences)
        )

    # =========================================================
    # OUTPUT
    # =========================================================

    def set_output(self, text):

        self.hausa_text.configure(
            state="normal"
        )

        self.hausa_text.delete(
            "1.0",
            "end"
        )

        self.hausa_text.insert(
            "1.0",
            text
        )

        self.hausa_text.configure(
            state="disabled"
        )

    # =========================================================
    # STATUS
    # =========================================================

    def set_status(self, text, status_type="normal"):

        self.status_label.configure(
            text=text
        )

    # =========================================================
    # COPY
    # =========================================================

    def copy_translation(self):

        translation = self.hausa_text.get(
            "1.0",
            "end"
        ).strip()

        if not translation:

            self.set_status(
                "Nothing to copy.",
                "warning"
            )

            return

        self.clipboard_clear()

        self.clipboard_append(
            translation
        )

        self.update()

        self.set_status(
            "✓ Translation copied to clipboard.",
            "success"
        )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear_text(self):

        self.english_text.delete(
            "1.0",
            "end"
        )

        self.hausa_text.configure(
            state="normal"
        )

        self.hausa_text.delete(
            "1.0",
            "end"
        )

        self.hausa_text.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="Ready"
        )

        self.time_label.configure(
            text="Translation time: --"
        )

        self.english_text.focus()


# =============================================================
# RUN APPLICATION
# =============================================================

if __name__ == "__main__":

    app = TranslatorGUI()

    app.mainloop()