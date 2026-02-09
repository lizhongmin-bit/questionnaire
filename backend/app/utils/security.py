import secrets


def generate_public_token() -> str:
    return secrets.token_hex(32)
