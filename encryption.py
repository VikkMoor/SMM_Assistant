
from cryptography.fernet import Fernet
from config import fernet_key


class Encryption:
    def __init__(self):
        if not fernet_key:
            raise ValueError("Не задан ключ шифрования FERNET_KEY в .env")

        self.cipher = Fernet(fernet_key.encode())

    def encrypt(self, value):
        if not value:
            return None

        encrypted_value = self.cipher.encrypt(value.encode())
        return encrypted_value.decode()

    def decrypt(self, value):
        if not value:
            return None

        decrypted_value = self.cipher.decrypt(value.encode())
        return decrypted_value.decode()
