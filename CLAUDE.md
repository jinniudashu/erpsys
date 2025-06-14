# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Basic Development
- **Run development server**: `python manage.py runserver` (Django with SQLite)
- **Run with MCP server**: `python manage.py runserver_with_mcp` (Django + MCP server together)
- **Run tests**: `pytest` (configured with Django settings)
- **Database migrations**: `python manage.py migrate`
- **Create superuser**: `python manage.py createsuperuser`
- **Collect static files**: `python manage.py collectstatic`

### Database Operations
- **Initial setup**: `python dev_initial.py` (loads initial business models)
- **Backup data**: `python backup.py`

### Celery Task Queue
- **Start Celery worker**: `celery -A erpsys worker -l info`
- **Start Celery beat scheduler**: `celery -A erpsys beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

### Docker Deployment
- **Development**: `docker-compose up` (includes PostgreSQL, Redis, Celery)
- **Production**: Uses PostgreSQL backend with Redis for caching and message queue

## Architecture Overview

### Three-Layer Meta-Framework Design

**Design Layer (`design/` app)** - Configuration engine for business domain modeling:
- **DataItem**: Meta-models for business entities with inheritance and composition
- **Service**: Configurable business processes and workflows  
- **Resource**: Abstract resource types (Material, Equipment, Device, Capital, Knowledge)
- **Form**: Dynamic UI generation from data structure definitions

**Execution Layer (`kernel/` app)** - Process workflow engine with OS-inspired design:
- **Process Control Block (PCB)**: Business processes with states (NEW, READY, RUNNING, WAITING, SUSPENDED, TERMINATED)
- **Scheduler**: Resource-aware process allocation and constraint-based scheduling
- **Event-driven automation**: Signal-based workflow triggers and rule evaluation
- **Generic entity binding**: Flexible process-to-business-entity relationships

**Application Layer (`applications/` app)** - Domain-specific implementations from configured models.

### Key Design Patterns

**Meta-Programming Architecture**: Runtime model generation from meta-definitions enables no-code business entity creation with Chinese language support.

**Process-as-OS-Process Metaphor**: Business operations become schedulable processes with resource contention resolution using CPU scheduling algorithms.

**Event-Driven Workflow**: Signal-based automation with real-time state synchronization across components.

## Technology Stack

- **Backend**: Django 4.2.7 with Django REST Framework and JWT authentication
- **Database**: SQLite (dev) / PostgreSQL (prod) 
- **Real-time**: Django Channels with WebSocket support
- **Task Queue**: Celery with Redis broker and django-celery-beat scheduler
- **Caching**: Redis with django-redis
- **Frontend Assets**: HTMX, Vue.js, Bootstrap (served statically)
- **Internationalization**: Chinese language support with pypinyin

## Environment Configuration

Development uses SQLite and local Redis. Production uses PostgreSQL and containerized Redis.

Set `DJANGO_ENV=dev` for development mode. Environment variables are loaded from `.env` file.

MCP (Model Context Protocol) server integration is available for AI assistant interactions during development.