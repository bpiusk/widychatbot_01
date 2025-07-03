# auth.py
# Modul autentikasi admin dan JWT untuk backend
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi JWT dan admin
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")  # hash password admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")
    
def verify_password(plain_password, hashed_password):
    """Verifikasi password plain dengan hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash password baru."""
    return pwd_context.hash(password)

def authenticate_admin(username: str, password: str):
    """Cek username dan password admin."""
    if username != ADMIN_USERNAME:
        return False
    if not ADMIN_PASSWORD_HASH:
        return False
    return verify_password(password, ADMIN_PASSWORD_HASH)

def create_access_token(username: str):
    """Buat JWT token untuk admin."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_admin(token: str = Depends(oauth2_scheme)):
    """Ambil username admin dari JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != ADMIN_USERNAME:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username