from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management import call_command
from django.utils import timezone

import json
from collections import defaultdict

from design.specification import GLOBAL_INITIAL_STATES
from design.script_file_header import ScriptFileHeader
from design.models import DataItem, DESIGN_CLASS_MAPPING, Role as design_Role, Operator as design_Operator, Resource as design_Resource, Material as design_Material, Equipment as design_Equipment, Device as design_Device, Capital as design_Capital, Knowledge as design_Knowledge, Service as design_Service, Event as design_Event
from design.models import ServiceConsists, FormConfig, MaterialRequirements, EquipmentRequirements, DeviceRequirements, CapitalRequirements, KnowledgeRequirements
from design.script_file_header import ScriptFileHeader, get_admin_script, get_model_footer

from kernel.models import Role as kernel_Role, Operator as kernel_Operator, Resource as kernel_Resource, Service as kernel_Service, Event as kernel_Event
from applications.models import CLASS_MAPPING, Material as applications_Material, Equipment as applications_Equipment, Device as applications_Device, Capital as applications_Capital, Knowledge as applications_Knowledge

COPY_CLASS_MAPPING = {
    "Role": (design_Role, kernel_Role),
    "Operator": (design_Operator, kernel_Operator),
    "Resource": (design_Resource, kernel_Resource),
    "Event": (design_Event, kernel_Event),
    "Material": (design_Material, applications_Material),
    "Equipment": (design_Equipment, applications_Equipment),
    "Device": (design_Device, applications_Device),
    "Capital": (design_Capital, applications_Capital),
    "Knowledge": (design_Knowledge, applications_Knowledge),
}

