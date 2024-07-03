from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management import call_command
from django.utils import timezone

import json
from collections import defaultdict

from pypinyin import lazy_pinyin

from design.models import *
from design.script_file_header import ScriptFileHeader

from maor.models import class_mappings

# 生成脚本, 被design.admin调用
def generate_source_code(project):
    def sort_data_items(queryset):
        # Function to build the inheritance tree
        def build_inheritance_tree_with_depth(queryset):
            tree = defaultdict(list)
            root_items = []
            depth_map = {}

            for item in queryset:
                if item.business_type is None:
                    root_items.append(item)
                    depth_map[item.id] = 0
                else:
                    tree[item.business_type_id].append(item)

            return tree, root_items, depth_map

        # Recursive function to get sorted items and update depth_map
        def get_sorted_items_with_depth(tree, root_items, depth_map, current_depth=0):
            sorted_items = []

            def recurse(item, depth):
                depth_map[item.id] = depth
                sorted_items.append(item)
                children = tree.get(item.id, [])
                children.sort(key=lambda x: x.id)  # Sort children by id
                for child in children:
                    recurse(child, depth + 1)

            root_items.sort(key=lambda x: x.id)  # Sort root items by id
            for root_item in root_items:
                recurse(root_item, current_depth)

            return sorted_items, depth_map

        tree, root_items, depth_map = build_inheritance_tree_with_depth(queryset)
        sorted_items, depth_map = get_sorted_items_with_depth(tree, root_items, depth_map)

        # 根据外键引用调整深度
        for item in sorted_items:
            print('根据外键引用调整深度')
            print(item, depth_map[item.id])

        # Sort the items by depth first, then by id
        sorted_items.sort(key=lambda x: (depth_map[x.id], x.id))
        print('sorted_items:', sorted_items)
        return sorted_items

    def write_project_file(file_name, content):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    def migrate_app(app_name):
        # try:
        print(f"Start migrating {app_name}...")
        call_command('makemigrations', app_name)
        call_command('migrate', app_name, interactive=False)
        print(f"Successfully migrated {app_name}")
        # except Exception as e:
        #     print(f"Error migrating {app_name}: {e}")

    def import_init_data():
        for item in DataItem.objects.filter(field_type='TypeField', init_content__isnull=False):
            class_name = item.get_data_item_classname()
            print(class_name, item.init_content)
            model_class = class_mappings.get(class_name)
            if model_class:
                model_class.objects.all().delete()

                init_content_list = json.loads(item.init_content)
                for content_dict in init_content_list:
                    name_dict = {}
                    for key in content_dict:
                        key_data_item = DataItem.objects.get(label=key)
                        name_dict = {key_data_item.name: content_dict[key]}
                        print(name_dict)
                    
                    model_class.objects.create(**name_dict)
            else:
                # 处理未找到对应类的情况
                print(f"Class not found for label: {item.label}")

    def import_test_data():
        pass

    # 生成models.py, admin.py脚本
    def generate_models_admin_script(query_set, domain):

        models_script = ScriptFileHeader['models_file_head']
        admin_script =  ScriptFileHeader['admin_file_head']
        fields_type_script = ScriptFileHeader['fields_type_head']
        fields_type = {}
        class_mappings_str = """class_mappings = {\n"""

        for item in query_set:
            script = item.generate_script(domain)
            models_script = f'{models_script}{script["models"]}'
            admin_script = f'{admin_script}{script["admin"]}'

            fields_type.update(script["fields_type"])

            _class_name = item.get_data_item_classname()
            class_mappings_str = f'{class_mappings_str}    "{_class_name}": {_class_name},\n'

        class_mappings_str = class_mappings_str + '}\n\n'
        fields_type_script = f'{fields_type_script}{fields_type}'

        return {'models': models_script + class_mappings_str, 'admin': admin_script, 'fields_type': fields_type_script}

    def generate_forms_script(forms, domain):
        models_script = admin_script = ''

        for form in forms:
            script = form.generate_form_script(domain)            
            models_script = f'{models_script}{script["models"]}'
            admin_script = f'{admin_script}{script["admin"]}'

        return {'models': models_script, 'admin': admin_script}

    source_code = {
        'script': {
            'service': {},
        },
        'data': {
            'core': {},
        }
    }

    # 生成运行时数据结构代码
    _queryset = DataItem.objects.filter(field_type='TypeField').order_by('business_type')
    sorted_items = sort_data_items(_queryset)
    source_code['script']['type'] = generate_models_admin_script(sorted_items, project.domain)

    # 生成服务表单代码
    forms = [service.form for service in project.services.all()]
    source_code['script']['form'] = generate_forms_script(forms, project.domain)

    result = SourceCode.objects.create(
        name = timezone.now().strftime('%Y%m%d%H%M%S'),
        project = project,
        code = json.dumps(source_code, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder),
    )
    print(f'作业脚本写入数据库成功, id: {result}')

    print('写入项目文件...')
    models_script = source_code['script']['type']['models'] + source_code['script']['form']['models']
    admin_script = source_code['script']['type']['admin'] + source_code['script']['form']['admin']
    object_files = [
        (f'./{project.name}/models.py', models_script),
        (f'./{project.name}/admin.py', admin_script),
        (f'./kernel/app_types.py', source_code['script']['type']['fields_type']),
    ]
    for filename, content in object_files:
        write_project_file(filename, content)

    # makemigrations & migrate
    migrate_app(project.name)

    # 写入初始业务数据
    import_init_data()
