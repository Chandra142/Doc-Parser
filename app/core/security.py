from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from app.core.config import settings
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(value: str) -> str: return pwd.hash(value)
def verify_password(value: str, hashed: str) -> bool: return pwd.verify(value, hashed)
def token_for(user_id: str) -> str:
    return jwt.encode({"sub": user_id, "exp": datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes)}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
def user_from_token(token: str) -> str:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])["sub"]
