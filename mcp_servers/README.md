# MCP Server for Django ERP System

This directory contains the Model Context Protocol (MCP) server implementation for the Django ERP system, providing access to DataItem and DataItemConsists models.

## Features

- **DataItem Management**: Create, read, update, delete DataItem records
- **Relationship Management**: Manage DataItemConsists relationships
- **Search & Query**: Search and filter DataItems by various criteria
- **Ancestry Tracking**: Get inheritance chains and composition relationships

## Verification Methods

### 1. Django Management Commands

#### Basic Test
```bash
python manage.py test_mcp_server
```

#### Full Test with Data Creation
```bash
python manage.py test_mcp_server --create-test-data --test-mcp-functions
```

#### Run MCP Server
```bash
python manage.py run_mcp_server
```

### 2. Standalone Verification
```bash
python mcp_servers/verify_mcp.py
```

### 3. STDIO Mode Test
```bash
python test_mcp_stdio.py
```

## Available Tools

- `create_data_item()` - Create new DataItem
- `update_data_item()` - Update existing DataItem
- `delete_data_item()` - Delete DataItem
- `list_data_items()` - List DataItems with filtering
- `search_data_items()` - Search DataItems by text
- `add_data_item_consists()` - Add composition relationship
- `remove_data_item_consists()` - Remove composition relationship

## Available Resources

- `dataitem://{item_id}` - Get specific DataItem
- `dataitem://{item_id}/consists` - Get DataItem composition relationships
- `dataitem://{item_id}/ancestry` - Get DataItem inheritance chain and composition

## Usage Examples

### Creating a DataItem
```python
from mcp_servers.mcp_server import create_data_item

new_item = create_data_item(
    label="新数据项",
    field_type="CharField",
    implement_type="Field",
    max_length=100
)
```

### Searching DataItems
```python
from mcp_servers.mcp_server import search_data_items

results = search_data_items("测试", limit=10)
```

### Getting DataItem with Relationships
```python
from mcp_servers.mcp_server import get_data_item_ancestry

ancestry_data = get_data_item_ancestry(item_id)
print(f"Ancestors: {len(ancestry_data['ancestry'])}")
print(f"Consists: {len(ancestry_data['consists'])}")
```

## Integration with Django

The MCP server is fully integrated with Django:

1. **Django Settings**: Uses `erpsys.settings` configuration
2. **Django Models**: Direct access to `design.models.DataItem` and `DataItemConsists`
3. **Django ORM**: All database operations use Django ORM
4. **Django Management**: Accessible via Django management commands

## Verification Results

When properly configured, you should see:

```
=== MCP Server Django Integration Test ===
✓ MCP Server imports successfully
✓ Django models accessible. DataItem count: XX
✓ list_data_items returned X items
✓ get_data_item retrieved: [item_label]
✓ get_data_item_consists returned X relations
✓ get_data_item_ancestry returned ancestry: X, consists: X
✓ search_data_items found X items
✓ create_data_item created: [new_item_label] (ID: XX)
=== Test completed ===
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Django is properly configured and the app is in INSTALLED_APPS
2. **Database Errors**: Run migrations if DataItem tables don't exist
3. **UUID Validation**: The server handles UUID to string conversion automatically

### Debug Mode

Set Django DEBUG=True for detailed error messages during development.

## Server Information

- **Server Name**: ERPSysDataItemMCP
- **Transport**: STDIO (default)
- **Protocol**: Model Context Protocol (MCP)
- **Django Integration**: Full ORM access 