class MessageQueue:
    def __init__(self):
        self.queue = []

    def add_message(self, message):
        self.queue.append(message)

    def get_message(self):
        if self.queue:
            return self.queue.pop(0)
        return None
