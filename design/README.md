# Design Layer - Meta-Modeling System

The **Design Layer** is the configuration engine where business domains are defined without programming. This layer provides the meta-modeling infrastructure that enables no-code business entity creation and complex workflow design.

## Core Purpose

The Design Layer serves as the blueprint definition system that:
- Defines business entities through meta-models without coding
- Configures service processes and workflows declaratively
- Manages resource types and requirements
- Generates forms and UI dynamically from data structures
- Enables runtime model generation with inheritance and composition

## Key Components

### Data Structure Designer

**DataItem** - The core meta-model for defining business entities:
- **Field Type System**: Supports Django field types (CharField, IntegerField, etc.)
- **Business Type Inheritance**: Entity inheritance hierarchies through `business_type`
- **Composition Relationships**: Complex structures via `DataItemConsists`
- **Implementation Types**: Field, Model, Log, Dict for different entity roles
- **Computed Logic**: Dynamic field calculations and business rules

**DataItemConsists** - Composition relationships between data items:
- **Order Management**: Sequencing of composed elements
- **API Mapping**: Integration with external systems
- **Default Values**: Pre-configured field defaults

### Service Architecture Designer

**Service** - Configurable business processes and workflows:
- **Generic Content Types**: Services can operate on any entity type
- **Service Composition**: Complex workflows through ServiceConsists
- **Resource Requirements**: Multi-dimensional resource allocation
- **Form Integration**: Dynamic UI generation from service definitions
- **API Integration**: External system connectivity

**ServiceRule** - Event-driven business logic definitions:
- **Event Triggers**: Automated workflow activation
- **System Instructions**: Orchestrated system operations  
- **Entity Binding**: Generic relationships to any business object
- **Parameter Passing**: Configurable rule parameters

**Event** - Trigger conditions and automation expressions:
- **Expression Evaluation**: Dynamic condition checking
- **Timer Events**: Scheduled automation triggers
- **Parameter Configuration**: Event-specific data passing

### Resource Planning Designer

**Resource Types** - Abstract resource definitions:
- **Material** - Physical supplies and inventory
- **Equipment** - Shared medical equipment
- **Device** - Tools and instruments
- **Capital** - Financial resource abstractions
- **Knowledge** - Information and expertise

**Resource Requirements** - Service-to-resource mappings:
- **Quantity Specifications**: Required resource amounts
- **Multi-Resource Services**: Complex resource dependencies
- **Capacity Planning**: Resource allocation algorithms

### Human Resources

**Operator** - Personnel and role definitions:
- **Role-Based Access**: Service permissions through roles
- **Context Management**: Operator-specific data and state
- **Organization Structure**: Hierarchical personnel management

**Role** - Permission and service groupings:
- **Service Authorization**: Controlled access to business processes
- **Multi-Role Support**: Flexible permission combinations

### UI/Form Generator

**Form** - Dynamic form definitions from data structures:
- **Field Expansion**: Automatic form generation from DataItems
- **Choice Types**: Various input control types
- **Aggregate Fields**: Complex data presentation
- **Visibility Control**: Conditional field display

**MenuItem** - Navigation structure generation:
- **Hierarchical Menus**: Tree-structured navigation
- **Form Integration**: Direct links to generated forms
- **Icon Support**: Visual menu enhancement

### External Integration

**Api** - External system integration definitions:
- **RESTful Support**: Multiple HTTP methods
- **Field Mapping**: Data transformation between systems
- **Documentation**: API specification management

**Project** - Domain deployment configurations:
- **Source Code Management**: Generated code tracking
- **Domain Specification**: Business area definitions

## Meta-Programming Architecture

### Runtime Model Generation
The design layer enables true meta-programming:
1. **DataItem definitions** specify entity structure
2. **Dynamic class generation** creates Django models at runtime
3. **Chinese language support** with automatic pinyin conversion
4. **Inheritance and composition** support complex business relationships

### No-Code Configuration
Business analysts can:
- Define entities without programming knowledge
- Configure workflows through visual tools
- Manage resource requirements declaratively
- Generate forms automatically from data definitions

### Schema Evolution
The system supports:
- **Dynamic field addition** without migrations
- **Business logic modification** through configuration
- **Workflow adaptation** without code changes
- **Multi-tenant customization** per domain

## Integration with Other Layers

### Kernel Layer Integration
- **Process binding** connects entities to workflow engine
- **Service execution** triggers from design definitions
- **Resource allocation** based on design specifications
- **Event processing** drives automated workflows

### Application Layer Generation
- **Model instantiation** from DataItem definitions
- **Business logic inheritance** from design patterns
- **Process integration** through kernel connections
- **API generation** for frontend consumption

## File Structure

- `models.py` - Core meta-model definitions
- `types.py` - Type definitions and choices
- `utils.py` - Meta-programming utilities
- `admin.py` - Django admin configuration
- `views.py` - API endpoints for design management

## Usage Patterns

### Entity Definition
1. Create DataItem with field specifications
2. Configure inheritance through business_type
3. Add composition via DataItemConsists
4. Generate runtime models through utilities

### Service Configuration
1. Define Service with content type target
2. Add resource requirements
3. Configure ServiceRules for automation
4. Link to forms for UI generation

### Workflow Design
1. Create Event triggers
2. Define system Instructions
3. Configure ServiceRules linking events to actions
4. Test automation through kernel execution

The Design Layer represents the most innovative aspect of the ERP framework - enabling business domain experts to configure complex enterprise systems without traditional development cycles.