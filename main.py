from fastapi import FastAPI, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import datetime
from datetime import timedelta
from sqlalchemy.orm import Session
from database_setup import User, Exercise, get_db, TrainingSession
from pathlib import Path
from fastapi.responses import FileResponse
from typing import Optional
from schemes import (
    User_Response,
    UserCreate,
    Exersice_Response,
    Token,  
    Exercise_Create, 
    TrainingSession_Response,
    TrainingSession_Create,
    TrainingSession_Response_Simple
    )
from security import (
    TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
    create_access_token,
    verify_password,
    get_password_hash
    )

app = FastAPI(title = 'GymTrack', description = 'A simple API for tracking gym workouts and progress', version = '1.0.0')

# ==== HTML фронт ====
BASE_DIR = Path(__file__).parent / 'html'

@app.get('/')
def index():
    return FileResponse(BASE_DIR / 'index.html')

@app.get('/login.html')
def login_page():
    return FileResponse(BASE_DIR / 'login.html')

@app.get('/register.html')
def register_page():
    return FileResponse(BASE_DIR / 'register.html')

@app.get('/dashboard.html')
def dashboard_page():
    return FileResponse(BASE_DIR / 'dashboard.html')

@app.get('/')
def root():
    return {'message': 'Welcome to GymTrack API!'}

#-----------------Users endpoints------------------

#-----------------Auth endpoints-------------------
@app.post('/api/register/', response_model=User_Response, status_code=status.HTTP_201_CREATED) 
def register_user(user:UserCreate, db: Session = Depends(get_db)):
    exist_user =  db.query(User).filter(User.email == user.email).first()

    if exist_user:
        raise HTTPException(status_code = 400, detail = 'User already exists')
    
    new_user = User(
        name = user.name,
        email = user.email,
        hashed_password = get_password_hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post('/api/token/', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect email or password')
    
    expires_delta = timedelta(TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email, "id": user.id}, expires_delta=expires_delta)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get('/api/users/me/', response_model=User_Response)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

#-----------------CRUD endpoints for training sessions-------------------

#creating training session (HTTP=POST, CRUD=CREATE)
@app.post('/api/users/me/training_sessions/', status_code=status.HTTP_201_CREATED)
def create_training_session(
    training_session: TrainingSession_Create,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    new_session = TrainingSession(
        type = training_session.type,
        user_id = current_user.id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session
    

#creating exercise for training session (HTTP=POST, CRUD=CREATE)
@app.post('/api/users/me/training_sessions/{session_id}/exercises/', response_model=Exersice_Response, status_code=status.HTTP_201_CREATED)
def add_exercise(
    session_id: int,
    exercise: Exercise_Create,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    print(exercise)
    new_exercise = Exercise(
        name = exercise.name,
        sets = exercise.sets,
        reps = exercise.reps,
        weight = exercise.weight,
        user_id = current_user.id,
        training_session_id = session_id
    )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise

#delete exercise from training session (HTTP=DELETE, CRUD=DELETE)
@app.delete('/api/users/me/training_sessions/{session_id}/exercises/{exercise_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    session_id: int,
    exercise_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):

    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id,
        Exercise.user_id == current_user.id,
        Exercise.training_session_id == session_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail='Exercise not found')
    
    db.delete(exercise)
    db.commit()

#update exercise (HTTP=PUT, CRUD=UPDATE)
@app.patch('/api/users/me/training_sessions/{session_id}/exercises/{exercise_id}', response_model=Exersice_Response)
def update_exercise(
    session_id: int,
    exercise_id: int,
    updated_exercise: Exersice_Response,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')
    
    update_data = updated_exercise.model_dump(exclude_unset=True)

    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id, 
        Exercise.user_id == current_user.id,
        Exercise.training_session_id == session_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail='Exercise not found')

    for key, value in update_data.items():
        setattr(exercise, key, value)
 
    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    return exercise

#get all exercises for training session (HTTP=GET, CRUD=READ)
@app.get('/api/users/me/training_sessions/{session_id}/exercises/', response_model=list[Exersice_Response])
def get_session_by_id(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    exercises = db.query(Exercise).filter(
        Exercise.user_id == current_user.id,
        Exercise.training_session_id == session_id
    ).all()

    return exercises

@app.get('/api/users/{user_id}', response_model=User_Response)
def get_user_by_id(
    user_id:int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    return user

@app.delete('/api/users/me/training_sessions/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_training_sessions(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):

    session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.user_id == current_user.id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail='Training session not found')
    
    db.delete(session)
    db.commit()

@app.get('/api/users/me/exercises/{name}', response_model=list[Exersice_Response])
def search_exercises_by_name(
    name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    exercises = db.query(Exercise).filter(
        Exercise.user_id == current_user.id,
        Exercise.name == name
    ).all()

    return exercises