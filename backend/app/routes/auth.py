@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    import time

    start = time.perf_counter()

    db_user = users_collection.find_one(
        {"email": form_data.username}
    )

    after_db = time.perf_counter()

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

    after_bcrypt = time.perf_counter()

    token = create_access_token(
        {
            "sub": db_user["email"]
        }
    )

    after_jwt = time.perf_counter()

    print(
        "LOGIN TIMING:",
        "DB =", round(after_db - start, 3),
        "bcrypt =", round(after_bcrypt - after_db, 3),
        "JWT =", round(after_jwt - after_bcrypt, 3),
        "TOTAL =", round(after_jwt - start, 3)
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }