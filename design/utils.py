from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management import call_command
from django.utils import timezone
import json
from collections import defaultdict

from design.models import *
from design.script_file_header import ScriptFileHeader

# Function to build the inheritance tree
def build_inheritance_tree_with_depth(queryset):
    tree = defaultdict(list)
    root_items = []
    depth_map = {}

    for item in queryset:
        if item.inherit is None:
            root_items.append(item)
            depth_map[item.id] = 0
        else:
            tree[item.inherit_id].append(item)

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

def write_project_file(file_name, content):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(content)

def migrate_app(app_name):
    try:
        call_command('makemigrations', app_name)
        call_command('migrate', app_name)
        print(f"Successfully migrated {app_name}")
    except Exception as e:
        print(f"Error migrating {app_name}: {e}")

# 生成脚本, 被design.admin调用
def generate_source_code(project):
    # 生成models.py, admin.py脚本
    def _generate_models_admin(query_set, domain):

        models_script = ScriptFileHeader['models_file_head']
        admin_script =  ScriptFileHeader['admin_file_head']
        fields_type_script = ScriptFileHeader['fields_type_head']
        fields_type = {}

        for item in query_set:
            script = item.generate_script(domain)            
            models_script = f'{models_script}{script["models"]}'
            admin_script = f'{admin_script}{script["admin"]}'
            fields_type.update(script["fields_type"])

        fields_type_script = f'{fields_type_script}{fields_type}'

        return {'models': models_script, 'admin': admin_script, 'fields_type': fields_type_script}

    # 生成基类脚本baseclass.py
    def _generate_baseclass_script(queryset):
        def _get_field_type(component):
            _type = component.content_type.model
            if _type == 'characterfield':
                return 'String'
            elif _type == 'numberfield':
                return 'Numbers'
            elif _type == 'dtfield':
                return 'Datetime' if component.content_object.type == 'DateTimeField' else 'Date'
            elif _type == 'relatedfield':
                # 返回关联字段的类型: Model name
                model_name = component.content_object.related_content.related_content
                app_label = component.content_object.related_content.related_content_type
                return f'{app_label}.{model_name}'

        # 生成FieldsType内容
        fields_type_script = f'''
from enum import Enum
class FieldsType(Enum):
    # 手工添加CustomerSchedule字段数据类型
    start_time = "Datetime"  # 开始时间
    scheduled_time = "Datetime"  # 计划执行时间
    overtime = "Datetime"  # 超期时限
    scheduled_operator = "entities.Stuff"  # 计划执行人员
    service = "core.Service"  # 服务
    priority_operator = "core.VirtualStaff"  # 虚拟职员
    reference_operation = "core.OperationProc"  # 引用表单
    is_assigned = "Boolean"  # 是否已生成任务

    # 自动生成字段数据类型'''

        for component in queryset:
            field_type = _get_field_type(component)
            fields_type_script = f'{fields_type_script}\n    {component.name} = "{field_type}"  # {component.label}'

        # 获取hsscbase_class脚本内容
        with open('./formdesign/hsscbase_class.py', 'r', encoding="utf8") as f:
            hsscbase_class = f.read()
        
        # 返回合并内容
        return {'hsscbase_class': f'{hsscbase_class}\n\n{fields_type_script}'}

    # 生成业务定义数据
    def _generate_init_data(project):
        # 需要导出的模块清单
        exported_models=[
            Service,
        ]

        models_data = {}
        for model in exported_models:
            # 获取当前model的项目数据
            queryset = project.get_queryset_by_model(model.__name__)
            # 构造model数据
            models_data[model.__name__.lower()]=model.objects.backup_data(queryset)

        return models_data

    source_code = {
        'script': {
            'service': {},
        },
        'data': {
            'core': {},
        }
    }

    # 生成运行时数据结构代码
    _queryset = DataItem.objects.filter(field_type='TypeField')
    tree, root_items, depth_map = build_inheritance_tree_with_depth(_queryset)
    sorted_items, depth_map = get_sorted_items_with_depth(tree, root_items, depth_map)
    # Sort the items by depth first, then by id
    sorted_items.sort(key=lambda x: (depth_map[x.id], x.id))
    source_code['script']['type'] = _generate_models_admin(sorted_items, project.domain)
    print('models:', source_code['script']['type']['models'])
    print('admin:', source_code['script']['type']['admin'])
    print('fields_type:', source_code['script']['type']['fields_type'])

    # 生成服务表单代码
    # project_queryset = project.get_queryset_by_model('Service').order_by('-id')
    # print('project_queryset', project_queryset)
    # source_code['script']['form'] = _generate_models_admin(project_queryset, project.domain)

    # 导出baseclass.py脚本
    
    # 导出业务定义数据
    # source_code['data']['core'] = _generate_init_data(project)

    # result = SourceCode.objects.create(
    #     name = timezone.now().strftime('%Y%m%d%H%M%S'),
    #     project = project,
    #     code = json.dumps(source_code, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder),
    # )
    # print(f'作业脚本写入数据库成功, id: {result}')

    print('写入项目文件...')
    object_files = [
        (f'./{project.name}/models.py', source_code['script']['type']['models']),
        (f'./{project.name}/admin.py', source_code['script']['type']['admin']),
        (f'./kernel/app_types.py', source_code['script']['type']['fields_type']),
    ]
    for filename, content in object_files:
        write_project_file(filename, content)

    # makemigrations & migrate
    migrate_app(project.name)