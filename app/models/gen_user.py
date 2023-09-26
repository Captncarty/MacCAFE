import secrets
import string

def generate_username(length=8):
    """ Generate a username with the given length
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_password(length=12):
    """ Generate a password with the given length"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))