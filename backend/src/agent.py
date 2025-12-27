"""
Núcleo del agente de estudio inteligente
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from src.database import Database
from src.llm_service import LLMService
from src.models import SessionResponse


class StudyAgent:
    """Agente inteligente que decide qué estudiar y genera sesiones personalizadas"""
    
    def __init__(self, database: Database):
        """Inicializar el agente con acceso a la base de datos"""
        self.db = database
        self.llm = LLMService()
    
    async def generate_study_session(
        self, 
        subject_id: int, 
        topic_id: Optional[int] = None,
        duration: int = 10
    ) -> SessionResponse:
        """Generar una sesión de estudio completa"""
        # Si no se especifica tema, seleccionar el óptimo
        if topic_id is None:
            topic_id = self.select_next_topic(subject_id)
            if topic_id is None:
                raise ValueError("No topics available for this subject")
        
        # Obtener información del tema
        topic = self.db.get_topic(topic_id)
        if not topic:
            raise ValueError("Topic not found")
        
        print(f"\n=== AGENT: Generating session for topic: {topic['name']} ===")
        
        # Obtener contenido del tema si existe
        topic_content = self.db.get_topic_content(topic_id)
        
        if topic_content:
            print(f"Topic has reference material: {len(topic_content)} chars")
            print(f"First 200 chars: {topic_content[:200]}...")
        else:
            print("No reference material found for topic")
        
        # Generar contenido de la sesión usando LLM
        session_content = await self.llm.generate_session_content(
            topic_name=topic['name'],
            topic_description=topic.get('description'),
            duration=duration,
            reference_material=topic_content
        )
        
        print(f"Session content generated:")
        print(f"  - Learning objective: {session_content['learning_objective'][:100]}...")
        print(f"  - Content length: {len(session_content['content'])} chars")
        print(f"  - Key concepts: {len(session_content['key_concepts'])} items")
        
        # Generar quiz
        quiz = await self.llm.generate_quiz(
            topic_name=topic['name'],
            content=session_content['content'],
            num_questions=3
        )
        
        return SessionResponse(
            topic_id=topic_id,
            topic_name=topic['name'],
            duration=duration,
            learning_objective=session_content['learning_objective'],
            content=session_content['content'],
            key_concepts=session_content['key_concepts'],
            quiz=quiz
        )
    
    def select_next_topic(self, subject_id: int) -> Optional[int]:
        """Seleccionar el siguiente tema a estudiar basado en heurísticas"""
        topics = self.db.get_topics_by_subject(subject_id)
        
        if not topics:
            return None
        
        # Calcular prioridad para cada tema
        topic_priorities = []
        
        for topic in topics:
            stats = self.db.get_topic_statistics(topic['id'])
            priority = self.calculate_topic_priority(topic, stats)
            topic_priorities.append((topic['id'], priority))
        
        # Ordenar por prioridad (mayor es mejor)
        topic_priorities.sort(key=lambda x: x[1], reverse=True)
        
        return topic_priorities[0][0]
    
    def calculate_topic_priority(self, topic: Dict[str, Any], stats: Dict[str, Any]) -> float:
        """Calcular la prioridad de un tema basado en múltiples factores"""
        priority = 0.0
        
        # Factor 1: Nunca estudiado tiene máxima prioridad
        if stats['session_count'] == 0:
            priority += 100.0
        else:
            # Factor 2: Tiempo desde el último estudio
            if stats['last_studied']:
                last_studied = datetime.fromisoformat(stats['last_studied'])
                days_since = (datetime.now() - last_studied).days
                priority += min(days_since * 5, 50)  # Máximo 50 puntos por recencia
            
            # Factor 3: Desempeño previo (menor desempeño = mayor prioridad)
            avg_performance = stats['avg_performance'] or 0
            priority += (1.0 - avg_performance) * 30  # Máximo 30 puntos por bajo desempeño
        
        # Factor 4: Tiene contenido cargado (PDFs)
        if topic.get('has_content'):
            priority += 10.0
        
        return priority
    
    def recommend_next_topics(self, subject_id: int, limit: int = 3) -> List[Dict[str, Any]]:
        """Recomendar los próximos temas a estudiar"""
        topics = self.db.get_topics_by_subject(subject_id)
        
        if not topics:
            return []
        
        # Calcular prioridad y estadísticas para cada tema
        recommendations = []
        
        for topic in topics:
            stats = self.db.get_topic_statistics(topic['id'])
            priority = self.calculate_topic_priority(topic, stats)
            
            recommendations.append({
                'topic_id': topic['id'],
                'topic_name': topic['name'],
                'priority_score': round(priority, 2),
                'times_studied': stats['session_count'],
                'last_studied': stats['last_studied'],
                'average_performance': round(stats['avg_performance'] * 100, 1) if stats['avg_performance'] else None,
                'reason': self.get_recommendation_reason(topic, stats)
            })
        
        # Ordenar por prioridad
        recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return recommendations[:limit]
    
    def get_recommendation_reason(self, topic: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """Generar una razón legible para la recomendación"""
        if stats['session_count'] == 0:
            return "Nunca estudiado"
        
        reasons = []
        
        # Verificar recencia
        if stats['last_studied']:
            last_studied = datetime.fromisoformat(stats['last_studied'])
            days_since = (datetime.now() - last_studied).days
            
            if days_since > 7:
                reasons.append(f"Estudiado hace {days_since} dias")
            elif days_since > 1:
                reasons.append(f"Estudiado hace {days_since} dias")
        
        # Verificar desempeño
        if stats['avg_performance'] and stats['avg_performance'] < 0.7:
            performance_pct = round(stats['avg_performance'] * 100)
            reasons.append(f"Desempeno promedio: {performance_pct}%")
        
        # Si no hay razones específicas
        if not reasons:
            return "Listo para repasar"
        
        return ", ".join(reasons)