# 加载初始数据
def init_data_loader():
    def import_init_data_from_data_item():
        def insert_to_model(model_class):
            if model_class:
                model_class.objects.all().delete()

                init_content_list = json.loads(item.init_content)
                for content_dict in init_content_list:
                    name_dict = {}
                    for key in content_dict:
                        key_data_item = DataItem.objects.get(label=key)
                        name_dict[key_data_item.name] = content_dict[key]
                        print(name_dict)
                    
                    model_class.objects.create(**name_dict)
            else:
                # 处理未找到对应类的情况
                print(f"Class not found for label: {item.label}")

        for item in DataItem.objects.filter(field_type__in = ['TypeField', 'Reserved'], init_content__isnull=False):
            if item.field_type == 'Reserved':
                class_name = item.name
                model_class = DESIGN_CLASS_MAPPING.get(class_name)
                insert_to_model(model_class)
            else:
                class_name = item.get_data_item_classname()
            model_class = CLASS_MAPPING.get(class_name)
            insert_to_model(model_class)
            print(class_name, item.init_content)

    def copy_design_to_kernel():
        for model_name, models in COPY_CLASS_MAPPING.items():
            source_model, target_model = models
            # 删除目标模型中的所有数据
            target_model.objects.all().delete()
            # 从源模型中读取所有实例
            source_objects = source_model.objects.all()
            target_objects = [
                target_model(**{
                    field.name: getattr(obj, field.name)
                    for field in source_model._meta.fields
                    if field.name in [f.name for f in target_model._meta.fields] and field.name != 'id'
                })
                for obj in source_objects
            ]
            # 批量创建数据，这里用到了bulk_create来优化性能
            target_model.objects.bulk_create(target_objects)
            print(f"Copied {len(target_objects)} records from {source_model.__name__} to {target_model.__name__}.")

    def import_service_from_design():
        services = design_Service.objects.all()
        kernel_Service.objects.all().delete()
        for service in services:
            service_json = {
                "erpsys_id": service.erpsys_id,
                "consists": [
                    {"erpsys_id": sub_service.sub_service.erpsys_id, "name": sub_service.sub_service.name, "quantity": sub_service.quantity}
                    for sub_service in ServiceConsists.objects.filter(service=service)
                ],
                "material_requirements": [
                    {"erpsys_id": req.resource_object.erpsys_id, "name": req.resource_object.name, "quantity": req.quantity}
                    for req in MaterialRequirements.objects.filter(service=service)
                ],
                "equipment_requirements": [
                    {"erpsys_id": req.resource_object.erpsys_id, "name": req.resource_object.name, "quantity": req.quantity}
                    for req in EquipmentRequirements.objects.filter(service=service)
                ],
                "device_requirements": [
                    {"erpsys_id": req.resource_object.erpsys_id, "name": req.resource_object.name, "quantity": req.quantity}
                    for req in DeviceRequirements.objects.filter(service=service)
                ],
                "capital_requirements": [
                    {"erpsys_id": req.resource_object.erpsys_id, "name": req.resource_object.name, "quantity": req.quantity}
                    for req in CapitalRequirements.objects.filter(service=service)
                ],
                "knowledge_requirements": [
                    {"erpsys_id": req.resource_object.erpsys_id, "name": req.resource_object.name, "quantity": req.quantity}
                    for req in KnowledgeRequirements.objects.filter(service=service)
                ],
                "price": str(service.price),
                "subject": {
                    "erpsys_id": service.subject.erpsys_id,
                    "name": service.subject.get_data_item_classname()
                } if service.subject else {},
                "form_config": [
                    {
                        "erpsys_id": config.data_item.erpsys_id,
                        "name": config.data_item.name,
                        "default_value": config.default_value,
                        "readonly": config.readonly,
                        "is_required": config.is_required
                    }
                    for config in FormConfig.objects.filter(service=service)
                ],
                "authorize_roles": [
                    {"erpsys_id": role.erpsys_id, "name": role.name}
                    for role in service.authorize_roles.all()
                ],
                "authorize_operators": [
                    {"erpsys_id": operator.erpsys_id, "name": operator.name}
                    for operator in service.authorize_operators.all()
                ],
                "route_to": {
                    "erpsys_id": service.route_to.erpsys_id,
                    "name": service.route_to.name
                } if service.route_to else {},
                "reference": [
                    {"erpsys_id": item.erpsys_id, "name": item.name}
                    for item in service.reference.all()
                ],
                "program": service.program,
                "service_type": service.service_type
            }

            kernel_Service.objects.create(
                name=service.name,
                label=service.label,
                config=service_json
            )
            print(f"Exported Service {service.name} to kernel")

    import_init_data_from_data_item()
    import_service_from_design()
    copy_design_to_kernel()

