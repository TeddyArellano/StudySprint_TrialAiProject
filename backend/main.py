"""
FastAPI backend principal para el agente de estudio
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

from src.models import (
    Subject, Topic, StudySession, QuizResult,
    SubjectCreate, TopicCreate, SessionRequest, SessionResponse
)
from src.database import Database
from src.agent import StudyAgent
from src.pdf_processor import PDFProcessor

app = FastAPI(title="Study Sprint Agent API", version="1.0.0")

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
db = Database()
agent = StudyAgent(db)
pdf_processor = PDFProcessor()


@app.on_event("startup")
async def startup_event():
    """Inicializar la base de datos al arrancar la aplicación"""
    db.initialize()


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Study Sprint Agent API", "status": "running"}


@app.post("/subjects", response_model=Subject)
async def create_subject(subject: SubjectCreate):
    """Crear una nueva materia"""
    return db.create_subject(subject.name, subject.description)


@app.get("/subjects", response_model=List[Subject])
async def get_subjects():
    """Obtener todas las materias"""
    return db.get_all_subjects()


@app.get("/subjects/{subject_id}", response_model=Subject)
async def get_subject(subject_id: int):
    """Obtener una materia específica"""
    subject = db.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@app.post("/subjects/{subject_id}/topics", response_model=Topic)
async def create_topic(subject_id: int, topic: TopicCreate):
    """Crear un nuevo tema para una materia"""
    subject = db.get_subject(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return db.create_topic(subject_id, topic.name, topic.description)


@app.get("/subjects/{subject_id}/topics", response_model=List[Topic])
async def get_topics(subject_id: int):
    """Obtener todos los temas de una materia"""
    return db.get_topics_by_subject(subject_id)


@app.post("/subjects/{subject_id}/topics/{topic_id}/upload")
async def upload_material(subject_id: int, topic_id: int, file: UploadFile = File(...)):
    """Subir material PDF para un tema"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Leer y procesar el PDF
    content = await file.read()
    extracted_text = pdf_processor.extract_text(content)
    
    if not extracted_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    
    # Guardar el contenido del PDF
    db.save_topic_content(topic_id, extracted_text, file.filename)
    
    return {"message": "Material uploaded successfully", "filename": file.filename}


@app.post("/session/generate", response_model=SessionResponse)
async def generate_session(request: SessionRequest):
    """Generar una nueva sesión de estudio"""
    try:
        print(f"\n=== GENERATING SESSION ===")
        print(f"Subject ID: {request.subject_id}")
        print(f"Topic ID: {request.topic_id}")
        print(f"Duration: {request.duration}")
        
        session = await agent.generate_study_session(
            subject_id=request.subject_id,
            topic_id=request.topic_id,
            duration=request.duration
        )
        
        print(f"\n=== SESSION GENERATED ===")
        print(f"Topic: {session.topic_name}")
        print(f"Learning Objective: {session.learning_objective[:100]}...")
        print(f"Content Length: {len(session.content)} chars")
        print(f"Key Concepts: {len(session.key_concepts)} items")
        print(f"Quiz Questions: {len(session.quiz)} questions")
        
        return session
    except Exception as e:
        print(f"\n=== ERROR GENERATING SESSION ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session/complete")
async def complete_session(result: QuizResult):
    """Registrar la finalización de una sesión de estudio"""
    db.record_session_completion(
        topic_id=result.topic_id,
        duration=result.duration,
        score=result.score,
        total_questions=result.total_questions
    )
    return {"message": "Session recorded successfully"}


@app.get("/history/{subject_id}")
async def get_study_history(subject_id: int):
    """Obtener el historial de estudio de una materia"""
    return db.get_study_history(subject_id)


@app.get("/recommendations/{subject_id}")
async def get_recommendations(subject_id: int):
    """Obtener recomendaciones de temas para estudiar"""
    recommendations = agent.recommend_next_topics(subject_id, limit=3)
    return {"recommendations": recommendations}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
