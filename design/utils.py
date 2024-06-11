from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
import json

from design.models import *
from design.script_file_header import ScriptFileHeader

# 生成脚本, 被design.admin调用
def generate_source_code(project):
    # 生成models.py, admin.py脚本
    def _generate_models_admin(query_set, domain):

        models_script = ScriptFileHeader['models_file_head']
        admin_script =  ScriptFileHeader['admin_file_head']

        for item in query_set:
            # 判断item类型：DataItemDict or Service or Form
            if item.__class__.__name__ == 'DataItemDict':
                pass
            elif item.__class__.__name__ == 'Service':
                pass
            elif item.__class__.__name__ == 'Form':
                pass
            else:
                print(f'未知类型: {item.__class__.__name__}')
                continue
            
            script = item.generate_script(domain)
            models_script = f'{models_script}{script["models"]}'
            admin_script = f'{admin_script}{script["admin"]}'

        return {'models': models_script, 'admin': admin_script, }

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

    # 生成运行时数据结构
    dict_queryset = DataItemDict.objects.all()
    source_code['script']['dictionary'] = _generate_models_admin(dict_queryset, project.domain)  # 导出App:service脚本

    # 生成服务&表单脚本
    project_queryset = project.get_queryset_by_model('Service').order_by('-id')
    print('project_queryset', project_queryset)
    source_code['script']['service'] = _generate_models_admin(project_queryset, project.domain)  # 导出App:service脚本

    # 导出baseclass.py脚本
    # 导出业务定义数据
    # source_code['data']['core'] = _generate_init_data(project)

    result = SourceCode.objects.create(
        name = timezone.now().strftime('%Y%m%d%H%M%S'),
        project = project,
        code = json.dumps(source_code, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder),
    )
    print(f'作业脚本写入数据库成功, id: {result}')

    # # 写入json文件
    # print('开始写入json文件...')
    # with open(f'./define_backup/backup/script/作业系统脚本_{project.name}_{script_name}.json', 'w', encoding='utf-8') as f:
    #     json.dump(source_code, f, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder)
    #     print(f'作业脚本写入成功, id: {script_name}')
