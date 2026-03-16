from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime as dt
from typing import List, Optional

engine = create_engine('sqlite:///GymTrack.db')
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()


#creating tables
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, index = True)
    email = Column(String, unique = True, index = True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default = True)
    training_sessions = relationship('Exercise', back_populates = 'user')

class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(Integer, primary_key = True, autoincrement=True, index = True)
    name = Column(String, index = True)
    sets = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float)
    date = Column(DateTime, default = dt.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates = 'training_sessions')
#    sessions = relationship('TrainingSession', back_populates = 'exercises')

'''class TrainingSession(Base):
    __tablename__ = 'training_sessions'
    id = Column(Integer, primary_key = True, autoincrement=True, index = True)
    date = Column(DateTime, default = DateTime.now)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates = 'training_sessions')
    exercises = relationship('Exercise', back_populates = 'sessions')'''

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()