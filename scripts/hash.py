import sys

from passlib.hash import bcrypt

print(bcrypt.hash(sys.argv[1]))
