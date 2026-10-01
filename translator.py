import csv
import os
import re
import time


class Translator:
    """
    English-to-Hausa translation engine.

    Dataset format:
        English,Hausa

    Features:
        - Exact sentence matching
        - Text normalization
        - Paragraph translation
        - Sentence-by-sentence processing
        - Translation coverage statistics
    """

    def __init__(self, dataset_path="dataset/master_dataset.csv"):
        self.dataset_path = dataset_path
        self.translations = {}

        self.load_dataset()

    # =========================================================
    # TEXT NORMALIZATION
    # =========================================================

    def normalize(self, text):
        """
        Normalize text so that small differences in formatting
        do not prevent a translation from being found.
        """

        if not isinstance(text, str):
            return ""

        text = text.strip()

        # Replace multiple spaces with one space
        text = re.sub(r"\s+", " ", text)

        # Normalize common quotation marks
        text = text.replace("“", '"')
        text = text.replace("”", '"')
        text = text.replace("‘", "'")
        text = text.replace("’", "'")

        # Remove unnecessary space before punctuation
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)

        # Case-insensitive matching
        text = text.casefold()

        return text

    # =========================================================
    # LOAD DATASET
    # =========================================================

    def load_dataset(self):
        """
        Load English-Hausa translations from CSV.
        """

        if not os.path.exists(self.dataset_path):

            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_path}"
            )

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            required_columns = {"English", "Hausa"}

            if not required_columns.issubset(
                reader.fieldnames or []
            ):

                raise ValueError(
                    "The dataset must contain these columns: "
                    "English,Hausa"
                )

            for row in reader:

                english = (
                    row.get("English", "")
                    .strip()
                )

                hausa = (
                    row.get("Hausa", "")
                    .strip()
                )

                if not english or not hausa:
                    continue

                normalized_english = (
                    self.normalize(english)
                )

                self.translations[
                    normalized_english
                ] = hausa

    # =========================================================
    # SINGLE SENTENCE TRANSLATION
    # =========================================================

    def translate(self, text):
        """
        Translate one English sentence.
        """

        normalized_text = self.normalize(text)

        if not normalized_text:
            return None

        # -----------------------------------------
        # First: exact match
        # -----------------------------------------

        translation = self.translations.get(
            normalized_text
        )

        if translation:
            return translation

        # -----------------------------------------
        # Second: try without final punctuation
        # -----------------------------------------

        without_punctuation = re.sub(
            r"[.!?]+$",
            "",
            normalized_text
        ).strip()

        if without_punctuation:

            for key, value in self.translations.items():

                key_without_punctuation = re.sub(
                    r"[.!?]+$",
                    "",
                    key
                ).strip()

                if (
                    key_without_punctuation
                    == without_punctuation
                ):

                    return value

        return None

    # =========================================================
    # SENTENCE SPLITTING
    # =========================================================

    def split_sentences(self, text):
        """
        Split a paragraph into individual sentences.

        Example:

        Hello. How are you?

        becomes:

        [
            "Hello.",
            "How are you?"
        ]
        """

        if not isinstance(text, str):
            return []

        text = text.strip()

        if not text:
            return []

        # Split after ., ! or ?
        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    # =========================================================
    # PARAGRAPH TRANSLATION
    # =========================================================

    def translate_paragraph(self, text):
        """
        Translate a complete paragraph sentence by sentence.
        """

        start_time = time.perf_counter()

        sentences = self.split_sentences(text)

        translated_sentences = []

        translated_count = 0
        not_found_count = 0

        not_found_sentences = []

        for sentence in sentences:

            translation = self.translate(
                sentence
            )

            if translation:

                translated_sentences.append(
                    translation
                )

                translated_count += 1

            else:

                # Keep the paragraph readable.
                translated_sentences.append(
                    sentence
                )

                not_found_count += 1

                not_found_sentences.append(
                    sentence
                )

        total_sentences = len(sentences)

        if total_sentences > 0:

            coverage = (
                translated_count
                / total_sentences
            ) * 100

        else:

            coverage = 0

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        return {
            "translation":
                " ".join(
                    translated_sentences
                ),

            "total_sentences":
                total_sentences,

            "translated_sentences":
                translated_count,

            "not_found_sentences":
                not_found_count,

            "coverage":
                round(coverage, 2),

            "not_found":
                not_found_sentences,

            "time":
                elapsed_time
        }

    # =========================================================
    # DATASET SIZE
    # =========================================================

    def get_dataset_size(self):
        """
        Return number of unique translations.
        """

        return len(self.translations)


# =============================================================
# COMMAND-LINE TEST
# =============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "ENGLISH TO HAUSA TRANSLATOR"
    )

    print("=" * 60)

    try:

        translator = Translator()

        print(
            f"Loaded "
            f"{translator.get_dataset_size():,} "
            f"translations."
        )

        print(
            "\nType an English sentence "
            "or paragraph."
        )

        print(
            "Type 'exit' to close."
        )

        while True:

            sentence = input(
                "\nEnglish: "
            ).strip()

            if sentence.casefold() in {
                "exit",
                "quit"
            }:

                print(
                    "Translator closed."
                )

                break

            if not sentence:
                continue

            # Detect paragraph
            sentences = (
                translator.split_sentences(
                    sentence
                )
            )

            if len(sentences) <= 1:

                # Single sentence

                translation = (
                    translator.translate(
                        sentence
                    )
                )

                if translation:

                    print(
                        f"Hausa: "
                        f"{translation}"
                    )

                else:

                    print(
                        "Translation not found."
                    )

            else:

                # Paragraph

                result = (
                    translator.translate_paragraph(
                        sentence
                    )
                )

                print(
                    f"\nHausa:\n"
                    f"{result['translation']}"
                )

                print(
                    "\n"
                    f"Translation statistics:"
                )

                print(
                    f"Total sentences: "
                    f"{result['total_sentences']}"
                )

                print(
                    f"Translated: "
                    f"{result['translated_sentences']}"
                )

                print(
                    f"Not found: "
                    f"{result['not_found_sentences']}"
                )

                print(
                    f"Coverage: "
                    f"{result['coverage']}%"
                )

                print(
                    f"Processing time: "
                    f"{result['time']:.6f} seconds"
                )

    except FileNotFoundError as error:

        print(
            f"\nERROR: {error}"
        )

    except ValueError as error:

        print(
            f"\nDATASET ERROR: {error}"
        )