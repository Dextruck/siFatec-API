from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time


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



class AssessmentInstrumentSchema(BaseModel):
    description: str
    weight: int
    application_date: datetime
    score: Optional[int]

class ScoreInfo(BaseModel):
    subject: str
    assessment_instruments: list[AssessmentInstrumentSchema]

class AbsencesInfo(BaseModel):
    subject: str
    presences: int
    absences: int

class ClassInfo(BaseModel):
    subject_name: str
    acronym: str
    teacher: str
    start_time: time
    end_time: time
    local: str

class ScheduleInfo(BaseModel):
    week_day: str
    subjects: list[ClassInfo]



# class AssessmentInstrument:
#     date: str
#     value: float
#     desc: str


# Usado para retornar as notas do usuário
# class Scores(BaseModel):
#     subject:
#     assessment_instrument