## Overview

This project implements a backend system that ingests candidate data, processes it asynchronously in scheduled batches, retries failed records, and provides reporting and monitoring APIs.

The system simulates a real-world background processing pipeline where:

* Candidate data is submitted via API
* Records are validated and stored
* Processing happens in background batches (maximum 10 records per run)
* External API responses update candidate status
* Failed records are retried automatically
* Admin users can inspect batch runs
* Reports provide operational analytics

## Technology Stack

* Python
* Django
* Django REST Framework
* Celery (Job Queue)
* Redis (Message Broker)
* JWT Authentication
* PostgreSQL

## Key Features

* JWT-based authentication
* Role-based access control (ADMIN, REVIEWER)
* Candidate data validation
* Background batch processing (max 10 records per run)
* Scheduled job execution (every 2 hours)
* Manual batch trigger
* Retry mechanism for failed records
* Concurrency-safe processing
* Reporting and analytics endpoints
* Stuck candidate detection
* Health check endpoint

## Architecture Overview

Client → Django API → Database (store PENDING)
↓
Celery Beat (Scheduler)
↓
Redis Queue
↓
Celery Worker
↓
External API Call
↓
Update Candidate Status
↓
Reporting & Monitoring

### Why Asynchronous Processing?

Instead of calling the external API during the request:

* It prevents blocking user requests
* Improves performance
* Enables retry logic
* Supports batching
* Ensures better scalability

## Local Setup Instructions

### 1. Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Apply Migrations

```
python manage.py makemigrations
```

```
python manage.py migrate
```

### 4. Start Redis

```
redis-server
```

### 5. Start Django Server

```
python manage.py runserver
```

### 6. Start Celery Worker (Windows)

```
celery -A config worker --pool=solo --loglevel=info
```

Note: `--pool=solo` is required on Windows.

### 7. Start Celery Beat Scheduler

```
celery -A config beat --loglevel=info
```


### Project Structre Overview
```
project_root/
│
├── users/        → Authentication logic
├── candidates/   → Candidate data handling
├── batches/      → Background job processing & BatchRun & CandidateAttempt Models
├── reports/      → Reporting & analytics 
├── core/         → Health & shared utilities
└── config/       → Project configuration
```
## Authentication APIs – users App

Handles user authentication and token management.

Base Path: /auth/


- Seeded Admin User
```
email: admin@test.com
password: admin123
```
- Seeded Reviewer User
```
email: admin@test.com
password: admin123
```

### Login

POST
[http://127.0.0.1:8000/auth/login/](http://127.0.0.1:8000/auth/login/)

### Refresh Token

POST
[http://127.0.0.1:8000/auth/refresh/](http://127.0.0.1:8000/auth/refresh/)

### Logout

POST
[http://127.0.0.1:8000/auth/logout/](http://127.0.0.1:8000/auth/logout/)

Purpose:

* Accept and validate candidate form data
* Store candidate records
* Advanced filtering and search
* Pagination and sorting support

## Candidate APIs – candidates App
Handles candidate data ingestion and search functionality.
### Create Candidate

POST
[http://127.0.0.1:8000/candidates/](http://127.0.0.1:8000/candidates/)

Example Request:

```
{
  "name": "Alice Johnson",
  "email": "alice@gmail.com",
  "phoneNumber": "+919876543210",
  "link": "https://linkedin.com/in/alice",
  "dob": "24/03/2001"
}
```

### Search Candidates

GET
[http://127.0.0.1:8000/candidates/search/](http://127.0.0.1:8000/candidates/search/)

Example:

```
/candidates/search?q=alice&status=FAILED&page=1&pageSize=10
```

Purpose:

* Accept and validate candidate form data
* Store candidate records
* Advanced filtering and search
* Pagination and sorting support

## Batch Processing APIs – batches App
Handles background job processing and batch execution monitoring.

### List Batch Runs

GET
[http://127.0.0.1:8000/batch-runs/](http://127.0.0.1:8000/batch-runs/)

### Trigger Batch Manually (ADMIN only)

POST
[http://127.0.0.1:8000/batch-runs/trigger/](http://127.0.0.1:8000/batch-runs/trigger/)

Purpose:

* Scheduled batch execution (via Celery)
* Manual batch trigger (ADMIN only)
* Batch execution history tracking
* Operational monitoring

## Reporting & Analytics APIs – reports App
Provides system metrics and operational insights.

### Status Metrics

GET
[http://127.0.0.1:8000/reports/status-metrics/](http://127.0.0.1:8000/reports/status-metrics/)

Optional Parameters:

* groupBy=day | week
* includeDomains=true

Example:

```
/reports/status-metrics/?groupBy=day&includeDomains=true
```

### Stuck Candidates

GET
[http://127.0.0.1:8000/reports/stuck-candidates/](http://127.0.0.1:8000/reports/stuck-candidates/)

Optional Parameters:

* minAttempts
* hoursFailed
* hoursPending

Example:

```
/reports/stuck-candidates/?minAttempts=1&hoursFailed=0
```

Purpose:
* Processing statistics
* Success & failure metrics
* Retry distribution
* Grouped analytics (day/week)
* Domain-level analytics
* Detection of stuck records

## Health Endpoint
Provides basic system health check.

GET
[http://127.0.0.1:8000/health/](http://127.0.0.1:8000/health/)

Purpose:
* API availability check
* Monitoring system integration



## Batch Processing Logic

* Scheduler runs every 2 hours.
* Selects up to 10 candidates with status PENDING or FAILED.
* Locks rows to prevent duplicate processing.
* Sends batch to external API.
* Updates candidate status and attempt count.
* Saves batch execution summary.
* Failed records are retried in future batches.


## Important Notes

* Production schedule runs every 2 hours.
* For testing, schedule can be reduced to 1 minute.
* Celery and Redis are required for background processing.
* Windows requires `--pool=solo` for Celery worker.

## Conclusion

This system demonstrates:

* Asynchronous job queue implementation
* Concurrency-safe batch processing
* Retry logic
* Analytical reporting
* Clean and scalable backend design

The architecture mirrors real-world backend systems that require background processing and operational monitoring.