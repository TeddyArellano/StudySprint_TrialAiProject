"""
Modelos de datos Pydantic para el sistema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SubjectCreate(BaseModel):
    """Modelo para crear una nueva materia"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class Subject(BaseModel):
    """Modelo de materia"""
    id: int
    name: str
    description: Optional[str]
    created_at: str


class TopicCreate(BaseModel):
    """Modelo para crear un nuevo tema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class Topic(BaseModel):
    """Modelo de tema"""
    id: int
    subject_id: int
    name: str
    description: Optional[str]
    has_content: bool = False
    created_at: str


class SessionRequest(BaseModel):
    """Solicitud para generar una sesión de estudio"""
    subject_id: int
    topic_id: Optional[int] = None
    duration: int = Field(..., ge=5, le=15)


class QuizQuestion(BaseModel):
    """Pregunta de quiz"""
    question: str
    options: List[str]
    correct_answer: int


class SessionResponse(BaseModel):
    """Respuesta con el contenido de una sesión de estudio"""
    topic_id: int
    topic_name: str
    duration: int
    learning_objective: str
    content: str
    key_concepts: List[str]
    quiz: List[QuizQuestion]


class QuizResult(BaseModel):
    """Resultado de un quiz completado"""
    topic_id: int
    duration: int
    score: int
    total_questions: int


class StudySession(BaseModel):
    """Registro histórico de una sesión de estudio"""
    id: int
    topic_id: int
    topic_name: str
    subject_name: str
    duration: int
    score: int
    total_questions: int
    completed_at: str
