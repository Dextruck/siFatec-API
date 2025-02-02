from pydantic import BaseModel


class UserBase(BaseModel):
    email: str




class UserCreate(UserBase):
    password: str
    email: str
    name: str




class User(UserBase):
    d: int
    is_active: bool
    class Config:
        orm_mode = True