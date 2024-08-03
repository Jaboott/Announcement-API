class Announcements:
    def __init__(self, title, content, timestamp):
        """
        Initialize an Announcements object.

        :param title: Title of the announcement.
        :param content: Body of the announcement.
        :param timestamp: The time the announcement is created in Epoch time
        """

        self.title = title
        self.content = content
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp
        }