# 生成脚本, 被design.admin调用
def generate_source_code(project):
    def write_project_file(file_name, content):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    def migrate_app():
        # try:
        print(f"Start migrating applications...")
        call_command('makemigrations', 'applications')
        call_command('migrate', 'applications', interactive=False)
        print(f"Successfully migrated applications")
        # except Exception as e:
        #     print(f"Error migrating {app_name}: {e}")

    def generate_script(data_item):
        def _generate_field_definitions(data_item):
            field_definitions = ''
            field_type_dict = {}

            for item in data_item.subset.all():
                consist_item = item.sub_data_item
                field_name = consist_item.name
                # 如果字段有业务类型，使用业务类型的字段名，如：计划时间
                if consist_item.business_type and consist_item.business_type.implement_type == 'Field' and consist_item.business_type.field_type == 'Reserved':
                    field_name = consist_item.business_type.name
                field_type = consist_item.field_type
                field_type_dict.update({field_name: field_type})
                match field_type:
                    case 'CharField':
                        field_definitions += f"    {field_name} = models.CharField(max_length={consist_item.max_length}, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'TextField':
                        field_definitions += f"    {field_name} = models.TextField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'IntegerField':
                        field_definitions += f"    {field_name} = models.IntegerField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'BooleanField':
                        field_definitions += f"    {field_name} = models.BooleanField(default=False, verbose_name='{consist_item.label}')\n"
                    case 'DecimalField':
                        field_definitions += f"    {field_name} = models.DecimalField(max_digits={consist_item.max_digits}, decimal_places={consist_item.decimal_places}, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'DateTimeField':
                        field_definitions += f"    {field_name} = models.DateTimeField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'DateField':
                        field_definitions += f"    {field_name} = models.DateField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'JSONField':
                        field_definitions += f"    {field_name} = models.JSONField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'FileField':
                        field_definitions += f"    {field_name} = models.FileField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'TypeField':
                        _field_type = ''
                        if consist_item.business_type:
                            _field_type = consist_item.business_type.name
                        else:
                            _field_type = consist_item.get_data_item_classname()
                        if consist_item.is_multivalued:
                            field_definitions += f"    {field_name} = models.ManyToManyField({_field_type}, related_name='{field_name}', blank=True, verbose_name='{consist_item.label}')\n"
                        else:
                            field_definitions += f"    {field_name} = models.ForeignKey({_field_type}, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                        field_type_dict.update({field_name: _field_type})
                    case 'User':
                        field_definitions += f"    {field_name} = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                        field_type_dict.update({field_name: 'User'})
                    case 'ComputedField':
                        pass
                    case _:
                        pass

            return field_definitions, field_type_dict

        def _generate_model_footer_script(data_item):
            verbose_name = data_item.label
            if data_item.dependency_order == 0:
                verbose_name = f'Dict-{data_item.label}'
            else:
                if data_item.field_type == 'Reserved':
                    verbose_name = f'{data_item.field_type}-{data_item.label}'
                else:
                    verbose_name = f'App-{data_item.label}'
            return get_model_footer(verbose_name)

        if data_item.field_type == 'Reserved':
            model_head = f'class {data_item.name}(models.Model):'
        else:
            model_head = f'class {data_item.get_data_item_classname()}(models.Model):'
        model_head = model_head + ScriptFileHeader['class_base_fields']
        match data_item.name:
            case 'Profile':
                model_head = model_head + ScriptFileHeader['Profile_Reserved_body_script']
        model_fields, fields_type_dict = _generate_field_definitions(data_item)
        model_footer = _generate_model_footer_script(data_item)
        model_script = f'{model_head}{model_fields}{model_footer}\n'

        # construct admin script
        if data_item.business_type is None:
            class_name = data_item.get_data_item_classname()
        else:
            class_name = data_item.name
        admin_script = get_admin_script(class_name)

        return model_script, admin_script, fields_type_dict

    # 生成运行时数据结构代码
    models_script = ScriptFileHeader['models_file_head']
    admin_script =  ScriptFileHeader['admin_file_head']
    fields_type_script = ScriptFileHeader['fields_type_head']
    fields_type = {}
    class_mappings_str = """CLASS_MAPPING = {\n"""

    for item in DataItem.objects.filter(implement_type='Model').order_by('dependency_order'):
        _model_script, _admin_script, _fields_type_dict = generate_script(item)
        models_script = f'{models_script}{_model_script}'
        admin_script = f'{admin_script}{_admin_script}'
        fields_type.update(_fields_type_dict)

        if item.field_type == 'Reserved':
            class_name = item.name
        else:
            class_name = item.get_data_item_classname()
        class_mappings_str = f'{class_mappings_str}    "{class_name}": {class_name},\n'

    models_script = models_script + class_mappings_str + '}\n\n'
    fields_type_script = f'{fields_type_script}{fields_type}'

    print('写入项目文件...')
    object_files = [
        (f'./applications/models.py', models_script),
        (f'./applications/admin.py', admin_script),
        (f'./kernel/app_types.py', fields_type_script),
    ]
    for filename, content in object_files:
        write_project_file(filename, content)

    # makemigrations & migrate
    migrate_app()

    # 导入初始业务数据to kernel & applications
    init_data_loader()

    # source_code = {
    #     'script': {},
    #     'data': {}
    # }
    # source_code['script']['type']['models'] = models_script
    # source_code['script']['type']['admin'] = admin_script
    # result = SourceCode.objects.create(
    #     name = timezone.now().strftime('%Y%m%d%H%M%S'),
    #     project = project,
    #     code = json.dumps(source_code, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder),
    # )
    # print(f'作业脚本写入数据库成功, id: {result}')

