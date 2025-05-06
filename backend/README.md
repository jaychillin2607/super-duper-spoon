# Merchant Lead-to-Funding Application

This project implements a multi-step merchant application form with session persistence and external API enrichment as described in the assessment requirements.

## Features

- 3-step merchant application form with session persistence
- Redis-based session management that persists across tabs and browsers
- Business verification API simulation with artificial latency and occasional failures
- Clean API design with FastAPI and SQLAlchemy
- Complete Docker setup for local development and deployment

<!-- ## System Architecture

![Architecture Diagram](architecture_diagram.png) -->

### Key Components

- **FastAPI Backend**: Handles API requests, form validation, and business logic
- **Redis**: Manages session state with TTL-based expiration (24 hours)
- **PostgreSQL**: Stores submitted lead data
- **TIB API (Simulated)**: Business verification API that enriches form data

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- PostgreSQL (for local development without Docker)
- Redis (for local development without Docker)

### Running with Docker

1. Clone the repository
2. Navigate to the project root
3. Start the services:

```bash
cd docker
docker-compose up -d
```

The API will be available at http://localhost:8000

### Local Development Setup

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the development requirements:

```bash
pip install -r requirements/dev.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env file with your configuration
```

4. Run the application:

```bash
uvicorn app.main:app --reload
```

## API Documentation

After starting the application, visit http://localhost:8000/docs for the Swagger UI API documentation.

### Key Endpoints

- **POST /sessions**: Create a new session
- **GET /sessions/{session_id}**: Get session data
- **PUT /sessions/{session_id}**: Update session data
- **POST /enrichment**: Enrich business data
- **POST /leads**: Submit lead directly
- **POST /leads/submit/{session_id}**: Submit lead from session

## Development Notes

### Session Management

This implementation uses Redis for session management due to:

1. **Performance**: Redis offers sub-millisecond response times
2. **Persistence**: Can be configured for persistence while maintaining speed
3. **TTL Support**: Built-in time-to-live functionality for automatic session expiration
4. **Scalability**: Easy to scale horizontally in production environments

An alternative would be to use localStorage on the frontend, but this approach was not chosen because:
- It would not persist across different browsers
- It depends on frontend implementation details
- It requires more security considerations to prevent tampering

### API Integration

The enrichment API is simulated with realistic characteristics:
- Random latency (0.5-2s)
- Occasional failures (10% chance)
- Realistic dummy data generation

In a production environment, this would be replaced with an actual API client.

### Scaling Considerations

For higher scale deployments:

1. **Redis Scaling**:
   - Implement Redis Sentinel for high availability
   - Consider Redis Cluster for larger datasets

2. **Database Scaling**:
   - Add read replicas for PostgreSQL
   - Implement connection pooling
   - Consider sharding for very large datasets

3. **Application Scaling**:
   - Deploy multiple API instances behind a load balancer
   - Implement API gateway for request routing and rate limiting

## Testing

Run the test suite with:

```bash
pytest
```

For coverage reports:

```bash
pytest --cov=app
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.