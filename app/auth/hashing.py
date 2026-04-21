import bcrypt

# Return hashed password  
def hash_password(plaintext: str) -> str:
	"""Return a bcrypt hash of the plaintext password."""
	password_bytes = plaintext.encode("utf-8")
	hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
	return hashed.decode("utf-8")

# Verify that password is correct
def verify_password(plaintext: str, hashed: str) -> bool:
	"""Return True if plaintext matches the bcrypt hash (constant-time)."""
	password_bytes = plaintext.encode("utf-8")
	hashed_bytes = hashed.encode("utf-8")
	return bcrypt.checkpw(password_bytes, hashed_bytes)
