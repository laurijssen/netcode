from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

import os

# NOT SECURE reuses iv+key, EXPERIMENT
class EncryptionManager:
    def __init__(self):
        self.key = os.urandom(32)
        self.iv = os.urandom(16)

    def encrypt_message(self, message):
        encryptor = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend()).encryptor()
        padder = padding.PKCS7(128).padder()
        padded_message = padder.update(message)
        padded_message += padder.finalize()
        ciphertext = encryptor.update(padded_message)
        ciphertext += encryptor.finalize()
        return ciphertext

    def decrypt_message(self, ciphertext):
        decryptor = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend()).decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        padded_message = decryptor.update(ciphertext)
        padded_message += decryptor.finalize()
        message = unpadder.update(padded_message)
        message += unpadder.finalize()
        return message

enc = EncryptionManager()

plaintexts = [
    b"SHORTY",
    b"MEDMEDMEDMEDMEDMED",
    b"LONGLONGLONGLONGLONGLONG"
]

for text in plaintexts:
    e = enc.encrypt_message(text)
    print(e)
    d = enc.decrypt_message(e)
    print(d)

