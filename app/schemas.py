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

class UserToken(UserBase):
    name: str
    username: str
    full_name: str
    email: str
    cpf: str
    password: str
    is_active: bool
    id: int

class Users(UserBase):
    id: int
    is_active: bool
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

class AuthenticatedUser(BaseModel):
    user: UserToken
    role_id: list[int]

class UserRole(BaseModel):
    user_id: int
    role_id: int

    model_config = {
        "from_attributes": True
    }

# Usado para retornar os dados da tela inicial
class UserProfile(BaseModel):
    name: str
    registration_number: str
    student_period: int