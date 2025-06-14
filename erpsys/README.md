# ERP System Core Configuration

The **erpsys/** directory contains the core Django project configuration that orchestrates the three-layer meta-framework architecture. This directory serves as the central coordination point for the entire ERP system.

## Purpose

This core configuration module:
- **Integrates all framework layers** - Design, Kernel, and Application layers
- **Configures Django settings** for development and production environments
- **Manages real-time communication** through Django Channels and WebSockets
- **Coordinates async task processing** via Celery integration
- **Provides centralized routing** for all framework components

## Key Files

### settings.py - Environment Configuration

**Multi-Environment Support**:
- **Development**: SQLite database with local Redis
- **Production**: PostgreSQL with containerized Redis
- **Environment Variables**: Flexible configuration via django-environ

**Technology Stack Integration**:
- **Django Channels** - WebSocket support for real-time updates
- **Celery Configuration** - Async task processing with Redis broker
- **CORS Settings** - Frontend integration with Vue.js/HTMX
- **JWT Authentication** - Token-based API security
- **Static Files** - WhiteNoise for production static file serving

**Chinese Language Support**:
- **Locale**: zh-hans (Simplified Chinese)
- **Timezone**: Asia/Shanghai
- **Character Encoding**: Full Unicode support for Chinese text

### urls.py - Routing Configuration

**Application Integration**:
- **Custom Admin Site** - `applications_site` for business domain management
- **Standard Admin** - Django admin for system administration
- **Modular Routing** - Clean separation of application concerns

**Customer Site Mapping**:
- Dynamic URL prefix based on `CUSTOMER_SITE_NAME` setting
- Enables multi-tenant deployment with different URL namespaces

### asgi.py - Real-time Communication

**Protocol Routing**:
- **HTTP Protocol** - Standard Django ASGI application
- **WebSocket Protocol** - Real-time updates via Django Channels
- **Authentication Middleware** - Secure WebSocket connections

**Real-time Features**:
- **Process State Updates** - Live process status changes
- **Resource Availability** - Real-time resource status updates
- **Operator Notifications** - Instant task assignments and updates

### celery.py - Async Task Configuration

**Task Processing**:
- **Background Jobs** - Long-running business process execution
- **Scheduled Tasks** - Automated workflow triggers and maintenance
- **Resource Management** - Async resource allocation and cleanup

**Integration with Framework**:
- **Process Execution** - Async execution of business processes
- **Event Processing** - Background event evaluation and triggers
- **System Maintenance** - Automated cleanup and optimization tasks

### wsgi.py - Production Deployment

**WSGI Application**:
- Standard Django WSGI configuration for production deployment
- Compatible with Gunicorn and other WSGI servers
- Production-ready application serving

## Framework Integration

### Layer Coordination

**Design Layer Integration**:
- **Service Configuration** - Routes to design layer for service definitions
- **Meta-Model Access** - DataItem and Form configuration management
- **API Generation** - Dynamic API creation from design specifications

**Kernel Layer Integration**:
- **Process Management** - Real-time process state synchronization
- **Resource Scheduling** - Coordination of resource allocation
- **Event Processing** - Real-time event triggers and automation

**Application Layer Integration**:
- **Domain Models** - Access to generated business entity models
- **Custom Admin** - Business-specific administration interfaces
- **API Endpoints** - RESTful access to business data

### Multi-Tenant Architecture

**Customer Site Configuration**:
- **Dynamic Routing** - Customer-specific URL namespaces
- **Environment Configuration** - Per-customer settings and branding
- **Data Isolation** - Secure multi-tenant data separation

### Real-time Capabilities

**WebSocket Integration**:
- **Process Updates** - Live workflow status changes
- **Operator Dashboards** - Real-time task lists and notifications
- **Resource Monitoring** - Live resource availability and utilization

**Async Processing**:
- **Background Workflows** - Long-running business processes
- **Scheduled Automation** - Timer-based process triggers
- **Resource Optimization** - Background resource management

## Development vs Production

### Development Configuration
```python
if DJANGO_ENV == 'dev':
    DEBUG = True
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
    REDIS_HOST = 'localhost:6379'
```

### Production Configuration
```python
else:
    DEBUG = False
    DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql'}}
    REDIS_HOST = 'redis:6379'  # Docker container
```

## Security Features

**Authentication & Authorization**:
- **JWT Tokens** - Secure API access with configurable expiration
- **CORS Configuration** - Controlled frontend access
- **CSRF Protection** - Standard Django CSRF security

**Environment Security**:
- **Secret Management** - Environment-based secret configuration
- **Database Security** - Parameterized database connections
- **API Security** - Token-based authentication for all API endpoints

## Deployment Architecture

**Docker Support**:
- **Multi-service Configuration** - Django, PostgreSQL, Redis, Celery
- **Environment Isolation** - Container-based deployment
- **Scalability** - Horizontal scaling support through load balancing

**Production Readiness**:
- **Static File Serving** - WhiteNoise for efficient static file delivery
- **Database Optimization** - PostgreSQL with connection pooling
- **Caching Strategy** - Redis for session and application caching

## Monitoring and Logging

**Application Logging**:
- **Structured Logging** - JSON-formatted logs for analysis
- **File and Console** - Dual output for development and production
- **Error Tracking** - Comprehensive error logging and reporting

**Performance Monitoring**:
- **Database Query Optimization** - Django query analysis
- **Cache Hit Rates** - Redis performance monitoring
- **Process Performance** - Workflow execution timing

The erpsys configuration represents the orchestration layer that enables the sophisticated three-layer meta-framework to function as a cohesive, scalable enterprise system.