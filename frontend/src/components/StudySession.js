import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { sessionAPI, subjectsAPI } from '../api/api';

function StudySession({ subject, selectedTopic, preferredDuration, onComplete, onBack }) {
  const [duration, setDuration] = useState(preferredDuration || 10);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  
  // Estados para el timer
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [initialTime, setInitialTime] = useState(0);
  const [timerActive, setTimerActive] = useState(false);
  
  // Estados para el selector manual
  const [allSubjects, setAllSubjects] = useState([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState(null);
  const [availableTopics, setAvailableTopics] = useState([]);
  const [selectedTopicId, setSelectedTopicId] = useState(null);

  useEffect(() => {
    console.log('StudySession useEffect running...');
    console.log('Props - selectedTopic:', selectedTopic, 'subject:', subject);
    
    // Si hay un tema seleccionado (sesión aleatoria desde inicio), generar automáticamente
    if (selectedTopic && subject) {
      console.log('Auto-generating session with topic:', selectedTopic.id, 'subject:', subject.id);
      handleGenerateSessionWithTopic(selectedTopic.id, subject.id);
    } else if (!selectedTopic) {
      // Si no hay tema seleccionado, cargar materias para el selector
      console.log('Loading subjects for manual selection');
      loadSubjectsAndRandomSelect();
    }
  }, []);

  // Timer countdown effect
  useEffect(() => {
    if (!timerActive || timeRemaining <= 0) return;
    
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          setTimerActive(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [timerActive, timeRemaining]);

  // Iniciar timer cuando se genera la sesión
  useEffect(() => {
    if (session && !showResults) {
      const totalSeconds = session.duration * 60;
      setInitialTime(totalSeconds);
      setTimeRemaining(totalSeconds);
      setTimerActive(true);
    }
  }, [session, showResults]);

  const loadSubjectsAndRandomSelect = async () => {
    try {
      console.log('Loading subjects for manual selection...');
      const response = await subjectsAPI.getAll();
      const subjects = response.data;
      console.log('Subjects loaded:', subjects);
      setAllSubjects(subjects);
      
      if (subjects.length > 0) {
        // Seleccionar materia aleatoria
        const randomSubject = subjects[Math.floor(Math.random() * subjects.length)];
        console.log('Random subject selected:', randomSubject);
        setSelectedSubjectId(randomSubject.id);
        
        // Cargar temas de esa materia
        const topicsResponse = await subjectsAPI.getTopics(randomSubject.id);
        const topics = topicsResponse.data;
        console.log('Topics loaded:', topics);
        setAvailableTopics(topics);
        
        if (topics.length > 0) {
          // Seleccionar tema aleatorio
          const randomTopic = topics[Math.floor(Math.random() * topics.length)];
          console.log('Random topic selected:', randomTopic);
          setSelectedTopicId(randomTopic.id);
        }
      }
    } catch (error) {
      console.error('Error loading subjects:', error);
    }
  };

  const handleSubjectChange = async (subjectId) => {
    setSelectedSubjectId(subjectId);
    try {
      const response = await subjectsAPI.getTopics(subjectId);
      const topics = response.data;
      setAvailableTopics(topics);
      
      if (topics.length > 0) {
        // Auto-seleccionar primer tema o uno aleatorio
        const randomTopic = topics[Math.floor(Math.random() * topics.length)];
        setSelectedTopicId(randomTopic.id);
      } else {
        setSelectedTopicId(null);
      }
    } catch (error) {
      console.error('Error loading topics:', error);
    }
  };

  const handleGenerateSessionWithTopic = async (topicId, subjectId) => {
    try {
      setLoading(true);
      console.log('Generating session with topic:', topicId, 'subject:', subjectId, 'duration:', duration);
      const response = await sessionAPI.generate({
        subject_id: subjectId,
        topic_id: topicId,
        duration: duration
      });
      console.log('Session generated:', response.data);
      setSession(response.data);
      setQuizAnswers({});
      setShowResults(false);
    } catch (error) {
      console.error('Error generating session:', error);
      alert('Error al generar la sesion de estudio');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSession = async () => {
    if (!selectedSubjectId || !selectedTopicId) {
      alert('Por favor selecciona una materia y un tema');
      return;
    }
    
    try {
      setLoading(true);
      console.log('Generating session - subject:', selectedSubjectId, 'topic:', selectedTopicId, 'duration:', duration);
      const response = await sessionAPI.generate({
        subject_id: selectedSubjectId,
        topic_id: selectedTopicId,
        duration: duration
      });
      console.log('Session generated:', response.data);
      setSession(response.data);
      setQuizAnswers({});
      setShowResults(false);
    } catch (error) {
      console.error('Error generating session:', error);
      alert('Error al generar la sesion de estudio');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionIndex, answerIndex) => {
    setQuizAnswers({
      ...quizAnswers,
      [questionIndex]: answerIndex
    });
  };

  const handleSubmitQuiz = async () => {
    // Pausar timer al enviar quiz
    setTimerActive(false);
    
    let correctCount = 0;
    session.quiz.forEach((question, index) => {
      if (quizAnswers[index] === question.correct_answer) {
        correctCount++;
      }
    });

    setScore(correctCount);
    setShowResults(true);

    try {
      await sessionAPI.complete({
        topic_id: session.topic_id,
        duration: session.duration,
        score: correctCount,
        total_questions: session.quiz.length
      });
    } catch (error) {
      console.error('Error recording session:', error);
    }
  };

  const handleNewSession = () => {
    setSession(null);
    setQuizAnswers({});
    setShowResults(false);
    setScore(0);
    setTimeRemaining(0);
    setInitialTime(0);
    setTimerActive(false);
  };

  // Helper functions para el timer
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimerColor = () => {
    const percentage = (timeRemaining / initialTime) * 100;
    if (percentage > 75) return '#43a047'; // Verde
    if (percentage > 25) return '#fbbf24'; // Amarillo
    return '#dc2626'; // Rojo
  };

  const getProgressPercentage = () => {
    if (initialTime === 0) return 100;
    return (timeRemaining / initialTime) * 100;
  };

  if (!session) {
    // Si hay tema pre-seleccionado (flujo aleatorio), mostrar loading simple
    if (selectedTopic && subject) {
      return (
        <div>
          <div className="back-button">
            <button className="button button-secondary button-small" onClick={onBack}>
              Volver
            </button>
          </div>

          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <h2>Generando Sesion de Estudio</h2>
            <div style={{ 
              background: '#e3f2fd', 
              padding: '1.5rem', 
              borderRadius: '8px', 
              margin: '2rem auto',
              maxWidth: '500px',
              borderLeft: '4px solid #1e88e5'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#1e88e5' }}>{subject.name}</h3>
              <p style={{ margin: '0', fontSize: '1.1rem', color: '#555' }}>{selectedTopic.name}</p>
              <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem', color: '#777' }}>
                Duracion: {duration} minutos
              </p>
            </div>
            <div className="loading">Generando contenido personalizado...</div>
          </div>
        </div>
      );
    }

    // Si NO hay tema pre-seleccionado, mostrar selector manual
    const selectedSubject = allSubjects.find(s => s.id === selectedSubjectId);
    const selectedTopicData = availableTopics.find(t => t.id === selectedTopicId);
    
    return (
      <div>
        <div className="back-button">
          <button className="button button-secondary button-small" onClick={onBack}>
            Volver
          </button>
        </div>

        <div className="card">
          <h2>Nueva Sesion de Estudio</h2>
          <p style={{ color: '#666', marginBottom: '2rem' }}>
            Personaliza tu sesion de estudio seleccionando la materia, tema y duracion
          </p>
          
          <div className="form-group">
            <label>Materia</label>
            <select 
              value={selectedSubjectId || ''} 
              onChange={(e) => handleSubjectChange(Number(e.target.value))}
              disabled={allSubjects.length === 0}
            >
              {allSubjects.length === 0 && <option value="">No hay materias disponibles</option>}
              {allSubjects.map(subject => (
                <option key={subject.id} value={subject.id}>
                  {subject.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Tema</label>
            <select 
              value={selectedTopicId || ''} 
              onChange={(e) => setSelectedTopicId(Number(e.target.value))}
              disabled={availableTopics.length === 0}
            >
              {availableTopics.length === 0 && <option value="">No hay temas disponibles</option>}
              {availableTopics.map(topic => (
                <option key={topic.id} value={topic.id}>
                  {topic.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Duracion de la sesion</label>
            <select value={duration} onChange={(e) => setDuration(Number(e.target.value))}>
              <option value={5}>5 minutos</option>
              <option value={10}>10 minutos</option>
              <option value={15}>15 minutos</option>
            </select>
          </div>

          {selectedSubject && selectedTopicData && (
            <div style={{ 
              background: '#e3f2fd', 
              padding: '1rem', 
              borderRadius: '4px', 
              marginBottom: '1rem',
              borderLeft: '4px solid #1e88e5'
            }}>
              <strong>Sesion seleccionada:</strong>
              <p style={{ margin: '0.5rem 0 0 0', color: '#555' }}>
                {selectedSubject.name} - {selectedTopicData.name} ({duration} minutos)
              </p>
            </div>
          )}

          <button 
            className="button" 
            onClick={handleGenerateSession}
            disabled={loading || !selectedSubjectId || !selectedTopicId}
          >
            {loading ? 'Generando...' : 'Iniciar Sesion'}
          </button>
        </div>
      </div>
    );
  }

  console.log('Current session state:', session);

  return (
    <div>
      {/* Timer Bar - Solo mostrar cuando hay sesión activa y no se han mostrado resultados */}
      {session && !showResults && (
        <div className="timer-container">
          <div className="timer-bar-wrapper">
            <div 
              className="timer-bar-progress" 
              style={{ 
                width: `${getProgressPercentage()}%`,
                backgroundColor: getTimerColor(),
                transition: 'width 1s linear, background-color 0.3s ease'
              }}
            />
          </div>
          <div className="timer-display">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            <span className="timer-text" style={{ color: getTimerColor() }}>
              {formatTime(timeRemaining)} / {formatTime(initialTime)}
            </span>
            {timeRemaining <= 60 && timeRemaining > 0 && (
              <span className="timer-warning">¡Último minuto!</span>
            )}
          </div>
        </div>
      )}

      <div className="back-button">
        <button className="button button-secondary button-small" onClick={onBack}>
          Volver
        </button>
      </div>

      <div className="card">
        <h2>{session.topic_name}</h2>
        <p><strong>Duracion:</strong> {session.duration} minutos</p>
        
        <div style={{ marginTop: '1.5rem' }}>
          <h3>Objetivo de Aprendizaje</h3>
          <div style={{ background: '#e3f2fd', padding: '1rem', borderRadius: '4px', borderLeft: '4px solid #1e88e5' }}>
            {session.learning_objective ? (
              <ReactMarkdown>{session.learning_objective}</ReactMarkdown>
            ) : (
              <p style={{ color: '#999' }}>No hay objetivo de aprendizaje disponible</p>
            )}
          </div>
        </div>

        <div style={{ marginTop: '1.5rem' }}>
          <h3>Contenido</h3>
          <div className="markdown-content" style={{ lineHeight: '1.8', textAlign: 'justify' }}>
            {session.content ? (
              <ReactMarkdown>{session.content}</ReactMarkdown>
            ) : (
              <p style={{ color: '#999' }}>No hay contenido disponible</p>
            )}
          </div>
        </div>

        <div style={{ marginTop: '1.5rem' }}>
          <h3>Conceptos Clave</h3>
          <ul style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '4px' }}>
            {session.key_concepts.map((concept, index) => (
              <li key={index} style={{ marginBottom: '0.5rem' }}>
                <div className="concept-markdown">
                  <ReactMarkdown>{concept}</ReactMarkdown>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card quiz-container">
        <h3>Mini-Quiz</h3>
        <p>Responde las siguientes preguntas para evaluar tu comprension:</p>

        {session.quiz.map((question, qIndex) => (
          <div key={qIndex} className="quiz-question">
            <h4>Pregunta {qIndex + 1}</h4>
            <p>{question.question}</p>
            <ul className="quiz-options">
              {question.options.map((option, oIndex) => (
                <li
                  key={oIndex}
                  className={`quiz-option ${quizAnswers[qIndex] === oIndex ? 'selected' : ''} ${
                    showResults
                      ? oIndex === question.correct_answer
                        ? 'correct'
                        : quizAnswers[qIndex] === oIndex
                        ? 'incorrect'
                        : ''
                      : ''
                  }`}
                  onClick={() => !showResults && handleAnswerSelect(qIndex, oIndex)}
                  style={{
                    cursor: showResults ? 'default' : 'pointer',
                    background: showResults
                      ? oIndex === question.correct_answer
                        ? '#c8e6c9'
                        : quizAnswers[qIndex] === oIndex
                        ? '#ffccbc'
                        : '#f8f9fa'
                      : undefined
                  }}
                >
                  {String.fromCharCode(65 + oIndex)}) {option}
                </li>
              ))}
            </ul>
          </div>
        ))}

        {!showResults ? (
          <button
            className="button"
            onClick={handleSubmitQuiz}
            disabled={Object.keys(quizAnswers).length < session.quiz.length}
          >
            Enviar Respuestas
          </button>
        ) : (
          <div>
            <div className="alert alert-success">
              <h4>Resultado del Quiz</h4>
              <p>
                Obtuviste {score} de {session.quiz.length} respuestas correctas
                ({Math.round((score / session.quiz.length) * 100)}%)
              </p>
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button className="button" onClick={handleNewSession}>
                Nueva Sesion
              </button>
              <button className="button button-secondary" onClick={onComplete}>
                Finalizar
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default StudySession;
