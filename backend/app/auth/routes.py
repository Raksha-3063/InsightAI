from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timezone
from bson import ObjectId
from backend.app.database.connection import db_helper
from backend.app.schemas.user import UserCreate, UserResponse, UserLogin, Token, RefreshRequest
from backend.app.auth.service import verify_password, get_password_hash, create_access_token, decode_access_token, create_refresh_token, decode_refresh_token
from backend.app.models.user import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login-json")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Query database for user
    user_dict = await db_helper.db.users.find_one({"email": email})
    if user_dict is None:
        raise credentials_exception
    
    return User(**user_dict)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db_helper.db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed = get_password_hash(user_data.password)
    
    # Create user dict
    new_user_dict = {
        "name": user_data.name,
        "email": user_data.email,
        "hashed_password": hashed,
        "createdAt": datetime.now(timezone.utc)
    }
    
    # Insert in DB
    result = await db_helper.db.users.insert_one(new_user_dict)
    new_user_dict["_id"] = str(result.inserted_id)
    
    return UserResponse(**new_user_dict)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    user_dict = await db_helper.db.users.find_one({"email": credentials.email})
    if not user_dict or not verify_password(credentials.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user_dict["email"]})
    refresh_token = create_refresh_token(data={"sub": user_dict["email"]})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

# Form-based login for Swagger UI compat
@router.post("/login-json", response_model=Token, include_in_schema=False)
async def login_json(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = await db_helper.db.users.find_one({"email": form_data.username})
    if not user_dict or not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user_dict["email"]})
    refresh_token = create_refresh_token(data={"sub": user_dict["email"]})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/refresh", response_model=Token)
async def refresh(request: RefreshRequest):
    payload = decode_refresh_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject"
        )
        
    user_dict = await db_helper.db.users.find_one({"email": email})
    if user_dict is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    new_access_token = create_access_token(data={"sub": email})
    new_refresh_token = create_refresh_token(data={"sub": email})
    return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    user_dict = current_user.model_dump(by_alias=True)
    user_dict["_id"] = str(user_dict["_id"])
    return UserResponse(**user_dict)
