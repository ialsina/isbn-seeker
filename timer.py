from datetime import datetime

class Timer:
    def __init__(self, active=True):
        self.active = active
        self.time = datetime.now()

    def lap(self):
        last = self.time
        self.time = datetime.now()
        delta = self.time - last
        if self.active:
            print(delta)
