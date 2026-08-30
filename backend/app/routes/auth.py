from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from secrets import token_urlsafe
from datetime import datetime, timedelta

from app.models.user import UserRegister
from app.models.password import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from app.config.database import users_collection

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.auth.dependencies import get_current_user
from app.auth.email import send_reset_email


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# -------------------------
# Test Email
# -------------------------
@router.get("/test-email")
def test_email():

    send_reset_email(
        "yourgmail@gmail.com",
        "test123456"
    )

    return {
        "message": "Email sent successfully"
    }


# -------------------------
# Register
# -------------------------
@router.post("/register")
def register(user: UserRegister):

    existing_user = users_collection.find_one(
        {"email": user.email}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password)
    }

    users_collection.insert_one(new_user)

    return {
        "message": "User registered successfully"
    }


# -------------------------
# Login
# -------------------------
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    db_user = users_collection.find_one(
        {"email": form_data.username}
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        db_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "sub": db_user["email"]
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------
# Current User
# -------------------------
@router.get("/me")
def get_me(
    current_user=Depends(get_current_user)
):

    return {
        "name": current_user["name"],
        "email": current_user["email"]
    }


# -------------------------
# Forgot Password
# -------------------------
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest
):

    user = users_collection.find_one(
        {"email": data.email}
    )

    # Do not reveal whether the email exists
    if not user:
        return {
            "message":
                "If an account exists with this email, "
                "a password reset link has been sent."
        }

    token = token_urlsafe(32)

    expiry = (
        datetime.utcnow()
        + timedelta(minutes=15)
    )

    users_collection.update_one(
        {"email": data.email},
        {
            "$set": {
                "reset_token": token,
                "reset_token_expiry": expiry
            }
        }
    )

    send_reset_email(
        data.email,
        token
    )

    return {
        "message":
            "Password reset email sent successfully."
    }


# -------------------------
# Reset Password
# -------------------------
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest
):

    # Find user using reset token
    user = users_collection.find_one(
        {"reset_token": data.token}
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset token."
        )

    # Check if expiry field exists
    expiry = user.get(
        "reset_token_expiry"
    )

    if not expiry:
        raise HTTPException(
            status_code=400,
            detail="Password reset token is invalid."
        )

    # Check whether token has expired
    if datetime.utcnow() > expiry:
        raise HTTPException(
            status_code=400,
            detail="Password reset token has expired."
        )

    # Hash new password
    hashed_password = hash_password(
        data.new_password
    )

    # Update password and remove reset token
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password": hashed_password
            },
            "$unset": {
                "reset_token": "",
                "reset_token_expiry": ""
            }
        }
    )

    return {
        "message":
            "Password reset successfully. "
            "You can now log in with your new password."
    }