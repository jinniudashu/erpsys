#!/usr/bin/env python
"""
Standalone verification script for MCP Server
This script can be run independently to verify MCP server functionality
"""

import os
import sys
import django

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpsys.settings')
django.setup()

def test_mcp_server():
    """Test MCP server functionality"""
    print("=== MCP Server Verification ===")
    
    try:
        # Test 1: Import MCP Server
        print("1. Testing MCP Server imports...")
        from mcp_servers.mcp_server import (
            mcp, DataItemSchema, DataItemConsistsSchema,
            create_data_item, get_data_item, list_data_items,
            search_data_items, get_data_item_consists, get_data_item_ancestry
        )
        print("   ✓ MCP Server imports successful")
        
        # Test 2: Test Django models access
        print("2. Testing Django models access...")
        from design.models import DataItem, DataItemConsists
        count = DataItem.objects.count()
        print(f"   ✓ DataItem count: {count}")
        
        # Test 3: Test MCP functions
        print("3. Testing MCP functions...")
        
        # List data items
        items = list_data_items(limit=3)
        print(f"   ✓ list_data_items: {len(items)} items")
        
        if items:
            # Get specific item
            item = get_data_item(items[0].id)
            print(f"   ✓ get_data_item: {item.label}")
            
            # Get consists
            consists = get_data_item_consists(items[0].id)
            print(f"   ✓ get_data_item_consists: {len(consists)} relations")
            
            # Get ancestry
            ancestry = get_data_item_ancestry(items[0].id)
            print(f"   ✓ get_data_item_ancestry: {len(ancestry['ancestry'])} ancestors, {len(ancestry['consists'])} consists")
        
        # Search items
        search_results = search_data_items("测试", limit=3)
        print(f"   ✓ search_data_items: {len(search_results)} results")
        
        # Create new item
        new_item = create_data_item(
            label="验证测试项",
            field_type="CharField",
            implement_type="Field"
        )
        print(f"   ✓ create_data_item: {new_item.label} (ID: {new_item.id})")
        
        print("\n=== All tests passed! ===")
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_server_info():
    """Display MCP server information"""
    print("\n=== MCP Server Information ===")
    
    try:
        from mcp_servers.mcp_server import mcp
        
        # Get server info
        print(f"Server Name: {mcp.name}")
        print(f"Server Version: {getattr(mcp, 'version', 'Unknown')}")
        
        # List available tools
        print("\nAvailable Tools:")
        tools = [
            "create_data_item", "update_data_item", "delete_data_item",
            "list_data_items", "search_data_items", "get_data_item",
            "add_data_item_consists", "remove_data_item_consists"
        ]
        for tool in tools:
            print(f"  - {tool}")
        
        # List available resources
        print("\nAvailable Resources:")
        resources = [
            "dataitem://{item_id}",
            "dataitem://{item_id}/consists", 
            "dataitem://{item_id}/ancestry"
        ]
        for resource in resources:
            print(f"  - {resource}")
            
    except Exception as e:
        print(f"Error getting server info: {e}")

if __name__ == "__main__":
    success = test_mcp_server()
    test_mcp_server_info()
    
    if success:
        print("\n🎉 MCP Server is working correctly with Django!")
        sys.exit(0)
    else:
        print("\n❌ MCP Server verification failed!")
        sys.exit(1) 