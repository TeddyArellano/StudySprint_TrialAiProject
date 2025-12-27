import React, { useState } from 'react';
import { subjectsAPI } from '../api/api';

function CreateSubject({ onSubjectCreated }) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name.trim()) {
      alert('El nombre es requerido');
      return;
    }

    try {
      setLoading(true);
      await subjectsAPI.create({ name, description });
      setName('');
      setDescription('');
      setShowForm(false);
      onSubjectCreated();
    } catch (error) {
      console.error('Error creating subject:', error);
      alert('Error al crear la materia');
    } finally {
      setLoading(false);
    }
  };

  if (!showForm) {
    return (
      <div className="modern-card action-card">
        <button className="modern-button modern-button-primary" onClick={() => setShowForm(true)}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14m-7-7h14"/>
          </svg>
          Nueva Materia
        </button>
      </div>
    );
  }

  return (
    <div className="modern-card form-card">
      <div className="form-header">
        <h3 className="form-title">Nueva Materia</h3>
        <p className="form-subtitle">Agrega una nueva materia a tu plan de estudios</p>
      </div>
      <form onSubmit={handleSubmit} className="modern-form">
        <div className="modern-form-group">
          <label className="modern-label">Nombre de la Materia</label>
          <input
            type="text"
            className="modern-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ej: Inteligencia Artificial"
            required
          />
        </div>
        
        <div className="modern-form-group">
          <label className="modern-label">Descripción (opcional)</label>
          <textarea
            className="modern-textarea"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Breve descripción de la materia"
            rows="3"
          />
        </div>

        <div className="form-actions">
          <button 
            type="button"
            className="modern-button modern-button-secondary"
            onClick={() => setShowForm(false)}
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            className="modern-button modern-button-primary" 
            disabled={loading}
          >
            {loading ? 'Creando...' : 'Crear Materia'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateSubject;
