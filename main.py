from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError

# Initialize FastAPI app
app = FastAPI(title="User CRUD API", version="1.0.0")

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ==================== Pydantic Models ====================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==================== Mock Database ====================
# In production, replace this with a real database (SQLAlchemy, MongoDB, etc.)

users_db = {}
user_id_counter = 1


# ==================== Helper Functions ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except PyJWTError:
        raise credentials_exception
    
    user = next((u for u in users_db.values() if u["email"] == token_data.email), None)
    if user is None:
        raise credentials_exception
    return UserInDB(**user)


# ==================== Auth Endpoints ====================

@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Register a new user
    
    - **email**: User's email address (must be unique)
    - **full_name**: User's full name
    - **password**: User's password (will be hashed)
    """
    global user_id_counter
    
    # Check if email already exists
    if any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = user_id_counter
    user_id_counter += 1
    
    new_user = {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hash_password(user.password),
        "created_at": datetime.utcnow()
    }
    
    users_db[user_id] = new_user
    
    return User(
        id=new_user["id"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        created_at=new_user["created_at"]
    )


@app.post("/login", response_model=Token)
async def login(user_credentials: LoginRequest):
    """
    Login with email and password
    
    Returns an access token for authenticated requests
    
    - **email**: User's email address
    - **password**: User's password
    """
    user = next((u for u in users_db.values() if u["email"] == user_credentials.email), None)
    
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== CRUD Endpoints ====================

@app.get("/users", response_model=List[User])
async def list_users(current_user: UserInDB = Depends(get_current_user)):
    """
    List all users (requires authentication)
    
    Returns a list of all registered users
    """
    return [
        User(
            id=u["id"],
            email=u["email"],
            full_name=u["full_name"],
            created_at=u["created_at"]
        )
        for u in users_db.values()
    ]


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, current_user: UserInDB = Depends(get_current_user)):
    """
    Get a specific user by ID (requires authentication)
    
    - **user_id**: The ID of the user to retrieve
    """
    user = users_db.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"]
    )


@app.get("/users/profile/me", response_model=User)
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get the current authenticated user's profile
    """
    return User(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at
    )


@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update a user's information (requires authentication)
    
    - **user_id**: The ID of the user to update
    - **full_name**: New full name (optional)
    - **email**: New email address (optional)
    """
    # Check if user exists
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is updating their own profile or is authorized
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    user = users_db[user_id]
    
    # Check if new email is already taken
    if user_update.email and user_update.email != user["email"]:
        if any(u["email"] == user_update.email for u in users_db.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user["email"] = user_update.email
    
    if user_update.full_name:
        user["full_name"] = user_update.full_name
    
    return User(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"]
    )


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: UserInDB = Depends(get_current_user)):
    """
    Delete a user (requires authentication)
    
    - **user_id**: The ID of the user to delete
    """
    # Check if user exists
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is deleting their own profile or is authorized
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own profile"
        )
    
    del users_db[user_id]
    return None


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
