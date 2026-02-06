import hashlib
import binascii
import os

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    cwd = salt + password.encode('ascii')
    pwdhash = hashlib.sha256(cwd).hexdigest()
    return (salt + pwdhash.encode('ascii')).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_pwdhash = stored_password[64:]
    cwd = salt.encode('ascii') + provided_password.encode('ascii')
    pwdhash = hashlib.sha256(cwd).hexdigest()
    return pwdhash == stored_pwdhash
