from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from .db import get_db
from collections import defaultdict
from datetime import datetime

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
# Para finalizar: modularizar funções, adicionar verificações e HTTPExceptions
@app.get("/students/scores", response_model= list[schemas.ScoreInfo])
def get_student_scores(token: dict = Depends(token_info_validate), db: Session = Depends(get_db)):
    user_id = int(token.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    result = {}

    for enrollment in user.enrollments:

        if enrollment.status_id != 1:
            continue

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
# Para finalizar: modularizar funções, adicionar verificações e HTTPExceptions
@app.get("/students/absences", response_model= list[schemas.AbsencesInfo])
def get_student_absences(token: dict = Depends(token_info_validate), db: Session = Depends(get_db)):

    user_id = int(token.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    result = {}

    for enrollment in user.enrollments:

        if enrollment.status_id != 1:
            continue

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


# Rota para buscar a agenda semanal do aluno
# Para finalizar: modularizar funções, adicionar verificações e HTTPExceptions
@app.get("/students/schedule", response_model= list[schemas.ScheduleInfo])
def get_student_schedule(db: Session = Depends(get_db), token: dict = Depends(token_info_validate)):
    user_id = int(token.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    schedule_by_day = {}
    sessions = []

    for enrollment in user.enrollments:
        sessions.append(enrollment.class_group.sessions)
    
    flat_list = [item for sublist in sessions for item in sublist]

    sessions = flat_list

    for session in sessions:
        if not session.class_group or not session.week_day or not session.schedule:
            continue

        week_day_name = session.week_day.name.lower()

        # Garante que a lista de disciplinas para o dia da semana existe
        if week_day_name not in schedule_by_day:
            schedule_by_day[week_day_name] = []

        subjects = schedule_by_day[week_day_name]

        # Verifica se já existe uma disciplina nesse mesmo horário
        if any(d.start_time == session.schedule.start_time for d in subjects):
            continue  # pula se já houver uma com o mesmo horário

        subject_info = schemas.ClassInfo(
            subject_name = session.class_group.subject.name,
            acronym = session.class_group.subject.syllabus,
            teacher = session.class_group.teacher.name if session.class_group.teacher else "Professor não definido",
            start_time = session.schedule.start_time,
            end_time = session.schedule.end_time,
            local = session.location if session.location else "Não definido"
        )

        subjects.append(subject_info)
        schedule_by_day[week_day_name] = subjects

    # Monta a lista final ordenada por dias da semana (opcional)
    sorted_days = [
        "segunda-feira", "terça-feira", "quarta-feira", 
        "quinta-feira", "sexta-feira", "sábado", "domingo"
    ]

    result = [
        {
            "week_day": day,
            "subjects": sorted(schedule_by_day[day], key=lambda d: d.start_time)
        }
        for day in sorted_days if day in schedule_by_day
    ]

    return result

# Rota para buscar o historico do aluno
# Para finalizar: modularizar funções, adicionar verificações e HTTPExceptions
@app.get("/students/history", response_model=List[schemas.HistoryInfo])
def get_student_history(token: dict = Depends(token_info_validate), db: Session = Depends(get_db)):
    user_id = int(token.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    history = {}

    for enrollment in user.enrollments:
        if enrollment.status_id != 3:
            continue

        year = enrollment.class_group.period.school_year.year
        period = enrollment.class_group.period.name
        key = f"{year}-{period}"

        if key not in history:
            history[key] = {
                "year": year,
                "period": period,
                "subjects": []
            }

        subject = enrollment.class_group.subject
        subject_name = subject.name
        acronym = subject.syllabus

        instruments = enrollment.class_group.assessment_instruments
        total_weight = 0
        weighted_sum = 0

        for instrument in instruments:
            score = next((s.value for s in instrument.scores if s.enrollment_id == enrollment.id and s.value is not None), None)
            if score is not None:
                weight = instrument.weight
                weighted_sum += score * weight
                total_weight += weight

        avg_score = round(weighted_sum / total_weight, 2) if total_weight > 0 else None

        class_sessions = enrollment.class_group.sessions
        total_classes = len(class_sessions)
        total_absences = sum(
            1 for session in class_sessions for ab in session.absences if ab.enrollment_id == enrollment.id
        )
        attendance_percent = round(((total_classes - total_absences) / total_classes) * 100, 2) if total_classes > 0 else None

        history[key]["subjects"].append({
            "subject_name": subject_name,
            "acronym": acronym,
            "attendance": attendance_percent,
            "avarage_score": avg_score
        })

    return [schemas.HistoryInfo(**item) for item in history.values()]


# create message
@app.post("/messages/", response_model=schemas.MessageOut)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.id.in_(message.user_ids)).all()

    if len(users) != len(set(message.user_ids)):
        raise HTTPException(status_code=400, detail="Um ou mais usuários não foram encontrados.")

    db_message = models.Message(titulo=message.titulo, mensagem=message.mensagem)
    db_message.destinatarios = users
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return {
        "id": db_message.id,
        "titulo": db_message.titulo,
        "mensagem": db_message.mensagem,
        "created_at": db_message.created_at,
        "user_ids": [user.id for user in db_message.destinatarios]
    }


# get messages
@app.get("/students/messages", response_model=List[schemas.GroupedMessagesResponse])
def get_user_messages(db: Session = Depends(get_db), token: dict = Depends(token_info_validate)):
    user_id = int(token.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    

    messages = user.mensagens_recebidas

    # Ordenar mensagens por created_at
    messages.sort(key=lambda m: m.created_at, reverse=False)  # ou reverse=True se quiser mais recentes primeiro

    # Agrupar por dia (formato "dd/mm/yyyy")
    grouped = defaultdict(list)
    for m in messages:
        day_str = m.created_at.strftime("%d/%m/%Y")
        grouped[day_str].append({
            "id": m.id,
            "titulo": m.titulo,
            "mensagem": m.mensagem,
            "created_at": m.created_at,
            "user_ids": [u.id for u in m.destinatarios]
        })

    # Retornar como lista de dicionários
    result = [
        {"day": day, "messages": msgs}
        for day, msgs in grouped.items()
    ]

    # Ordenar grupos por data (mais recente primeiro, se quiser)
    result.sort(key=lambda g: datetime.strptime(g["day"], "%d/%m/%Y"), reverse=True)

    return result
