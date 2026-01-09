"""
Authentication module for JWT token generation, password hashing, and user verification.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jwt import encode, decode, InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
import logging

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# Security scheme for FastAPI
security = HTTPBearer()


class PasswordManager:
    """Handles password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password using bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
        """
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False


class TokenManager:
    """Handles JWT token generation and verification."""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Dictionary containing token claims (should include 'sub' for user identifier)
            expires_delta: Optional timedelta for token expiration
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            logger.info(f"Access token created for user: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {str(e)}")
            raise
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            data: Dictionary containing token claims
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            logger.info(f"Refresh token created for user: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation error: {str(e)}")
            raise
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string to verify
            token_type: Expected token type ('access' or 'refresh')
            
        Returns:
            Decoded token payload dictionary
            
        Raises:
            HTTPException: If token is invalid, expired, or wrong type
        """
        try:
            payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected '{token_type}'",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Extract user identifier
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user identifier",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.info(f"Token verified for user: {user_id}")
            return payload
            
        except ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to extract and verify current user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from request
        
    Returns:
        Decoded token payload containing user information
        
    Raises:
        HTTPException: If token is invalid or user cannot be verified
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )
    
    token = credentials.credentials
    payload = TokenManager.verify_token(token, token_type="access")
    return payload


async def get_current_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Dependency to get only the user ID from current user.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        User ID string
    """
    return current_user.get("sub")


# Example usage helper
def create_token_response(user_id: str, additional_claims: Optional[Dict] = None) -> Dict[str, str]:
    """
    Create a token response with both access and refresh tokens.
    
    Args:
        user_id: User identifier to include in token
        additional_claims: Optional additional claims to include in token
        
    Returns:
        Dictionary with access_token, refresh_token, and token_type
    """
    claims = {"sub": user_id}
    if additional_claims:
        claims.update(additional_claims)
    
    access_token = TokenManager.create_access_token(claims)
    refresh_token = TokenManager.create_refresh_token(claims)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
