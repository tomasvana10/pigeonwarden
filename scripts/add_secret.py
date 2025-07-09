import secrets

from dotenv import set_key

_env = ".env.local"
_key = "SECRET_KEY"

secret = secrets.token_hex(32)
set_key(_env, _key, secret)

print("updated/added secret.")
