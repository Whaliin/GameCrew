from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Return hashed password  
def hash_password(plaintext: str) -> str:
    """Return a bcrypt hash of the plaintext password."""
    return _pwd_context.hash(plaintext)

# Verify that password is correct
def verify_password(plaintext: str, hashed: str) -> bool:
    """Return True if plaintext matches the bcrypt hash (constant-time)."""
    return _pwd_context.verify(plaintext, hashed)
