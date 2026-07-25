from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(
        ...,
        description="Password reset token"
    )

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (minimum 8 characters)"
    )