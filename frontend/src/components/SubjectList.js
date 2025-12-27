import React from 'react';

function SubjectList({ subjects, onSelectSubject }) {
  if (subjects.length === 0) {
    return (
      <div className="modern-card empty-state">
        <div className="empty-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
        </div>
        <h3>No hay materias registradas</h3>
        <p>Crea tu primera materia para comenzar a estudiar</p>
      </div>
    );
  }

  return (
    <div className="modern-content">
      <div className="section-header">
        <h2 className="section-title">Mis Materias</h2>
        <p className="section-subtitle">Selecciona una materia para ver sus temas</p>
      </div>
      <div className="subjects-grid">
        {subjects.map((subject, index) => (
          <div
            key={subject.id}
            className={`subject-modern-card color-${(index % 4) + 1}`}
            onClick={() => onSelectSubject(subject)}
          >
            <div className="subject-card-header">
              <div className="subject-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <div className="subject-arrow">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 18l6-6-6-6"/>
                </svg>
              </div>
            </div>
            <h3 className="subject-card-title">{subject.name}</h3>
            {subject.description && (
              <p className="subject-card-description">{subject.description}</p>
            )}
            <div className="subject-card-footer">
              <span className="subject-date">
                {new Date(subject.created_at).toLocaleDateString('es-ES', { 
                  day: 'numeric', 
                  month: 'short', 
                  year: 'numeric' 
                })}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SubjectList;
