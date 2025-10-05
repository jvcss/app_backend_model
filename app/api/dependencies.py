from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.session import SessionAsync, SessionSync
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_db():
    async with SessionAsync() as session:
        yield session

# Synchronous version if needed
def get_db_sync():
    db = SessionSync()
    try:
        yield db
    finally:
        db.close()


# app/api/dependencies.py (adjusted)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_sync)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        tv = payload.get("tv")
        if user_id is None or tv is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).get(int(user_id))
    if not user or int(tv) != int(user.token_version or 1):
        raise credentials_exception
    return user