# 抽取excel数据
def abstract_excel_data(file_path="design/business_data/preprocessing/initial_data.xlsx"):
    import pandas as pd
    # 将 Pandas 数据类型映射到 Python 的原生数据类型
    dtype_map = {
        'int64': 'IntegerField',
        'float64': 'DecimalField',
        'bool': 'BooleanField',
        'datetime64[ns]': 'DateTimeField',
        'object': 'CharField'
    }    

    # Load the Excel file
    xls = pd.ExcelFile(file_path)

    result = {}
    # Iterate through each sheet
    for sheet_name in xls.sheet_names:
        dict_data_item = DataItem.objects.get_or_create(label=sheet_name, defaults={'field_type': 'TypeField'})[0]

        # Parse the sheet into a DataFrame
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Parse the column names and their types
        fields = [{'name': col, 'type': dtype_map.get(str(df[col].dtype), 'CharField')} for col in df.columns]
        for field in fields:
            data_item = DataItem.objects.get_or_create(label=field['name'], defaults={'field_type': field['type']})[0]
            dict_data_item.consists.add(data_item)
        
        # Parse the sheet data into a list of dictionaries
        dict_data = df.to_dict(orient='records')
        dict_data_item.init_content = json.dumps(dict_data, ensure_ascii=False)
        dict_data_item.save()

        # Add parsed information to the result
        result[sheet_name] = {
            'fields': fields,
            'data': dict_data
        }
        print(f"Created DataItemDict: {sheet_name}, {result[sheet_name]}")

# 抽取Forms数据
def abstract_forms_data(forms=GLOBAL_INITIAL_STATES['Forms']):
    def _map_field_type(f_type):
        mapping = {
            'String': 'CharField',
            'Date': 'DateField',
            'Boolean': 'BooleanField',
            'Integer': 'IntegerField',
            'Decimal': 'DecimalField',
            'Text': 'TextField'
        }
        return mapping.get(f_type, 'CharField')  # Default to 'CharField' if not found

    def _process_entry(entry, form):
        if entry['type'] == 'group':
            for entry in entry['entries']:
                _process_entry(entry, form)
        elif entry['type'] == 'field':
            label = entry.get('label')
            field_type = _map_field_type(entry.get('field_type'))
            enum = entry.get('enum', None)
            try:
                if enum is None:
                    data_item = DataItem.objects.get_or_create(label=label, defaults={'field_type': field_type})[0]
                    # 向表单添加数据项
                    form.data_items.add(data_item)
                    print(f"Created DataItem: {data_item.label if data_item else 'None'}")
                else:
                    dict_data_item, created = DataItem.objects.get_or_create(label=label, defaults={'field_type': 'TypeField'})
                    if created:
                        dict_data_item.consists.add(zhi_data_item)
                        dict_data_item.init_content = json.dumps([{'值': item} for item in enum], ensure_ascii=False)
                        dict_data_item.save()
                    # 向表单添加字典对应的数据项
                    form.data_items.add(dict_data_item)
                    print(f"Created DataItemDict: {dict_data_item}")
            except IntegrityError as e:
                print(f"Error creating field: {e}")

    zhi_data_item = DataItem.objects.get_or_create(label='值', defaults={'field_type': 'CharField'})[0]
    for form in forms:
        entries = form.get('entries', [])
        _form = Form.objects.get_or_create(label=form['label'], defaults={'form_type': FormType.PRODUCE.name})[0]
        for entry in entries:
            _process_entry(entry, _form)
