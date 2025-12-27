import React, { useState, useEffect } from 'react';
import { subjectsAPI, historyAPI } from '../api/api';

function TopicManager({ subject, onBack, onStartStudy }) {
  const [topics, setTopics] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [showAddTopic, setShowAddTopic] = useState(false);
  const [topicName, setTopicName] = useState('');
  const [topicDescription, setTopicDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadingTopic, setUploadingTopic] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTopics();
    loadRecommendations();
  }, [subject.id]);

  const loadTopics = async () => {
    try {
      const response = await subjectsAPI.getTopics(subject.id);
      setTopics(response.data);
    } catch (error) {
      console.error('Error loading topics:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const response = await historyAPI.getRecommendations(subject.id);
      setRecommendations(response.data.recommendations || []);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    }
  };

  const handleAddTopic = async (e) => {
    e.preventDefault();
    
    if (!topicName.trim()) {
      alert('El nombre del tema es requerido');
      return;
    }

    try {
      await subjectsAPI.createTopic(subject.id, { 
        name: topicName, 
        description: topicDescription 
      });
      setTopicName('');
      setTopicDescription('');
      setShowAddTopic(false);
      loadTopics();
      loadRecommendations();
    } catch (error) {
      console.error('Error creating topic:', error);
      alert('Error al crear el tema');
    }
  };

  const handleFileSelect = (topicId, file) => {
    setUploadingTopic(topicId);
    setSelectedFile(file);
  };

  const handleUpload = async (topicId) => {
    if (!selectedFile) return;

    try {
      await subjectsAPI.uploadMaterial(subject.id, topicId, selectedFile);
      alert('Material cargado exitosamente');
      setSelectedFile(null);
      setUploadingTopic(null);
      loadTopics();
    } catch (error) {
      console.error('Error uploading material:', error);
      alert('Error al cargar el material');
    }
  };

  return (
    <div className="modern-content">
      <div className="back-button">
        <button className="modern-button modern-button-secondary" onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5m0 0l7 7m-7-7l7-7"/>
          </svg>
          Volver a Materias
        </button>
      </div>

      <div className="modern-card subject-header-card">
        <div className="subject-header-content">
          <div className="subject-header-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
          </div>
          <div>
            <h2 className="subject-header-title">{subject.name}</h2>
            {subject.description && <p className="subject-header-description">{subject.description}</p>}
          </div>
        </div>
      </div>

      {recommendations.length > 0 && (
        <div className="modern-card recommendations-card">
          <div className="card-header-with-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            <h3>Recomendaciones de Estudio</h3>
          </div>
          <p className="recommendations-subtitle">Temas sugeridos basados en tu historial</p>
          <div className="recommendations-list">
            {recommendations.map((rec) => (
              <div key={rec.topic_id} className="recommendation-item">
                <div className="recommendation-icon">✓</div>
                <div className="recommendation-content">
                  <strong>{rec.topic_name}</strong>
                  <p>{rec.reason}</p>
                  {rec.average_performance !== null && (
                    <span className="recommendation-badge">
                      Desempeño: {rec.average_performance}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="modern-card">
        <div className="card-header-actions">
          <div>
            <h3 className="card-title">Temas</h3>
            <p className="card-subtitle">Gestiona los temas de esta materia</p>
          </div>
          <button 
            className={`modern-button ${showAddTopic ? 'modern-button-secondary' : 'modern-button-primary'}`}
            onClick={() => setShowAddTopic(!showAddTopic)}
          >
            {showAddTopic ? (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
                Cancelar
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 5v14m-7-7h14"/>
                </svg>
                Nuevo Tema
              </>
            )}
          </button>
        </div>

        {showAddTopic && (
          <form onSubmit={handleAddTopic} className="modern-form add-topic-form">
            <div className="modern-form-group">
              <label className="modern-label">Nombre del Tema</label>
              <input
                type="text"
                className="modern-input"
                value={topicName}
                onChange={(e) => setTopicName(e.target.value)}
                placeholder="Ej: Algoritmos de Búsqueda"
                required
              />
            </div>
            <div className="modern-form-group">
              <label className="modern-label">Descripción (opcional)</label>
              <textarea
                className="modern-textarea"
                value={topicDescription}
                onChange={(e) => setTopicDescription(e.target.value)}
                placeholder="Breve descripción del tema"
                rows="3"
              />
            </div>
            <button type="submit" className="modern-button modern-button-primary">
              Agregar Tema
            </button>
          </form>
        )}

        {loading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Cargando temas...</p>
          </div>
        )}

        {!loading && topics.length === 0 && !showAddTopic && (
          <div className="empty-state-inline">
            <p>No hay temas registrados. Agrega tu primer tema para comenzar.</p>
          </div>
        )}

        {!loading && topics.length > 0 && (
          <div className="topics-list">
            {topics.map((topic, index) => (
              <div key={topic.id} className={`topic-modern-item color-${(index % 4) + 1}`}>
                <div className="topic-item-header">
                  <div className="topic-number">{index + 1}</div>
                  <div className="topic-info">
                    <h4 className="topic-title">{topic.name}</h4>
                    {topic.description && <p className="topic-description">{topic.description}</p>}
                    {topic.has_content && (
                      <span className="topic-badge">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                        </svg>
                        Material cargado
                      </span>
                    )}
                  </div>
                </div>
                <div className="topic-actions">
                  {uploadingTopic === topic.id ? (
                    <div className="upload-section">
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={(e) => setSelectedFile(e.target.files[0])}
                        className="file-input"
                      />
                      <div className="upload-buttons">
                        <button
                          className="modern-button modern-button-primary modern-button-small"
                          onClick={() => handleUpload(topic.id)}
                          disabled={!selectedFile}
                        >
                          Subir
                        </button>
                        <button
                          className="modern-button modern-button-secondary modern-button-small"
                          onClick={() => {
                            setUploadingTopic(null);
                            setSelectedFile(null);
                          }}
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      className="modern-button modern-button-secondary modern-button-small"
                      onClick={() => setUploadingTopic(topic.id)}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4m14-7l-5-5-5 5m5-5v12"/>
                      </svg>
                      Cargar PDF
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {topics.length > 0 && (
        <div className="modern-card action-card-full">
          <button className="modern-button modern-button-primary modern-button-large" onClick={onStartStudy}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
            Iniciar Sesión de Estudio
          </button>
        </div>
      )}
    </div>
  );
}

export default TopicManager;
