"""
Encryption utilities for OAuth tokens.
"""

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


class TokenEncryption:
    """Handles encryption and decryption of OAuth tokens."""

    def __init__(self, key: str = None):
        """
        Initialize encryption with a key.
        
        Args:
            key: Encryption key (32 bytes). Uses settings.ENCRYPTION_KEY if not provided.
        """
        encryption_key = key or settings.ENCRYPTION_KEY
        
        # Derive a key from the provided string
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"social_media_ai_salt",  # In production, use a random salt per user
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        self.fernet = Fernet(derived_key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        encrypted = base64.urlsafe_b64decode(ciphertext.encode())
        decrypted = self.fernet.decrypt(encrypted)
        return decrypted.decode()


# Global encryption instance
token_encryption = TokenEncryption()


def encrypt_token(token: str) -> str:
    """Encrypt an OAuth token."""
    return token_encryption.encrypt(token)


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an OAuth token."""
    return token_encryption.decrypt(encrypted_token)
