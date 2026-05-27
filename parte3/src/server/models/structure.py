class Structure:
    def __init__(self, structure_type, author, timestamp):
        self.structure_type = structure_type
        self.author = author
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "type": self.structure_type,
            "author": self.author,
            "time": self.timestamp
        }
