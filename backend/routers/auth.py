from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.database import get_db
from backend.models import User
from backend.schemas import UserLogin, UserRegister, UserResponse, TokenResponse
from backend.auth import hash_password, verify_password, create_access_token
from backend.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Helper mapping for username aliases used in testing/demo accounts
USERNAME_ALIASES = {
    "owner": "owner@marketmind.ai",
    "manager": "manager@marketmind.ai",
    "exec": "exec@marketmind.ai",
    "admin": "admin@marketmind.ai",
}

VALID_ROLES = {"owner", "manager", "sales_executive", "admin"}


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    identifier = credentials.username.strip().lower()
    # Resolve alias if provided (e.g. 'owner' -> 'owner@marketmind.ai')
    resolved_email = USERNAME_ALIASES.get(identifier, identifier)

    user = db.query(User).filter(
        or_(User.email == resolved_email, User.email == identifier)
    ).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue JWT token with subject and role
    token = create_access_token(
        data={"sub": user.email, "role": user.role, "name": user.name}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Validate role
    role = user_in.role.strip().lower()
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{role}'. Must be one of: {', '.join(sorted(VALID_ROLES))}",
        )

    # Check if email is already taken
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=hash_password(user_in.password),
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
