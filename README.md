# SkillRoute

SkillRoute is an intelligent, personalized learning platform that dynamically maps out optimal educational journeys based on a user's skills, budget, and learning preferences. 

The platform acts as a GPS for education, moving away from static lists of courses and instead providing a highly interactive, node-based Directed Acyclic Graph (DAG) that visualizes prerequisites, core concepts, and recommended resources to reach a specific career destination.

## System Architecture

The application is built on a modern decoupled architecture:

### Frontend (Client)
- **Framework:** React + TypeScript (Vite)
- **State Management:** React Context API (`ChatContext`)
- **Styling:** Tailwind CSS (Premium light theme, custom components)
- **Core Visualization:** React Flow (`@xyflow/react`) for rendering the interactive DAG Learning Map
- **Icons:** Lucide React

### Backend (Server)
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM & Migrations:** SQLAlchemy and Alembic
- **Concurrency:** Async/Await handling via `aiohttp` for robust data pipelines

### Ingestion Pipeline
A production-grade, highly scalable asynchronous data pipeline designed to ingest and normalize external course datasets (like Coursera or Udemy):
- **Idempotency:** Safely re-runs datasets without creating duplicates, only applying genuine changes.
- **Concurrent Validation:** Automatically pings URLs during ingestion to detect dead links (404s) without hammering external servers.
- **Skill Mapping:** Translates arbitrary provider tags into SkillRoute's controlled vocabulary.

## Core Features

- **AI Chat Profiler:** An intelligent onboarding flow where users discuss their goals with an AI coach. The system extracts their intent, performs a gap analysis, and sequences a DAG learning route.
- **Interactive Learning Map:** A dynamic, 3-column dashboard where users can explore their custom roadmap. Users can zoom, pan, and click on nodes to reveal deep resource details.
- **Dynamic Node States:** Visual indicators for progress including "Completed", "In Progress", "Locked", and "Destination Target".
- **Real-time AI Overlay:** A floating chatbot widget that persists state across the application, allowing users to tweak their map on the fly.
- **Robust Resource Catalogue:** A verified, deduplicated backend database containing normalized cost, difficulty, and URL metadata.

## Local Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL

### 1. Database Setup
1. Ensure PostgreSQL is running locally.
2. Create a database named `aln_db` (or update the connection string in `backend/database.py`).

### 2. Backend Setup
Navigate to the backend directory and set up the Python environment:
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn main:app --reload
```
The backend API will be available at `http://localhost:8000`.

### 3. Frontend Setup
Open a new terminal, navigate to the frontend directory, and start the development server:
```bash
cd frontend
npm install
npm run dev
```
The application UI will be available at `http://localhost:5173`.

### 4. Running the Ingestion Pipeline (Optional)
To seed the database with external course data:
```bash
cd backend
# Make sure your venv is activated
python scripts/import_resources.py --source coursera --file data/raw/coursera.csv
```
Use the `--dry-run` flag to validate a dataset without mutating the database.
