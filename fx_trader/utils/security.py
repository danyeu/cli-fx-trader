import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password

def verify_password(password:str, actual_hashed_password: str):
    password_bytes = password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, actual_hashed_password)
