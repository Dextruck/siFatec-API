from pydantic import BaseModel


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