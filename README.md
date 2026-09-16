# Entrepreneur Scheme Copilot

A comprehensive platform designed to match Indian entrepreneurs and MSMEs with the most relevant government schemes (loans, subsidies, training) using a rule-based matching engine and AI-driven analysis.

## Features
- **User Profiles**: Detailed capture of demographic and business characteristics.
- **Matching Engine**: Deterministic matching based on hard eligibility rules.
- **AI Analysis**: Contextual explanations for why a scheme fits using Gemini API.
- **Admin Dashboard**: Full CRUD interface for scheme management and verification.
- **Source Transparency**: Direct links to official sources and verification timestamps.

## Local Setup

### Backend
\\\ash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
\\\

### Frontend
Simply serve the rontend folder using any static web server, or open index.html via the backend static mount at http://127.0.0.1:8000/.

## Production Deployment

### Environment Variables
Create a .env file in the ackend directory based on .env.example.

### Docker
\\\ash
cd backend
docker build -t scheme-copilot-backend .
docker run -p 8000:8000 --env-file .env scheme-copilot-backend
\\\

### Platform as a Service (e.g., Render, Railway, Heroku)
1. Connect your repository.
2. Set the build command: pip install -r backend/requirements.txt
3. Set the start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT (or use the provided Procfile).
4. Set environment variables, specifically DATABASE_URL (PostgreSQL format: postgresql://...) and ENVIRONMENT=production.

## Database (PostgreSQL)
The application dynamically switches to PostgreSQL if DATABASE_URL starts with postgresql://. Ensure your database is initialized before starting the application.
