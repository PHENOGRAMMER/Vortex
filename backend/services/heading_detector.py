import re


class HeadingDetector:

    @staticmethod
    def is_heading(text: str) -> bool:

        text = text.strip()

        if not text:
            return False

        # Very short line
        if len(text) > 80:
            return False

        # Ends with punctuation → probably a sentence
        if text.endswith((".", ",", ";", ":")):
            return False

        # Numbered headings
        if re.match(r"^\d+(\.\d+)*\s+", text):
            return True

        # Roman numeral headings
        if re.match(r"^[IVXLCDM]+\.", text):
            return True

        # ALL CAPS heading
        if text.isupper() and len(text.split()) <= 8:
            return True

        # Title Case heading
        words = text.split()

        if (
            len(words) <= 10
            and all(
                w[:1].isupper() or w.isdigit()
                for w in words
            )
        ):
            return True

        return False