
import os, secrets, string
from datetime import datetime, timedelta, timezone
from jose import jwt
import bcrypt
import pyotp
from app.core.config import settings

SECRET_KEY = settings.KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 99999

RESET_SESSION_EXPIRE_MINUTES = 15       # short-lived session for changing password
OTP_TTL_MINUTES = 10
OTP_LENGTH = 6


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password)

def get_password_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_access_token(data: dict, token_version: int, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "tv": token_version})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- OTP (email) ---
def generate_otp() -> str:
    # digits only to ease typing in mobile
    return "".join(secrets.choice(string.digits) for _ in range(OTP_LENGTH))

def hash_otp(otp: str) -> str:
    return bcrypt.hashpw(otp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_otp(otp: str, hashed: str) -> bool:
    return bcrypt.checkpw(otp.encode("utf-8"), hashed.encode("utf-8"))

# --- TOTP (authenticator app) ---
def generate_totp_secret() -> str:
    return pyotp.random_base32()

def verify_totp(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)  # ±30s window

# --- Reset-session JWT (limited scope) ---
def create_reset_session_token(user_id: int, token_version: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_SESSION_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "tv": token_version, "scope": "pwd_reset", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
