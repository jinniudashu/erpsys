from django.core.management.base import BaseCommand
from django.core.management import CommandError
from design.models import DataItem, DataItemConsists
import json


class Command(BaseCommand):
    help = 'Test MCP Server integration with Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data for verification',
        )
        parser.add_argument(
            '--test-mcp-functions',
            action='store_true',
            help='Test MCP server functions',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== MCP Server Django Integration Test ==='))
        
        # Test 1: Import MCP Server
        try:
            from mcp_servers.mcp_server import mcp, DataItemSchema, DataItemConsistsSchema
            from mcp_servers.mcp_server import (
                create_data_item, get_data_item, list_data_items, 
                search_data_items, add_data_item_consists
            )
            self.stdout.write(self.style.SUCCESS('✓ MCP Server imports successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ MCP Server import failed: {e}'))
            return

        # Test 2: Django Models Access
        try:
            count = DataItem.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✓ Django models accessible. DataItem count: {count}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Django models access failed: {e}'))
            return

        # Test 3: Create test data if requested
        if options['create_test_data']:
            self.create_test_data()

        # Test 4: Test MCP functions if requested
        if options['test_mcp_functions']:
            self.test_mcp_functions()

        self.stdout.write(self.style.SUCCESS('=== Test completed ==='))

    def create_test_data(self):
        self.stdout.write('Creating test data...')
        
        # Create a parent data item
        parent_item, created = DataItem.objects.get_or_create(
            label='测试父项',
            defaults={
                'field_type': 'CharField',
                'implement_type': 'Model',
                'max_length': 100
            }
        )
        if created:
            self.stdout.write(f'✓ Created parent item: {parent_item.label}')
        else:
            self.stdout.write(f'✓ Parent item exists: {parent_item.label}')

        # Create child data items
        child_item1, created = DataItem.objects.get_or_create(
            label='测试子项1',
            defaults={
                'field_type': 'CharField',
                'implement_type': 'Field',
                'max_length': 50
            }
        )
        if created:
            self.stdout.write(f'✓ Created child item 1: {child_item1.label}')

        child_item2, created = DataItem.objects.get_or_create(
            label='测试子项2',
            defaults={
                'field_type': 'IntegerField',
                'implement_type': 'Field'
            }
        )
        if created:
            self.stdout.write(f'✓ Created child item 2: {child_item2.label}')

        # Create consists relationships
        relation1, created = DataItemConsists.objects.get_or_create(
            data_item=parent_item,
            sub_data_item=child_item1,
            defaults={'order': 1}
        )
        if created:
            self.stdout.write(f'✓ Created consists relation: {parent_item.label} -> {child_item1.label}')

        relation2, created = DataItemConsists.objects.get_or_create(
            data_item=parent_item,
            sub_data_item=child_item2,
            defaults={'order': 2}
        )
        if created:
            self.stdout.write(f'✓ Created consists relation: {parent_item.label} -> {child_item2.label}')

    def test_mcp_functions(self):
        self.stdout.write('Testing MCP server functions...')

        try:
            # Import MCP functions
            from mcp_servers.mcp_server import (
                create_data_item, list_data_items, search_data_items,
                get_data_item, get_data_item_consists, get_data_item_ancestry
            )

            # Test list_data_items
            data_items = list_data_items(limit=5)
            self.stdout.write(f'✓ list_data_items returned {len(data_items)} items')

            if data_items:
                # Test get_data_item
                first_item = data_items[0]
                retrieved_item = get_data_item(first_item.id)
                self.stdout.write(f'✓ get_data_item retrieved: {retrieved_item.label}')

                # Test get_data_item_consists
                consists = get_data_item_consists(first_item.id)
                self.stdout.write(f'✓ get_data_item_consists returned {len(consists)} relations')

                # Test get_data_item_ancestry
                ancestry = get_data_item_ancestry(first_item.id)
                self.stdout.write(f'✓ get_data_item_ancestry returned ancestry: {len(ancestry["ancestry"])}, consists: {len(ancestry["consists"])}')

            # Test search_data_items
            search_results = search_data_items('测试', limit=5)
            self.stdout.write(f'✓ search_data_items found {len(search_results)} items')

            # Test create_data_item
            new_item = create_data_item(
                label='MCP测试项',
                field_type='CharField',
                implement_type='Field',
                max_length=100
            )
            self.stdout.write(f'✓ create_data_item created: {new_item.label} (ID: {new_item.id})')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ MCP function test failed: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc())) 