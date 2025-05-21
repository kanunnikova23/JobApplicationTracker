# importing the security toolbox that handles hashing passwords
from passlib.context import CryptContext

# setting up the rules for how passwords will be hashed.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# This function receives a plain-text password from the user and hashes it,
# so it can be safely stored in the database
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# This function is used during login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
