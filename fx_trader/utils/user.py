class User:
    def __init__(self):
        self.uid = None
        self.username = None

    def set(self, uid: int, username: str):
        self.uid = uid
        self.username = username

    def logout(self):
        self.uid = None
        self.username = None

    def exists(self) -> bool:
        return self.uid is not None and self.username is not None


# Singleton
user = User()
