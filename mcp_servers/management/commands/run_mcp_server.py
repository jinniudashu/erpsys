from django.core.management.base import BaseCommand
import sys
import os


class Command(BaseCommand):
    help = 'Run the MCP Server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--transport',
            type=str,
            default='stdio',
            help='Transport method (stdio, sse, etc.)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting MCP Server...'))
        
        try:
            # Import and run the MCP server
            from mcp_servers.mcp_server import mcp
            
            transport = options['transport']
            self.stdout.write(f'Running MCP Server with {transport} transport...')
            
            if transport == 'stdio':
                mcp.run()
            else:
                self.stdout.write(self.style.ERROR(f'Transport {transport} not supported yet'))
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('MCP Server stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'MCP Server failed to start: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc())) 