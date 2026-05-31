from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    senha: str


class RefreshRequest(BaseModel):
    refreshToken: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    usuario: dict
