ScriptFileHeader = {
    'models_file_head': '''from django.db import models
from django.contrib.auth.models import User\n\n''',
    'admin_file_head': '''from django.contrib import admin
from .models import *\n\n''',
    'fields_type_head': '''app_types = ''',
}
