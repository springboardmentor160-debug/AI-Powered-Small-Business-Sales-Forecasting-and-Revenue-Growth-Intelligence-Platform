from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.database_models import User, Role
from app.auth.schemas import (
    RegisterRequest,
    UserResponse,
    LoginRequest,
    TokenResponse
)
from app.auth.security import hash_password, verify_password, create_access_token

from app.auth.dependencies import get_current_user

from app.auth.dependencies import (
    get_current_user,
    require_role,
    require_permission
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    # Check username
    existing_username = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    # Check email
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Find requested role
    role = db.query(Role).filter(
        Role.name == user_data.role
    ).first()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    # Create user
    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True
    )

    # Assign role
    new_user.roles.append(role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "role": role.name,
        "is_active": new_user.is_active
    }

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == login_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    role_names = [role.name for role in user.roles]

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "roles": role_names
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

#temporary route to test authentication
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    role_name = current_user.roles[0].name if current_user.roles else ""

    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": role_name,
        "is_active": current_user.is_active
    }

# temporary route to test role-based access control
@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(
        require_role("Administrator")
    )
):
    return {
        "message": "Administrator access granted",
        "username": current_user.username
    }

# temporary route to test permission-based access control
@router.get("/reports-test")
def reports_test(
    current_user: User = Depends(
        require_permission("reports:view")
    )
):
    return {
        "message": "Reports permission granted",
        "username": current_user.username
    }