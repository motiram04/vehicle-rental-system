from werkzeug.security import generate_password_hash

password = input("Enter password: ")

hashed_password = generate_password_hash(password)

print("\nGenerated Hash:\n")
print(hashed_password)