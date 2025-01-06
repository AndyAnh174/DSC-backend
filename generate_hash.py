import bcrypt

password = "test"
salt = bcrypt.gensalt(12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(hashed.decode('utf-8')) 
