from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    email: str

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

