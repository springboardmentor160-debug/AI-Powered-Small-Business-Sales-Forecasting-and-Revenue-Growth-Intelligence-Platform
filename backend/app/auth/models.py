class User:
    def __init__(
        self,
        id,
        username,
        email,
        password_hash,
        role
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role