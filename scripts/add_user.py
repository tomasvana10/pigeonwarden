from dotenv import set_key, get_key
import sys
from passlib.hash import bcrypt

_env = ".env.local"
_key = "USERS"

if len(sys.argv) != 3:
    print("Usage: scripts/add_user.py <username> <password>")
    sys.exit(1)

username, password = sys.argv[1], sys.argv[2]
hashed = bcrypt.hash(password)

existing = get_key(_env, _key)
if existing is None:
    existing = ""

pairs = [p for p in existing.split(",") if p.strip()]
pairs = [p for p in pairs if not p.startswith(f"{username}:")]
pairs.append(f"{username}:{hashed}")
new_users = ",".join(pairs)

set_key(_env, _key, new_users)
print("user entry added.")
