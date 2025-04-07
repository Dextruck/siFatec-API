from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base

# Definição da classe User
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String(30))
    full_name = Column(String)
    email = Column(String, unique=True)
    cpf = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())
    profile = relationship('UserProfile', back_populates='user', uselist=False)
    roles = relationship('RoleUser', back_populates='user')

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    registration_number = Column(String)
    father_name = Column(String(255))
    mother_name = Column(String(255))
    personal_phone = Column(String(15))
    work_phone = Column(String(15))
    birth_date = Column(DateTime())
    institution_id = Column(Integer, ForeignKey('institutions.id'))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    user = relationship('User', back_populates='profile')

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    syllabus = Column(String)
    workload_hours = Column(Integer)
    class_duration_minutes = Column(Integer)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    duration_years = Column(Integer)
    degree = Column(String(255))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class SchoolYear(Base):
    __tablename__ = 'school_years'
    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    start_date = Column(DateTime())
    end_date = Column(DateTime())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class Period(Base):
    __tablename__ = 'periods'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    school_year_id = Column(Integer, ForeignKey('school_years.id'))
    start_date = Column(DateTime())
    end_date = Column(DateTime())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class Shift(Base):
    __tablename__ = 'shifts'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class WeekDay(Base):
    __tablename__ = 'week_days'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class Institution(Base):
    __tablename__ = 'institutions'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    city = Column(String(255))
    state = Column(String(2))
    address = Column(String(255))
    is_active = Column(Boolean)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class ClassGroup(Base):
    __tablename__ = 'class_groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    period_id = Column(Integer, ForeignKey('periods.id'))
    institution_id = Column(Integer, ForeignKey('institutions.id'))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class ClassSchedule(Base):
    __tablename__ = 'class_schedules'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime())
    end_time = Column(DateTime())

class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    teacher_id = Column(String)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    class_group_id = Column(Integer, ForeignKey('class_groups.id'))
    institution_id = Column(Integer, ForeignKey('institutions.id'))
    shift_id = Column(Integer, ForeignKey('shifts.id'))
    period_id = Column(Integer, ForeignKey('periods.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    class_schedule_id = Column(Integer, ForeignKey('class_schedules.id'))
    location = Column(String(255))
    week_day_id = Column(Integer, ForeignKey('week_days.id'))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class Absence(Base):
    __tablename__ = 'absences'
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.id'))
    enrollment_id = Column(Integer, ForeignKey('enrollments.id'))
    justify = Column(Boolean)
    justify_types = Column(Integer)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class EnrollmentStatus(Base):
    __tablename__ = 'enrollment_statuses'
    id = Column(Integer, primary_key=True)
    status = Column(String(255))

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True)
    student_id = Column(String)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    class_group_id = Column(Integer, ForeignKey('class_groups.id'))
    status_id = Column(Integer, ForeignKey('enrollment_statuses.id'))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class RoleUser(Base):
    __tablename__ = 'role_user'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())
    user = relationship('User', back_populates='roles')

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    permission = Column(String(255))
    description = Column(String)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    permission_id = Column(Integer, ForeignKey('permissions.id'))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    deleted_at = Column(DateTime())