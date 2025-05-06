# Merchant Lead Form Application

This application implements a 3-step merchant application form with session persistence and data enrichment capabilities. It fulfills the requirements specified in the Cardiff Lead-to-Funding take-home assignment.

## Features

- **Multi-step Form**: A 3-step form collecting merchant information:
- **Session Persistence**: Form progress is saved automatically, allowing users to leave and return without losing data
  - Sessions persist across browser tabs
  - Sessions have a 24-hour expiration

- **Business Data Enrichment**: When Business Name and Zip Code are entered, data is enriched with simulated business verification data
  - Displays verification status, business start date, and status inline
  - Enhances the form with additional business context

- **Form Submission**: Complete data is submitted to a backend API and stored in a PostgreSQL database

## Tech Stack

### Backend
- **FastAPI**: Python-based REST API framework
- **PostgreSQL**: Database for lead storage
- **Redis**: Session management and form state persistence
- **Alembic**: Database migration tool
- **SQLAlchemy**: ORM for database interactions

### Frontend
- **React**: Frontend library with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API requests

### Infrastructure
- **Docker & Docker Compose**: Containerization and service orchestration

## Project Structure Overview

The project follows a clean architecture pattern with clear separation of concerns:

```
├── backend/                 # Backend API services
│   ├── alembic/             # Database migrations
│   ├── app/                 # Application code
│   │   ├── api/             # API routes and endpoints
│   │   ├── core/            # Core configuration and utilities
│   │   ├── db/              # Database models and repositories
│   │   ├── models/          # Domain models and schemas
│   │   ├── services/        # Business logic services
├── frontend/                # React frontend application
│   ├── public/              # Static assets
│   ├── src/                 # Source code
│   │   ├── api/             # API client functions
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── types/           # TypeScript type definitions
```

## Session Management

You're absolutely right, thank you for the correction. To be more precise:

The session management in this application uses a dual-storage approach:

1. **Client-side**: The session ID is stored in the browser's localStorage, allowing users to return to the application in the same browser and continue their form progress

2. **Server-side**: The actual session data (form contents, completion status, enrichment data) is stored in Redis with a 24-hour expiration

This approach provides several benefits:
- Users can close their browser and return later to continue
- Session data remains secure on the server
- Redis handles automatic expiration after 24 hours
- Multiple browser tabs can access the same session

This is clearly visible in the implementation where the frontend stores and retrieves the session ID from localStorage, while the backend manages the session data in Redis through the SessionService.
- **Scalability**: Redis provides high throughput and low latency access to session data
- **Persistence**: Sessions survive server restarts and can be shared across multiple instances
- **TTL Support**: Built-in time-to-live functionality for automatic session expiration
- **Cross-instance Access**: In a multi-server environment, all servers can access the same session data

The frontend maintains session correlation using localStorage, which persists the session ID across page refreshes and tabs. When a user returns to the application, it attempts to retrieve the existing session before creating a new one.

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Node.js and npm (for local development)
- Python 3.13+ (for local development)

### Running with Docker Compose

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd merchant-lead-form
   ```

2. Start the application stack:
   ```bash
   docker-compose up -d
   ```

3. Access the application at http://localhost:3000

### Local Development Setup

#### Backend

1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (create a .env file):
   ```
   DATABASE_URL=postgresql://postgres:password@localhost:5432/merchant_leads
   REDIS_URL=redis://localhost:6379/0
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set environment variables (create a .env file):
   ```
   VITE_API_URL=http://localhost:8000
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Access the application at http://localhost:3000

## API Documentation

### Session Endpoints

- `POST /sessions`: Create a new session
- `GET /sessions/{session_id}`: Retrieve session data
- `PUT /sessions/{session_id}`: Update session data
- `DELETE /sessions/{session_id}`: Delete a session

### Enrichment Endpoints

- `POST /enrichment`: Enrich business data with TIB verification

### Lead Endpoints

- `POST /leads`: Create a new lead directly
- `POST /leads/submit/{session_id}`: Submit a lead from session data

## Design Decisions and Scalability

### Backend Scalability

1. **Stateless API Design**: The backend follows a stateless API design, allowing horizontal scaling of API servers.

2. **Distributed Session Management**: Redis serves as a centralized session store, enabling multiple backend instances to share session data.

3. **Database Architecture**: The database schema is designed with appropriate indexes for efficient queries and includes constraints to maintain data integrity.

4. **Error Handling**: Comprehensive error handling with custom exceptions provides consistent error responses.

5. **Logging**: Structured logging with correlation IDs helps with debugging and monitoring.

### Frontend Considerations

1. **Session Recovery**: The frontend automatically attempts to recover existing sessions before creating new ones.

2. **Form Validation**: Client-side validation provides immediate feedback to users.

3. **Progressive Enhancement**: The enrichment feature enhances the form experience but doesn't block submission if unavailable.

## Deployment Considerations

For production deployment, consider:

1. **SSL/TLS**: Configure HTTPS for all traffic
2. **Rate Limiting**: Implement API rate limiting to prevent abuse
3. **Monitoring**: Add health checks and monitoring
4. **Backups**: Configure regular database backups
5. **CI/CD**: Implement continuous integration and deployment pipelines

## Future Improvements

1. **User Authentication**: Add user authentication for secure access
2. **Enhanced Validation**: Additional validation rules and business logic
3. **Analytics**: Integrate form analytics to track completion rates
4. **Multiple Enrichment Sources**: Connect to additional data sources
5. **Advanced Form Features**: Save and resume, PDF generation, etc.