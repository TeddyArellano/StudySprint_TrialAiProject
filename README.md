# Study Sprint Agent - MVP

Agente inteligente de apoyo al estudio que transforma material academico en micro-sesiones estructuradas y personalizadas.

## Inicio Rapido

### Ejecutar el Sistema

**Opcion 1 - Doble click:**
- Ejecuta `start.bat` o `start.ps1`

**Opcion 2 - Manual:**

Terminal 1 (Backend):
```bash
cd backend
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

## URLs

- **Backend API**: http://localhost:8000
- **Frontend Web**: http://localhost:3000

## Estructura

```
backend/           # FastAPI + Python
├── main.py       # Servidor API
├── src/          # Logica del agente
└── data/         # Base de datos SQLite

frontend/         # React
├── src/          # Componentes
└── public/       # Archivos estaticos
```

## Caracteristicas

- Gestion de materias y temas
- Carga de PDFs como material
- Sesiones de estudio de 5, 10 o 15 min
- Quizzes interactivos
- Recomendaciones inteligentes

## Requisitos

- Python 3.8+
- Node.js 16+
- OpenAI API Key (configurada en backend/.env)

