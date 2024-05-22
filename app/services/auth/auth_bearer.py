from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.models.user import Token
from app.services.auth.auth_jwt import JWTHandler


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials: HTTPAuthorizationCredentials | None = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(Token(access_token=credentials.credentials)):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials
        else:
            raise HTTPException(
                status_code=403,
                detail="Invalid authorization code.",
            )

    def verify_jwt(self, jwtoken: Token) -> bool:
        try:
            payload = JWTHandler.jwt_decode(token=jwtoken)
        except JWTError:
            payload = None

        return True if payload else False
