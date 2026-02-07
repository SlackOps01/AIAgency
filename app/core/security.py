from fastapi import Depends, HTTPException
from jose import JWTError, jwt 
from app.core.config import CONFIG
from fastapi.security.oauth2 import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from app.schemas.token import TokenData

oauth2scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    iat = datetime.now(timezone.utc)
    to_encode.update({"exp": expire, "iat": iat})
    encoded_jwt = jwt.encode(to_encode, CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM)
    return encoded_jwt    

def verify_access_token(token: str, credential_exception: HTTPException) -> TokenData:
    try:
        payload = jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])
        id = payload.get("id")
        role = payload.get("role")

        if id is None or role is None:
            raise credential_exception

        token_data = TokenData(id=id, role=role)
        return token_data
    except JWTError:
        raise credential_exception
        

def get_current_user(token: str = Depends(oauth2scheme)) -> TokenData:
    credential_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return verify_access_token(token, credential_exception)
            
        
        