# Security utilities - importing from main auth module
from auth import verify_password, get_password_hash as hash_password

# Re-export for compatibility
__all__ = ['verify_password', 'hash_password']
