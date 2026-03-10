from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from schemes import Token, TokenData
from database_setup import get_db, User
from sqlalchemy.orm import Session

SECRET_KEY = "bukakke_secret_key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30    

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")


#security options
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password) -> str: 
    #password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return TokenData(email=email)
    except jwt.PyJWTError:  
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
#Auth Dependencies
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(token)
    token_data = verify_token(token)
    user =   db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user

def get_current_active_user(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.email == current_user.email).first()
    print(user) 
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user