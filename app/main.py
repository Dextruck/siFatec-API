from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .db import get_db

from . import actions, models, schemas
from .database import SessionLocal, engine
from .auth import authenticate_user, create_access_token, get_home_profile, token_info_validate

# Cria as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

# Inicializa a aplicação FastAPI
app = FastAPI()

# Rota para criar um usuário
@app.post("/users/", response_model=schemas.Users)
def create_user(users: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = actions.get_user_by_email(db, email=users.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return actions.create_user(db=db, user=users)

# Rota para listar usuários
@app.get("/users/", response_model=list[schemas.Users])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = actions.get_users(db, skip=skip, limit=limit)
    return users

# Rota para obter um usuário específico pelo ID
@app.get("/users/{user_id}", response_model=schemas.Users)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = actions.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Rota de login e criação de token
@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.user.id), "email":user.user.email, "role":user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

# Rota para buscar infos da tela inicial
@app.get("/profile", response_model= schemas.UserProfile)
async def home_profile(current_user: models.User = Depends(get_home_profile)):
    return current_user


# Rota para buscar notas do usuário
# Para finalizar ainda é necessário criar identificação de semestre
@app.get("/students/scores", response_model= list[schemas.ScoreInfo])
def get_student_scores(token: dict = Depends(token_info_validate), db: Session = Depends(get_db)):
    user_id = int(token.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    result = {}

    for enrollment in user.enrollments:
        subject = enrollment.class_group.subject
        subject_name = subject.name

        instruments = enrollment.class_group.assessment_instruments

        assessments = []
        for instrument in instruments:
            score = next((s.value for s in instrument.scores if s.enrollment_id == enrollment.id), None)
            assessments.append({
                "instrument_id": instrument.id,
                "description": instrument.description,
                "application_date": instrument.application_date,
                "weight": instrument.weight,
                "score": score
            })

        if subject_name not in result:
            result[subject_name] = {
                "subject": subject_name,
                "assessment_instruments": assessments
            }
        else:
            result[subject_name]["assessment_instruments"].extend(assessments)
    
    print(list(result.values()))
    return list(result.values())



# Rota para buscar as faltas do usuário
# Para finalizar ainda é necessário criar identificação de semestre
@app.get("/students/absences", response_model= list[schemas.AbsencesInfo])
def get_student_absences(token: dict = Depends(token_info_validate), db: Session = Depends(get_db)):

    user_id = int(token.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    result = {}

    for enrollment in user.enrollments:

        subject = enrollment.class_group.subject
        subject_name = subject.name
        class_sessions = enrollment.class_group.sessions    

        classes = 0
        absences = 0

        for class_session in class_sessions:
            classes += 1
            for ab in class_session.absences:
                absences += 1

        result[subject_name] = {
            "subject": subject_name,
            "presences": classes - absences,
            "absences": absences
        }
    
    return list(result.values())


@app.get("/students/schedule")
def get_schedule(db: Session = Depends(get_db), token: dict = Depends(token_info_validate)):
    user_id = int(token.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    schedule_by_day = {}
    sessions = []

    for enrollment in user.enrollments:
        sessions.append(enrollment.class_group.sessions)
    
    lista_flat = [item for sublista in sessions for item in sublista]

    sessions = lista_flat

    for session in sessions:
        if not session.class_group or not session.week_day or not session.schedule:
            continue

        week_day_name = session.week_day.name.lower()

        # Garante que a lista de disciplinas para o dia da semana existe
        if week_day_name not in schedule_by_day:
            schedule_by_day[week_day_name] = []

        disciplinas = schedule_by_day[week_day_name]

        # Verifica se já existe uma disciplina nesse mesmo horário
        if any(d.start_time == session.schedule.start_time for d in disciplinas):
            continue  # pula se já houver uma com o mesmo horário

        disciplina_info = schemas.ClassInfo(
            subject_name = session.class_group.subject.name,
            acronym = session.class_group.subject.syllabus,
            teacher = session.class_group.teacher.name if session.class_group.teacher else "Professor não definido",
            start_time = session.schedule.start_time,
            end_time = session.schedule.end_time,
            local = session.location if session.location else "Local não definido"
        )

        disciplinas.append(disciplina_info)
        schedule_by_day[week_day_name] = disciplinas

    # Monta a lista final ordenada por dias da semana (opcional)
    dias_ordenados = [
        "segunda-feira", "terça-feira", "quarta-feira", 
        "quinta-feira", "sexta-feira", "sábado", "domingo"
    ]

    resultado = [
        {
            "dia_da_semana": dia,
            "disciplinas": sorted(schedule_by_day[dia], key=lambda d: d.start_time)
        }
        for dia in dias_ordenados if dia in schedule_by_day
    ]

    return resultado

















# @app.get("/students/schedule")
# def get_student_schedule(token: dict = Depends(token_info_validate), db: Session = Depends(get_db)):
#     user_id = int(token.get("sub"))
#     user = db.query(models.User).filter(models.User.id == user_id).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado")

#     # Mapeia os dias da semana para garantir ordem e nomes fixos
#     week_days_map = {
#         "domingo": [],
#         "segunda-feira": [],
#         "terça-feira": [],
#         "quarta-feira": [],
#         "quinta-feira": [],
#         "sexta-feira": [],
#         "sábado": []
#     }

#     for enrollment in user.enrollments:
#         class_group = enrollment.class_group
#         if not class_group:
#             continue

#         subject = class_group.subject
#         teacher = class_group.teacher

#         for session in class_group.sessions:

#             week_day_name = session.week_day.name.lower()

#             schedule = session.schedule


#             disciplina_info = schemas.ClassInfo(
#                 subject_name = subject.name,
#                 acronym = subject.syllabus,
#                 teacher = teacher.full_name if teacher else "Professor não definido",
#                 start_time = schedule.start_time,
#                 end_time = schedule.end_time,
#                 local = session.location
#             )

#             if week_day_name in week_days_map:
#                 print('aquiiiiii')
#                 week_days_map[week_day_name].append(disciplina_info)

#     # Monta a lista final
#     resultado = []
#     for dia, disciplinas in week_days_map.items():
#         if disciplinas:
#             resultado.append({
#                 "dia_da_semana": dia,
#                 "disciplinas": disciplinas
#             })
#     return resultado


















    #return resultado
# Rota para buscar a agenda semanal do usuário
# @app.get("/students/schedule", response_model= str)#list[schemas.ScheduleInfo])
# def get_student_schedule(token: dict = Depends(token_info_validate), db: Session = Depends(get_db)):

#     user_id = int(token.get("sub"))
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
#     result = {}

#     active_enrollments = [enrollment for enrollment in user.enrollments if enrollment.status_id == 1]
#     class_groups = [enr.class_group for enr in active_enrollments]

#     print(class_groups)
#     return 'test'

    # for enrollment in user.enrollments:

    #     subject = enrollment.class_group.subject
    #     subject_name = subject.name
    #     class_sessions = enrollment.class_group.sessions    

    #     classes = 0
    #     absences = 0

    #     for class_session in class_sessions:
    #         classes += 1
    #         for ab in class_session.absences:
    #             absences += 1

    #     result[subject_name] = {
    #         "subject": subject_name,
    #         "presences": classes - absences,
    #         "absences": absences
    #     }
    
    # return list(result.values())