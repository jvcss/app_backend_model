from pydantic import BaseModel, EmailStr

class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str | None = None

class ForgotPasswordStartIn(BaseModel):
    email: EmailStr

class ForgotPasswordVerifyIn(BaseModel):
    email: EmailStr
    otp: str | None = None
    totp: str | None = None

class ForgotPasswordVerifyOut(BaseModel):
    reset_session_token: str

class ForgotPasswordConfirmIn(BaseModel):
    new_password: str

class TwoFASetupOut(BaseModel):
    secret: str
    otpauth_url: str
