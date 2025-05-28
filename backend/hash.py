from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
plain_password = "kanyan141024"  # Ganti dengan password yang diinginkan
print(pwd_context.hash(plain_password))