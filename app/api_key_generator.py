import secrets

def generate_api_key() -> str:
    return secrets.token_hex(16)
