from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime



class UserCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=128)
    last_name: str = Field(min_length=2, max_length=128)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


    @field_validator("first_name", "last_name")
    def validate_name(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Name must contain only letters")
        return value


    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        return value
    

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(min_length=2, max_length=128)
    last_name: Optional[str] = Field(min_length=2, max_length=128)
    email: Optional[EmailStr]
    password: Optional[str] = Field(min_length=8, max_length=128)
    

    @field_validator("first_name", "last_name")
    def validate_name(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Name must contain only letters")
        return value


    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        return value
    

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

