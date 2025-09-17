# Add to __init__ method
def __init__(self, registry=None, recovery_library=None, commentary_engine=None):
    self.subsystems = {}
    self.registry = registry
    self.recovery_library = recovery_library
    self.commentary_engine = commentary_engine
    self.commentary_mode = True
    self.status_log = []

