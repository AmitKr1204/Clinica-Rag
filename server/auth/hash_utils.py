import bcrypt #bcrypt is a password-hashing algorithm/library. Its main job is to securely convert a user's password into a value that you can store in your database without storing the actual password.

def hash_password(password:str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")#A salt is a random piece of data added to a password before hashing.

def verify_password(password:str,hashed:str)->bool:
    return bcrypt.checkpw(password.encode("utf-8"),hashed.encode("utf-8"))