class Announcements:
    def __init__(self, title, content, timestamp):
        self.title = title
        self.content = content
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp
        }
