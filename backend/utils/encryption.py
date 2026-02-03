import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import json

# In production, load this from environment or secret manager
ENCRYPTION_KEY = os.getenv("FIELD_ENCRYPTION_KEY", base64.urlsafe_b64encode(os.urandom(32)).decode())

def _derive_key(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    return kdf.derive(password)

def encrypt_field(value: str | dict | float | int) -> str:
    if value is None:
        return None
    plaintext = json.dumps(value).encode()
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = _derive_key(ENCRYPTION_KEY.encode(), salt)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return base64.urlsafe_b64encode(salt + iv + encryptor.tag + ciphertext).decode()

def decrypt_field(token: str) -> str | dict | float | int:
    if token is None:
        return None
    data = base64.urlsafe_b64decode(token.encode())
    salt, iv, tag, ciphertext = data[:16], data[16:28], data[28:44], data[44:]
    key = _derive_key(ENCRYPTION_KEY.encode(), salt)
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return json.loads(plaintext.decode())
