# FinFlow

A modern, AI-powered accounting application built with Django, HTMX, and CrewAI for automated financial management and analysis.

## Features
- Double-entry bookkeeping system
- AI-powered ledger reconciliation and financial forecasting
- Dynamic UI updates with HTMX
- Background task processing with Celery
- Comprehensive testing suite

## Tech Stack
- **Backend**: Django 5.x (Python 3.11+)
- **Frontend**: HTMX 2.x, Bootstrap 5.x
- **AI Automation**: CrewAI
- **Database**: PostgreSQL (SQLite for development)
- **Task Queue**: Celery with Redis

## Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis

## Project Structure
```
accounting_app/
├── accounting/               # Core accounting logic
├── crewai_tasks/            # AI task definitions
├── config/                  # Project settings
├── requirements.txt         # Dependencies
├── manage.py               
└── README.md               
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.