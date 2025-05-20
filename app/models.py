from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func, Index, UniqueConstraint, Time
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

# Primary key e auto incremento
class PrimaryKey:
    id = Column(Integer, primary_key=True, autoincrement=True)

# Soft Delete e auditoria
class AuditMixin:
    created_at = Column(DateTime(), default=datetime.utcnow)
    updated_at = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime(), nullable=True)


# User
class User(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'users'
    name = Column(String)
    username = Column(String(30), unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    cpf = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean)

    profile = relationship('UsersProfiles', back_populates='user', uselist=False)
    roles = relationship('UsersRoles', back_populates='user')
    notifications = relationship('NotificationsUsers', back_populates='user')
    received_notifications = relationship('Notification', secondary='notifications_users', back_populates='receivers')
    student_periods = relationship('StudentPeriod', back_populates='user')

class UsersProfiles(Base, AuditMixin):
    __tablename__ = 'users_profiles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    registration_number = Column(String)
    father_name = Column(String(255))
    mother_name = Column(String(255))
    personal_phone = Column(String(15))
    work_phone = Column(String(15))
    birth_date = Column(DateTime())
    institution_id = Column(Integer, ForeignKey('institutions.id'))

    user = relationship('User', back_populates='profile')
    institution = relationship('Institution')

class Subject(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'subjects'
    name = Column(String, index=True)
    syllabus = Column(String)
    workload_hours = Column(Integer)
    class_duration_minutes = Column(Integer)

    class_group = relationship('ClassGroup', back_populates='subject')
    sessions = relationship('ClassSessions', back_populates='subject')

class Course(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'courses'
    name = Column(String(255), index=True)
    duration_years = Column(Integer)
    degree = Column(String(255))

    enrollments = relationship('Enrollment', back_populates='course')
    sessions = relationship('ClassSessions', back_populates='course')

class SchoolYear(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'school_years'
    year = Column(Integer, unique=True)
    start_date = Column(DateTime())
    end_date = Column(DateTime())

    periods = relationship('Period', back_populates='school_year')

class Period(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'periods'
    name = Column(String(255))
    school_year_id = Column(Integer, ForeignKey('school_years.id'))
    start_date = Column(DateTime())
    end_date = Column(DateTime())

    school_year = relationship('SchoolYear', back_populates='periods')
    class_groups = relationship('ClassGroup', back_populates='period')
    sessions = relationship('ClassSessions', back_populates='period')
    student_periods = relationship('StudentPeriod', back_populates='period')

class Shifts(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'shifts'
    name = Column(String(255))

    sessions = relationship('ClassSchedule', back_populates='shift')

class WeekDay(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'week_days'
    name = Column(String(255), unique=True)

    sessions = relationship('ClassSessions', back_populates='week_day')

class States(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'states'
    name = Column(String(255), unique=True)
    acronym = Column(String(5), unique=True)

    institutions = relationship('Institution', back_populates='state')

class Institution(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'institutions'
    name = Column(String(255))
    city = Column(String(255))
    state_id = Column(Integer, ForeignKey('states.id'))
    address = Column(String(255))
    is_active = Column(Boolean)

    state = relationship('States', back_populates='institutions')
    class_groups = relationship('ClassGroup', back_populates='institution')

class ClassGroup(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'class_groups'
    name = Column(String(255))
    period_id = Column(Integer, ForeignKey('periods.id'))
    institution_id = Column(Integer, ForeignKey('institutions.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))

    period = relationship('Period', back_populates='class_groups')
    institution = relationship('Institution', back_populates='class_groups')
    enrollments = relationship('Enrollment', back_populates='class_group')
    sessions = relationship('ClassSessions', back_populates='class_group')
    subject = relationship('Subject', back_populates='class_group')

class ClassSchedule(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'class_schedules'
    start_time = Column(Time())
    end_time = Column(Time())
    shift_id = Column(Integer, ForeignKey('shifts.id'))

    shift = relationship('Shifts', back_populates='sessions')
    sessions = relationship('ClassSessions', back_populates='schedule')

class ClassSessions(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'class_sessions'
    teacher_id = Column(Integer)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    class_group_id = Column(Integer, ForeignKey('class_groups.id'))
    period_id = Column(Integer, ForeignKey('periods.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    class_schedule_id = Column(Integer, ForeignKey('class_schedules.id'))
    location = Column(String(255))
    week_day_id = Column(Integer, ForeignKey('week_days.id'))

    subject = relationship('Subject', back_populates='sessions')
    class_group = relationship('ClassGroup', back_populates='sessions')
    period = relationship('Period', back_populates='sessions')
    course = relationship('Course', back_populates='sessions')
    schedule = relationship('ClassSchedule', back_populates='sessions')
    week_day = relationship('WeekDay', back_populates='sessions')
    absences = relationship('StudentAbsences', back_populates='class_session')

class StudentAbsences(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'student_absences'
    class_id = Column(Integer, ForeignKey('class_sessions.id'))
    enrollment_id = Column(Integer, ForeignKey('enrollments.id'))
    justify = Column(Boolean)
    justify_types = Column(Integer)

    enrollment = relationship('Enrollment', back_populates='absences')
    class_session = relationship('ClassSessions', back_populates='absences')

class EnrollmentsStatus(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'enrollments_status'
    status = Column(String(255), unique=True)

    enrollments = relationship('Enrollment', back_populates='status')

class Enrollment(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'enrollments'
    student_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    class_group_id = Column(Integer, ForeignKey('class_groups.id'))
    status_id = Column(Integer, ForeignKey('enrollments_status.id'))

    student = relationship('User')
    course = relationship('Course', back_populates='enrollments')
    class_group = relationship('ClassGroup', back_populates='enrollments')
    status = relationship('EnrollmentsStatus', back_populates='enrollments')
    absences = relationship('StudentAbsences', back_populates='enrollment')

class StudentPeriod(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'student_periods'

    user_id = Column(Integer, ForeignKey('users.id'))
    period_id = Column(Integer, ForeignKey('periods.id'))
    course_period = Column(Integer)  # Ex: 5 para 5º semestre

    user = relationship('User', back_populates='student_periods')
    period = relationship('Period', back_populates='student_periods')

class Role(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'roles'
    name = Column(String(255), nullable=False, unique=True)

    permissions = relationship('RolePermission', back_populates='role')
    users = relationship('UsersRoles', back_populates='role')

class UsersRoles(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'users_roles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)

    user = relationship('User', back_populates='roles')
    role = relationship('Role', back_populates='users')

class Permission(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'permissions'
    permission = Column(String(255), unique=True)
    description = Column(String)

    roles = relationship('RolePermission', back_populates='permission')

class RolePermission(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'role_permissions'
    role_id = Column(Integer, ForeignKey('roles.id'))
    permission_id = Column(Integer, ForeignKey('permissions.id'))

    role = relationship('Role', back_populates='permissions')
    permission = relationship('Permission', back_populates='roles')

class Notification(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'notifications'
    title = Column(String(50))
    text = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User")
    receivers = relationship("User", secondary="notifications_users", back_populates="received_notifications")

class NotificationsUsers(PrimaryKey, Base, AuditMixin):
    __tablename__ = 'notifications_users'
    notifications_id = Column(Integer, ForeignKey('notifications.id'))
    users_id = Column(Integer, ForeignKey('users.id'))

    notification = relationship('Notification')
    user = relationship('User', back_populates='notifications')
