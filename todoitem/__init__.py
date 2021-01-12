from datetime import datetime


class TodoItem:
    def __init__(self, descr=None, priority='A', time=0, done=False, created=datetime.utcnow):
        self.descr = descr
        self.priority = priority
        self.time = time
        self.done = done
        self.created = created
