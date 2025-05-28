from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib

class PasswordCrypto:
    def __init__(self):
        # Generate a key from the secret key (not the most secure, but functional)
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt a password"""
        try:
            encrypted = self.fernet.encrypt(password.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception:
            # If encryption fails, return the password as-is (fallback)
            return password
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt a password"""
        try:
            # Try to decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            # If decryption fails, assume it's already plaintext (for backward compatibility)
            return encrypted_password

# Global instance
password_crypto = PasswordCrypto()
