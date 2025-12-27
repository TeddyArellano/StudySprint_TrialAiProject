"""
Capa de persistencia usando SQLite
"""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os


class Database:
    """Clase para gestionar la persistencia de datos"""
    
    def __init__(self, db_path: str = "data/study_agent.db"):
        """Inicializar la conexión a la base de datos"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def get_connection(self):
        """Obtener una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize(self):
        """Crear las tablas necesarias en la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de materias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de temas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)
        
        # Tabla de contenido de temas (PDFs procesados)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                source_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)
        
        # Tabla de historial de sesiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_subject(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Crear una nueva materia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO subjects (name, description) VALUES (?, ?)",
            (name, description)
        )
        subject_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return self.get_subject(subject_id)
    
    def get_subject(self, subject_id: int) -> Optional[Dict[str, Any]]:
        """Obtener una materia por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_subjects(self) -> List[Dict[str, Any]]:
        """Obtener todas las materias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM subjects ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def create_topic(self, subject_id: int, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Crear un nuevo tema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO topics (subject_id, name, description) VALUES (?, ?, ?)",
            (subject_id, name, description)
        )
        topic_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return self.get_topic(topic_id)
    
    def get_topic(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un tema por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.*, 
                   CASE WHEN tc.id IS NOT NULL THEN 1 ELSE 0 END as has_content
            FROM topics t
            LEFT JOIN topic_content tc ON t.id = tc.topic_id
            WHERE t.id = ?
        """, (topic_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_topics_by_subject(self, subject_id: int) -> List[Dict[str, Any]]:
        """Obtener todos los temas de una materia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.*,
                   CASE WHEN tc.id IS NOT NULL THEN 1 ELSE 0 END as has_content
            FROM topics t
            LEFT JOIN topic_content tc ON t.id = tc.topic_id
            WHERE t.subject_id = ?
            ORDER BY t.created_at DESC
        """, (subject_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def save_topic_content(self, topic_id: int, content: str, source_file: str):
        """Guardar el contenido extraído de un PDF"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO topic_content (topic_id, content, source_file) VALUES (?, ?, ?)",
            (topic_id, content, source_file)
        )
        
        conn.commit()
        conn.close()
    
    def get_topic_content(self, topic_id: int) -> Optional[str]:
        """Obtener el contenido de un tema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT content FROM topic_content WHERE topic_id = ? ORDER BY created_at DESC LIMIT 1",
            (topic_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['content']
        return None
    
    def record_session_completion(self, topic_id: int, duration: int, score: int, total_questions: int):
        """Registrar la finalización de una sesión de estudio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO study_sessions (topic_id, duration, score, total_questions) VALUES (?, ?, ?, ?)",
            (topic_id, duration, score, total_questions)
        )
        
        conn.commit()
        conn.close()
    
    def get_study_history(self, subject_id: int) -> List[Dict[str, Any]]:
        """Obtener el historial de estudio de una materia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ss.*, t.name as topic_name, s.name as subject_name
            FROM study_sessions ss
            JOIN topics t ON ss.topic_id = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE s.id = ?
            ORDER BY ss.completed_at DESC
        """, (subject_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_topic_statistics(self, topic_id: int) -> Dict[str, Any]:
        """Obtener estadísticas de un tema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calcular el promedio correcto: promedio de porcentajes individuales, no suma total
        cursor.execute("""
            SELECT 
                COUNT(*) as session_count,
                MAX(completed_at) as last_studied,
                AVG(CAST(score AS FLOAT) / CAST(total_questions AS FLOAT)) as avg_performance
            FROM study_sessions
            WHERE topic_id = ?
        """, (topic_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {"session_count": 0, "last_studied": None, "avg_performance": 0}
