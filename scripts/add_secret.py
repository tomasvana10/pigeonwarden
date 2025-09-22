import secrets
import sys

from dotenv import set_key

_env = ".env.local"
_key = str(sys.argv[1])

secret = secrets.token_hex(32)
set_key(_env, _key, secret)

print("updated/added secret.")
