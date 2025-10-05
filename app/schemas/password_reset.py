# app/schemas/password_reset.py
from pydantic import BaseModel, EmailStr

class ForgotPasswordStartIn(BaseModel):
    email: EmailStr

class ForgotPasswordVerifyIn(BaseModel):
    email: EmailStr
    otp: str | None = None
    totp: str | None = None  # if user has TOTP enabled, must be provided

class ForgotPasswordVerifyOut(BaseModel):
    reset_session_token: str

class ForgotPasswordConfirmIn(BaseModel):
    new_password: str

class TwoFASetupOut(BaseModel):
    secret: str
    otpauth_url: str
