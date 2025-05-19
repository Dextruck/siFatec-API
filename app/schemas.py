from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    name: str
    username: str
    full_name: str
    email: str
    cpf: str
    password: str
    is_active: bool

class Users(UserBase):
    id: int
    is_active: bool
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class User(BaseModel):
    email: EmailStr
    disabled: bool = False

class UserInDB(User):
    hashed_password: str