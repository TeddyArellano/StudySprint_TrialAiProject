import React, { useState, useEffect } from 'react';
import { subjectsAPI } from './api/api';
import SubjectList from './components/SubjectList';
import CreateSubject from './components/CreateSubject';
import TopicManager from './components/TopicManager';
import StudySession from './components/StudySession';
import logo from './logo.png';
import './App.css';

function App() {
  const [subjects, setSubjects] = useState([]);
  const [allTopics, setAllTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [currentView, setCurrentView] = useState('home');
  const [loading, setLoading] = useState(true);
  const [durationPreference, setDurationPreference] = useState(10); // Duración preferida por defecto: 10 min
  const [isTimeDropdownOpen, setIsTimeDropdownOpen] = useState(false);

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      setLoading(true);
      const response = await subjectsAPI.getAll();
      setSubjects(response.data);
      
      // Cargar todos los temas de todas las materias
      const topicsPromises = response.data.map(subject => 
        subjectsAPI.getTopics(subject.id)
      );
      const topicsResponses = await Promise.all(topicsPromises);
      
      // Combinar todos los temas con información de la materia
      const allTopicsData = [];
      response.data.forEach((subject, index) => {
        const subjectTopics = topicsResponses[index].data.map(topic => ({
          ...topic,
          subjectName: subject.name,
          subjectId: subject.id
        }));
        allTopicsData.push(...subjectTopics);
      });
      
      setAllTopics(allTopicsData);
    } catch (error) {
      console.error('Error loading subjects:', error);
      alert('Error al cargar las materias');
    } finally {
      setLoading(false);
    }
  };

  const handleStartRandomStudy = () => {
    if (allTopics.length === 0) {
      alert('No hay temas disponibles. Por favor, crea una materia y agrega temas primero.');
      setCurrentView('subjects');
      return;
    }

    // Seleccionar tema aleatorio
    const randomIndex = Math.floor(Math.random() * allTopics.length);
    const randomTopic = allTopics[randomIndex];
    
    setSelectedTopic(randomTopic);
    setSelectedSubject({ id: randomTopic.subjectId, name: randomTopic.subjectName });
    setCurrentView('study');
  };

  const handleStartManualStudy = () => {
    if (subjects.length === 0) {
      alert('No hay materias disponibles. Por favor, crea una materia primero.');
      setCurrentView('subjects');
      return;
    }
    
    // No seleccionar nada, dejar que StudySession cargue el selector
    setSelectedTopic(null);
    setSelectedSubject(null);
    setCurrentView('study');
  };

  const handleSubjectCreated = async () => {
    await loadSubjects();
    setCurrentView('subjects');
  };

  const handleSubjectSelected = (subject) => {
    setSelectedSubject(subject);
    setCurrentView('topics');
  };

  const handleStartStudy = () => {
    setCurrentView('study');
  };

  const handleBackToHome = () => {
    setSelectedSubject(null);
    setSelectedTopic(null);
    setCurrentView('home');
  };

  const handleBackToSubjects = () => {
    setSelectedSubject(null);
    setCurrentView('subjects');
  };

  const handleSessionComplete = () => {
    setCurrentView('home');
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} alt="Study Sprint" className="header-logo" />
      </header>

      <main className="App-main">
        {loading && <div className="loading">Cargando...</div>}

        {!loading && currentView === 'home' && (
          <div className="modern-home">
            {/* Fondo decorativo superior */}
            <div className="hero-gradient"></div>
            <div className="decorative-circle circle-1"></div>
            <div className="decorative-circle circle-2"></div>

            {/* Header: Saludo y Perfil */}
            <div className="header-section">
              <div className="welcome-text">
                <p className="welcome-subtitle">Bienvenido de nuevo,</p>
                <h1 className="welcome-title">Jose</h1>
              </div>
              <div className="profile-badge">
                <div className="profile-avatar">J</div>
              </div>
            </div>

            {/* Tarjetas de Estadísticas: Racha y Duración */}
            <div className="stats-cards-container">
              {/* Tarjeta: Racha */}
              <div className="stats-card">
                <div className="stat-item">
                  <div className="stat-icon stat-icon-yellow">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M13 2L3 14h8l-1 8 10-12h-8l1-8z"/>
                    </svg>
                  </div>
                  <div className="stat-content">
                    <p className="stat-label">Racha de estudio</p>
                    <p className="stat-value">5 Días</p>
                  </div>
                </div>
              </div>

              {/* Tarjeta: Selector de Duración (Dropdown) */}
              <div className="stats-card duration-dropdown-card">
                <div className="stat-item">
                  <button 
                    onClick={() => setIsTimeDropdownOpen(!isTimeDropdownOpen)}
                    className="time-dropdown-button"
                  >
                    <div className="stat-icon stat-icon-green">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"/>
                        <polyline points="12 6 12 12 16 14"/>
                      </svg>
                    </div>
                    <div className="stat-content-dropdown">
                      <div className="stat-label-row">
                        <p className="stat-label">Tiempo</p>
                        <svg 
                          width="12" 
                          height="12" 
                          viewBox="0 0 24 24" 
                          fill="none" 
                          stroke="currentColor" 
                          strokeWidth="2"
                          className={`chevron-icon ${isTimeDropdownOpen ? 'rotate' : ''}`}
                        >
                          <polyline points="6 9 12 15 18 9"/>
                        </svg>
                      </div>
                      <p className="stat-value-large">{durationPreference} min</p>
                    </div>
                  </button>
                  
                  {/* Dropdown Menu */}
                  {isTimeDropdownOpen && (
                    <div className="time-dropdown-menu">
                      <button 
                        className={`time-dropdown-item ${durationPreference === 5 ? 'active' : ''}`}
                        onClick={() => {
                          setDurationPreference(5);
                          setIsTimeDropdownOpen(false);
                        }}
                      >
                        <span className="time-dropdown-text">5 minutos</span>
                        {durationPreference === 5 && (
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                          </svg>
                        )}
                      </button>
                      <button 
                        className={`time-dropdown-item ${durationPreference === 10 ? 'active' : ''}`}
                        onClick={() => {
                          setDurationPreference(10);
                          setIsTimeDropdownOpen(false);
                        }}
                      >
                        <span className="time-dropdown-text">10 minutos</span>
                        {durationPreference === 10 && (
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                          </svg>
                        )}
                      </button>
                      <button 
                        className={`time-dropdown-item ${durationPreference === 15 ? 'active' : ''}`}
                        onClick={() => {
                          setDurationPreference(15);
                          setIsTimeDropdownOpen(false);
                        }}
                      >
                        <span className="time-dropdown-text">15 minutos</span>
                        {durationPreference === 15 && (
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                          </svg>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Sección Principal: Acciones */}
            <div className="actions-section">
              {/* Botón Principal: Sesión Aleatoria */}
              <button 
                className="action-button action-primary"
                onClick={handleStartRandomStudy}
                disabled={allTopics.length === 0}
              >
                <div className="primary-button-glow"></div>
                <div className="primary-button-content">
                  <div className="ai-badge">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2l2.4 7.4h7.6l-6 4.6 2.3 7-6.3-4.6-6.3 4.6 2.3-7-6-4.6h7.6z"/>
                    </svg>
                    AGENTE IA
                  </div>
                  <div className="play-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                  <h2 className="primary-button-title">Sesión de Estudio Aleatoria</h2>
                  <p className="primary-button-subtitle">
                    Deja que la IA elija el mejor tema para reforzar hoy basado en tu progreso.
                  </p>
                </div>
              </button>

              {/* Botón Secundario: Seleccionar Tema */}
              <button 
                className="action-button action-secondary"
                onClick={handleStartManualStudy}
                disabled={subjects.length === 0}
              >
                <div className="secondary-button-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="7" height="7"/>
                    <rect x="14" y="3" width="7" height="7"/>
                    <rect x="14" y="14" width="7" height="7"/>
                    <rect x="3" y="14" width="7" height="7"/>
                  </svg>
                </div>
                <div className="secondary-button-text">
                  <h3 className="secondary-button-title">Seleccionar Tema</h3>
                  <p className="secondary-button-subtitle">Elige una materia específica</p>
                </div>
                <div className="secondary-button-arrow">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 18l6-6-6-6"/>
                  </svg>
                </div>
              </button>
            </div>

            {/* Información de temas disponibles */}
            {allTopics.length === 0 && (
              <p className="info-message info-warning">
                No tienes temas disponibles. Crea una materia y agrega temas primero.
              </p>
            )}
            {allTopics.length > 0 && (
              <p className="info-message info-success">
                Tienes {allTopics.length} tema{allTopics.length !== 1 ? 's' : ''} disponible{allTopics.length !== 1 ? 's' : ''} en {subjects.length} materia{subjects.length !== 1 ? 's' : ''}
              </p>
            )}

            {/* Menú Inferior: Gestión */}
            <div className="bottom-menu">
              <div className="bottom-menu-handle"></div>
              <button 
                className="manage-button"
                onClick={() => setCurrentView('subjects')}
              >
                <div className="manage-button-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 1v6m0 6v6m7.07-14.93l-4.24 4.24m-5.66 5.66l-4.24 4.24m14.93.07h-6m-6 0H1m14.93-7.07l-4.24-4.24m-5.66-5.66L1.07 1.07"/>
                  </svg>
                </div>
                <span>Gestionar Materias y Temas</span>
              </button>
            </div>
          </div>
        )}

        {!loading && currentView === 'subjects' && (
          <div className="subjects-list" style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 1rem' }}>
            <div className="back-button">
              <button className="button button-secondary button-small" onClick={handleBackToHome}>
                Volver al Inicio
              </button>
            </div>
            <SubjectList 
              subjects={subjects} 
              onSelectSubject={handleSubjectSelected}
            />
            <CreateSubject onSubjectCreated={handleSubjectCreated} />
          </div>
        )}

        {!loading && currentView === 'topics' && selectedSubject && (
          <div className="topic-manager" style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 1rem' }}>
            <TopicManager
              subject={selectedSubject}
              onBack={handleBackToSubjects}
              onStartStudy={handleStartStudy}
            />
          </div>
        )}

        {!loading && currentView === 'study' && (
          <div className="study-session">
            <StudySession
              subject={selectedSubject}
              selectedTopic={selectedTopic}
              preferredDuration={durationPreference}
              onComplete={handleSessionComplete}
              onBack={handleBackToHome}
            />
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Study Sprint - Trial Ai Project</p>
      </footer>
    </div>
  );
}

export default App;
