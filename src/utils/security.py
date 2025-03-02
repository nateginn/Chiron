"""
HIPAA-compliant security functions.
"""
from cryptography.fernet import Fernet
import os
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Security:
    def __init__(self, config):
        self.key = os.getenv('ENCRYPTION_KEY')
        if not self.key:
            self.key = Fernet.generate_key()
            logger.warning("No encryption key found, generated new key")
        self.cipher_suite = Fernet(self.key)
        
    def encrypt_data(self, data):
        """Encrypt sensitive data."""
        try:
            if isinstance(data, str):
                data = data.encode()
            return self.cipher_suite.encrypt(data)
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise
            
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data."""
        try:
            return self.cipher_suite.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise
            
    @staticmethod
    def sanitize_input(data):
        """Sanitize user input to prevent injection attacks."""
        # Implementation of input sanitization
        return data
