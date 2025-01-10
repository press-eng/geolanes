import bcrypt

salt = bcrypt.gensalt()


def hashpw(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), salt)


def checkpw(password: str, hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hash)
