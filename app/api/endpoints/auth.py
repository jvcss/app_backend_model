"""
    Authentication and Authorization Endpoints
    This module provides API endpoints for user authentication, registration, password reset, and two-factor authentication (2FA) management. It leverages FastAPI for routing, SQLAlchemy for database interactions, and JWT for secure token handling. The endpoints are designed with security best practices, including rate limiting, anti-enumeration measures, and support for out-of-band OTP delivery.
    Endpoints:
    - /login: Authenticates a user and issues a JWT access token.
    - /me: Returns the current authenticated user's information and a fresh access token.
    - /logout: Handles user logout (JWT-based, client-side or via blacklist).
    - /register: Registers a new user, creates a personal team, and issues an access token.
    - /forgot-password/start: Initiates the password reset process by sending an OTP to the user's email.
    - /forgot-password/verify: Verifies the OTP (and optionally TOTP) for password reset and issues a reset session token.
    - /forgot-password/confirm: Confirms the password reset using the reset session token and updates the user's password.
    - /2fa/setup: Generates and returns a TOTP secret and provisioning URI for 2FA setup.
    - /2fa/verify: Verifies the TOTP code and enables 2FA for the user.
    Security Features:
    - Rate limiting to prevent brute-force and enumeration attacks.
    - Uniform error responses to avoid leaking user existence.
    - OTP and TOTP verification for secure password reset and 2FA.
    - Token versioning to invalidate old tokens upon password change.
    Dependencies:
    - FastAPI, SQLAlchemy, pyotp, jose, custom security and helper modules.

"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
import pyotp
from sqlalchemy.orm import Session

from app.schemas.auth import Token, Login
from app.schemas.user import UserCreate

from app.models.team import Team as TeamModel
from app.api.dependencies import get_current_user, get_db, get_db_sync

from app.db.session import SessionSync
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.schemas.password_reset import (
    ForgotPasswordStartIn, ForgotPasswordVerifyIn, ForgotPasswordVerifyOut, ForgotPasswordConfirmIn, TwoFASetupOut
)
from app.core.security import (
    generate_otp, hash_otp, verify_otp, create_reset_session_token, verify_password,
    verify_totp, generate_totp_secret, create_access_token, get_password_hash, SECRET_KEY, ALGORITHM
)
from app.helpers.rate_limit import allow
from app.mycelery.worker import send_password_otp, send_password_otp_local


router = APIRouter()

@router.post("/login", response_model=Token)
def login(login_data: Login, db: Session = Depends(get_db_sync)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        token_version=user.token_version
        )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, 
        token_version=current_user.token_version
    )
    return {
        "user": current_user,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout():
    # Com JWT, logout pode ser gerenciado no cliente ou via blacklist (implementar)
    return {"message": "Logout realizado"}

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db_sync)):
    # Verifica se o email já está cadastrado
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Cria o usuário com a senha hasheada
    hashed_password = get_password_hash(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    # Realiza um flush para que new_user.id seja atribuído sem efetuar o commit
    db.flush()

    # Cria um time para o novo usuário
    new_team = TeamModel(name=f"Time de {new_user.name}", user_id=new_user.id, personal_team=True)
    db.add(new_team)
    db.flush()  # Garante que new_team.id seja atribuído

    # Atualiza o usuário com o ID do time criado
    new_user.current_team_id = new_team.id

    # Efetua o commit de todas as operações
    db.commit()
    db.refresh(new_user)

    # Cria o token de acesso para o novo usuário
    access_token = create_access_token(data={"sub": str(new_user.id)}, token_version=new_user.token_version)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password/start", status_code=status.HTTP_202_ACCEPTED)
def forgot_password_start(payload: ForgotPasswordStartIn, request: Request, db: Session = Depends(get_db_sync)):
    client_ip = request.headers.get("x-forwarded-for", request.client.host)
    # throttle
    if not allow("fp:start", payload.email, client_ip, max_attempts=5, window_sec=900):
        raise HTTPException(status_code=429, detail="Too many requests")

    user = db.query(User).filter(User.email == payload.email).first()

    # Always behave the same (anti-enumeration)
    if user:
        otp = generate_otp()
        pr = PasswordReset(
            user_id=user.id,
            email=payload.email,
            otp_hash=hash_otp(otp),
            otp_expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            require_totp=user.two_factor_enabled
        )
        db.add(pr)
        db.commit()

        # Send OTP out-of-band
        #send_password_otp_local(payload.email, otp)
        send_password_otp_local.delay(payload.email, otp)

    # Return 202 with generic message
    return {"message": "If the email exists, a verification code has been sent."}

@router.post("/forgot-password/verify", response_model=ForgotPasswordVerifyOut)
def forgot_password_verify(payload: ForgotPasswordVerifyIn, request: Request, db: Session = Depends(get_db_sync)):
    client_ip = request.headers.get("x-forwarded-for", request.client.host)
    if not allow("fp:verify", payload.email, client_ip, max_attempts=10, window_sec=900):
        raise HTTPException(status_code=429, detail="Too many attempts")

    # pick most recent valid request
    pr = (db.query(PasswordReset)
            .filter(PasswordReset.email == payload.email, PasswordReset.consumed_at.is_(None))
            .order_by(PasswordReset.id.desc())
            .first())

    # Uniform failure to avoid oracle
    if not pr or not pr.otp_hash or not pr.otp_expires_at or pr.otp_expires_at < datetime.now(pr.otp_expires_at.tzinfo):
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    # verify OTP
    if not payload.otp or not verify_otp(payload.otp, pr.otp_hash):
        pr.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    pr.otp_verified = True

    # if user requires TOTP, enforce it
    user = db.query(User).get(pr.user_id) if pr.user_id else None
    if pr.require_totp:
        if not user or not user.two_factor_secret or not payload.totp or not verify_totp(user.two_factor_secret, payload.totp):
            pr.attempts += 1
            db.commit()
            raise HTTPException(status_code=400, detail="Invalid or missing authenticator code")
        pr.totp_verified = True

    # issue reset session token
    pr.reset_session_issued_at = datetime.now(timezone.utc)
    db.commit()

    rst = create_reset_session_token(user_id=user.id, token_version=user.token_version)
    return ForgotPasswordVerifyOut(reset_session_token=rst)

@router.post("/forgot-password/confirm", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password_confirm(payload: ForgotPasswordConfirmIn, request: Request, db: Session = Depends(get_db_sync)):
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing reset session")

    token = auth_header.split(" ", 1)[1]
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid reset session")

    if claims.get("scope") != "pwd_reset":
        raise HTTPException(status_code=401, detail="Invalid reset session")

    user_id = int(claims["sub"])
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid reset session")

    # rotate password & bump token_version
    user.password = get_password_hash(payload.new_password)
    user.token_version = (user.token_version or 1) + 1
    db.commit()

    # mark last reset as consumed
    pr = (db.query(PasswordReset)
            .filter(PasswordReset.user_id == user_id, PasswordReset.consumed_at.is_(None))
            .order_by(PasswordReset.id.desc())
            .first())
    if pr:
        pr.consumed_at = datetime.now(timezone.utc)
        db.commit()

    return

@router.post("/2fa/setup", response_model=TwoFASetupOut)
def twofa_setup(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_sync)):
    secret = generate_totp_secret()
    issuer = "Application"
    label = f"{issuer}:{current_user.email}"
    url = pyotp.totp.TOTP(secret).provisioning_uri(name=label, issuer_name=issuer)

    current_user.two_factor_secret = secret
    current_user.two_factor_enabled = False
    db.commit()
    return TwoFASetupOut(secret=secret, otpauth_url=url)

@router.post("/2fa/verify", status_code=204)
def twofa_verify(code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_sync)):
    if not current_user.two_factor_secret or not verify_totp(current_user.two_factor_secret, code):
        raise HTTPException(status_code=400, detail="Invalid code")
    current_user.two_factor_enabled = True
    db.commit()
    return

