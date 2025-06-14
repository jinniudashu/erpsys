# Applications Layer

The **Application Layer** represents the final instantiation of business domain models configured through the Design Layer. This directory contains concrete business entities automatically generated from DataItem meta-definitions, specifically configured for the aesthetic medical practice domain.

## Purpose

This layer demonstrates how the meta-framework transforms abstract business definitions into operational Django models with:
- Automatic Chinese language support and pinyin generation
- Process integration via foreign key relationships
- Standardized field patterns across all models
- Business logic inheritance from kernel components

## Domain Implementation: Aesthetic Medical Practice

### Dictionary Models (Dict-*)
Core reference data for medical operations:
- **服务类别** (FuWuLeiBie) - Service categories
- **入出库操作** (RuChuKuCaoZuo) - Inventory operations
- **客户来源** (KeHuLaiYuan) - Customer sources
- **症状/诊断** (ZhengZhuang/ZhenDuan) - Symptoms and diagnoses
- **收费类型** (ShouFeiLeiXing) - Billing types

### Resource Models
Resource abstractions from design layer:
- **Material** - Medical supplies with inventory tracking
- **Equipment/Device** - Medical equipment and tools
- **Capital** - Financial resources
- **Knowledge** - Medical knowledge base with file/text storage

### Operational Models
Business process implementations:
- **Profile** - Patient demographics and medical records
- **YuYueJiLu** - Appointment scheduling with service integration
- **WuLiaoTaiZhang** - Material ledger with expiration tracking
- **ZhiLiaoXiangMu** - Treatment records for various procedures

### Treatment Records
Specialized models for aesthetic procedures:
- **RouDuSuZhiLiaoJiLu** - Botox treatment records
- **ChaoShengPaoZhiLiaoJiLu** - Ultrasound cannon treatments
- **ShuiGuangZhenZhiLiaoJiLu** - Hydra needle treatments
- **GuangZiZhiLiaoJiLu** - Photon therapy records

### Financial Models
- **ChongZhiJiLu** - Prepaid account recharges
- **XiaoFeiJiLu/ShouFeiJiLu** - Consumption and billing records
- **ZhiLiaoXiangMuHeXiaoJiLu** - Treatment verification records

### Process Integration Models
- **SuiFangJiLu** - Follow-up care tracking
- **DengLuQianDaoJiLu** - Check-in records
- **YuYueTiXingJiLu** - Appointment reminders

## Model Features

### Standard Fields
All models inherit common patterns:
- `label` - Chinese display name
- `name` - Pinyin-based system name
- `pym` - Pinyin abbreviation code
- `erpsys_id` - Unique system identifier
- `pid` - Process integration via foreign key
- `created_time/updated_time` - Audit timestamps

### Business Logic
- Automatic pinyin generation from Chinese labels
- UUID-based unique identifiers
- Process binding for workflow integration
- Master-detail relationships via `master` fields

### Process Integration
Models connect to the kernel process engine through:
- **Process foreign keys** - Link records to workflow processes
- **Master relationships** - Connect to Operator entities
- **Service references** - Link to configured service definitions

## Generation Pattern

These models demonstrate runtime generation from design definitions:
1. **DataItem definitions** in design layer specify structure
2. **Meta-programming** generates Django model classes
3. **Process integration** connects to workflow engine
4. **Business logic** inherited from base patterns

The `CLASS_MAPPING` dictionary at the end enables dynamic model access for the framework's meta-programming capabilities.

## Usage

Models are accessed through:
- Django admin interface for data management
- API endpoints for frontend integration
- Process workflow triggers for automation
- MCP server for AI assistant interactions