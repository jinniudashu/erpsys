# Django ERP OS Framework

A **customizable ERP framework** with sophisticated workflow engine and meta-modeling capabilities. This project demonstrates a novel approach to enterprise resource planning by treating business operations as computational processes, enabling unprecedented levels of automation and optimization.

## Framework Architecture

### Three-Layer Meta-Framework Design

#### 1. Design Layer (`design/` app) - Meta-Modeling System
The **configuration engine** where business domains are defined without programming:

**Data Structure Designer:**
- **DataItem**: Meta-model for defining business entities and their relationships
- **DataItemConsists**: Composition relationships between data items
- **Field Type System**: Dynamic field type definitions supporting various data types
- **Business Type Inheritance**: Entity inheritance hierarchies for complex business models

**Service Architecture Designer:**
- **Service**: Configurable business processes and workflows
- **ServiceRule**: Event-driven business logic definitions
- **Event**: Trigger conditions and expressions for automation
- **Instruction**: System-level commands and operations

**Resource Planning Designer:**
- **Resource Types**: Material, Equipment, Device, Capital, Knowledge abstractions
- **Resource Requirements**: Service-to-resource mappings and dependencies
- **Capacity Planning**: Resource allocation and scheduling algorithms

**UI/Form Generator:**
- **Form**: Dynamic form definitions from data structures
- **FormFields**: Field configuration and validation rules
- **MenuItem**: Navigation structure generation

#### 2. Execution Layer (`kernel/` app) - Workflow Engine
The **runtime engine** that executes designed business processes:

**Process Management Core:**
- **Process Control Block (PCB)**: Unique process identifier and state management
- **Process States**: NEW, READY, RUNNING, WAITING, SUSPENDED, TERMINATED
- **Process Hierarchy**: Parent-child and sequential process relationships
- **Entity Binding**: Generic foreign key binding to business entities
- **Operator Assignment**: Resource allocation and task assignment

**Scheduler Engine:**
- **Event-Driven Execution**: Signal-based process triggering and automation
- **Resource Allocation**: Multi-constraint scheduling algorithm
- **State Management**: Complete process lifecycle management
- **Context Switching**: Operator task switching capabilities

**Business Rules Engine:**
- **Rule Evaluator**: Dynamic expression evaluation for business logic
- **Event Processing**: Automated workflow triggers and responses
- **Instruction Execution**: System command processing and execution

#### 3. Application Layer (`applications/` app) - Domain Implementation
Where the **configured business domain models** are instantiated and deployed.

## Framework Capabilities

### Core Strengths

**True Meta-Programming Architecture**
- Runtime model generation from meta-definitions
- No-code business entity creation
- Inheritance and composition support
- Dynamic class generation with Chinese language support

**Sophisticated Process Management**
- OS-Inspired Design: Real Process Control Block implementation for business processes
- Multi-State Workflow: Complete process lifecycle management
- Resource-Aware Scheduling: Constraint-based process allocation
- Hierarchical Processes: Parent-child and sequential process chains

**Event-Driven Architecture**
- Signal-based workflow automation
- Real-time process state synchronization
- Decoupled component communication
- Automatic task list updates and scheduling

**Generic Resource Management**
- Unified resource abstraction across all resource types
- Capacity planning and allocation algorithms
- Resource requirement specifications per service
- Multi-dimensional resource constraints

## Technical Innovation

**Business Process as OS Process Metaphor**
- Each business operation becomes a schedulable process
- Resource contention resolution using CPU scheduling algorithms
- Context switching between different business activities
- Priority-based process execution

**Meta-Model Driven Development**
- Business analysts can define entities without programming
- Form generation from data structure definitions
- API mapping and integration capabilities
- Dynamic relationship management

**Multi-Tenant Service Framework**
- Generic service definitions reusable across domains
- Rule-based business logic configuration
- Pluggable instruction sets
- Domain-specific customization without code changes

## Technology Stack

- **Backend**: Django 4.2.7 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Caching & Message Queue**: Redis
- **Task Queue**: Celery with beat scheduler
- **Real-time**: Django Channels with WebSocket support
- **Internationalization**: Native Chinese language support with pypinyin

## Demo Implementation: Aesthetic Medical Practice

The framework includes a complete demonstration implementation for aesthetic medicine clinics, showcasing:

- **Patient Management**: Complete demographic and medical history tracking
- **Treatment Operations**: Support for various cosmetic procedures (Botox, laser, etc.)
- **Appointment Scheduling**: Advanced booking system with resource allocation
- **Financial Management**: Billing, prepaid accounts, and consumption tracking
- **Inventory Control**: Medical supplies with expiration date management
- **Follow-up Care**: Automated patient care and reminder systems

## Strategic Value

This framework represents a **meta-ERP platform** capable of generating domain-specific ERP solutions across industries. Key advantages:

**Rapid Deployment**: Configure new business domains without traditional development cycles
**Process Optimization**: Sophisticated workflow optimization using computational process management
**Vertical Market Solutions**: Easily adapt to different industries (healthcare, retail, manufacturing, hospitality)
**Scalable Architecture**: Support for multi-location and multi-tenant deployments
**No-Code Configuration**: Business users can modify workflows and entities without programming

## Installation and Setup

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure database**: Update settings for your environment
4. **Run migrations**: `python manage.py migrate`
5. **Create superuser**: `python manage.py createsuperuser`
6. **Start development server**: `python manage.py runserver`

For production deployment, use the included Docker configuration and PostgreSQL setup.

## Framework Evaluation

**Innovation Level**: Genuinely novel approach to ERP framework design
**Technical Architecture**: Well-structured meta-programming foundation
**Reusability**: Highly configurable across diverse business domains
**Commercial Viability**: Strong potential for vertical market ERP solutions

The process-centric design enables sophisticated workflow optimization that traditional ERP systems struggle with, making this framework particularly valuable for service-oriented businesses requiring complex resource allocation and process management.
