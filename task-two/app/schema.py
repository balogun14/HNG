from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    userId: str

    class Config:
        orm_mode = True

class OrganisationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganisationCreate(OrganisationBase):
    pass

class Organisation(OrganisationBase):
    orgId: str

    class Config:
        orm_mode = True

class UserOrganisationCreate(BaseModel):
    userId: str
