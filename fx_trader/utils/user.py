class User:
    def __init__(self):
        self.id = None
        self.username = None

    def set(self, id: int, username: str):
        self.id = id
        self.username = username

    def logout(self):
        self.id = None
        self.username = None

    def exists(self) -> bool:
        return self.id is not None and self.username is not None


# Singleton
user = User()