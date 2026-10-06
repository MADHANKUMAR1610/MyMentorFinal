from cryptography.fernet import Fernet
from app.core.config import settings


def get_cipher():
    return Fernet(settings.ADMIN_PASSWORD_ENCRYPTION_KEY)


def encrypt_password(password: str) -> str:
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    cipher = get_cipher()
    return cipher.decrypt(encrypted_password.encode()).decode()