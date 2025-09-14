# workers/worker_base.py
class WorkerBase:
    def __init__(self, config=None):
        self.name = self.__class__.__name__
        self.config = config or {}
    def execute_task(self, args, stop_event):
        raise NotImplementedError("This method must be implemented by subclasses.")
