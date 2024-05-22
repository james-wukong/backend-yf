from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import JWTClaimsError, JWTError, ExpiredSignatureError

from app.core.config import settings

# from app.core.log_config import ip_logger

from app.models.relationships import User
from app.models.user import Token, TokenPayload


class JWTHandler:
    key: str = settings.SECRET_KEY
    alg: str = settings.ALGORITHM

    @classmethod
    def jwt_encode(
        cls,
        user: User,
        expires_delta: timedelta = timedelta(hours=24 * 1),
    ) -> Token:
        payload = TokenPayload.model_validate(
            {
                "user_id": user.id,
                "sub": f"quants|{user.id}",
                "email": user.email,
                "exp": datetime.now(timezone.utc) + expires_delta,
            }
        )

        token_str = jwt.encode(
            payload.model_dump(),
            key=cls.key,
            algorithm=cls.alg,
        )
        print(token_str)

        return Token(access_token=token_str)

    @classmethod
    def jwt_decode(cls, token: Token) -> TokenPayload | None:
        try:
            decoded_token = jwt.decode(
                token=token.access_token, key=cls.key, algorithms=[cls.alg]
            )
            return TokenPayload(**decoded_token)
        except ExpiredSignatureError as e:
            print("Token Expired: ", e)
            unverified_claim = jwt.get_unverified_claims(token.access_token)
            new_payload = TokenPayload.model_validate(
                unverified_claim,
                update={
                    "exp": datetime.now(timezone.utc)
                    + timedelta(hours=float(settings.TOKEN_EXPIRE_HOURS)),
                },
            )
            new_token = JWTHandler.jwt_refresh(payload=new_payload)

            if not new_token:
                return None
            return new_payload
        except JWTClaimsError as e:
            print("Token Claim Error: ", e)
            return None
        except JWTError as e:
            print("Token Error: ", e)
            return None

    @classmethod
    def jwt_refresh(
        cls,
        payload: TokenPayload,
    ) -> Token | None:
        if payload.iat + timedelta(
            hours=float(settings.TOKEN_REFRESH_HOURS),
        ) > datetime.now(tz=timezone.utc):
            token_str = jwt.encode(
                payload.model_dump(),
                key=cls.key,
                algorithm=cls.alg,
            )
            return Token(access_token=token_str)
        else:
            print("refresh token expired")
            return None
