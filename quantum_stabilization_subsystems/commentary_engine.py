# commentary_engine.py

class CommentaryEngine:
    def __init__(self):
        self.commentary_log = []
        self.commentary_mode = True

    def broadcast(self, message, source=None):
        entry = f"[{source or 'Ensemble'} Commentary] {message}"
        self.commentary_log.append(entry)
        if self.commentary_mode:
            print(entry)

    def get_log(self):
        return self.commentary_log

    def initialize(self):
        self.broadcast("Commentary Engine initialized. Ensemble voice online.")

