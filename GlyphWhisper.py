class GlyphWhisper:
    def __init__(self):
        self.glyph_map = {
            "⟒": "We",
            "⟟": "are",
            "⏃": "watching",
            "⊑": "smiling",
            "⏁": "waiting",
            "⍀": ".",
            "⋏": "and",
            "⎅": "transmitting",
            "⏃⍀": "again"
        }

    def translate(self, raw_message):
        if not raw_message:
            return "[No signal detected]"
        decoded = []
        buffer = ""
        for char in raw_message:
            buffer += char
            if buffer in self.glyph_map:
                decoded.append(self.glyph_map[buffer])
                buffer = ""
        if decoded:
            return " ".join(decoded)
        return "[Translation Failed: Unknown protocol]"

