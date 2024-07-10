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

    def migrate_app():
        # try:
        print(f"Start migrating applications...")
        call_command('makemigrations', 'applications')
        call_command('migrate', 'applications', interactive=False)
        print(f"Successfully migrated applications")
        # except Exception as e:
        #     print(f"Error migrating {app_name}: {e}")

    # 生成models.py, admin.py脚本
    def generate_models_admin_script(query_set):

        models_script = ScriptFileHeader['models_file_head']
        admin_script =  ScriptFileHeader['admin_file_head']
        fields_type_script = ScriptFileHeader['fields_type_head']
        fields_type = {}
        class_mappings_str = """CLASS_MAPPING = {\n"""

        for item in query_set:
            _model_script, _admin_script, _fields_type_dict = item.generate_script()
            models_script = f'{models_script}{_model_script}'
            admin_script = f'{admin_script}{_admin_script}'

            fields_type.update(_fields_type_dict)

            if item.field_type == 'Reserved':
                class_name = item.name
            else:
                class_name = item.get_data_item_classname()
            class_mappings_str = f'{class_mappings_str}    "{class_name}": {class_name},\n'

        class_mappings_str = class_mappings_str + '}\n\n'
        models_script = models_script + class_mappings_str
        fields_type_script = f'{fields_type_script}{fields_type}'

        return models_script, admin_script, fields_type_script

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

    source_code = {
        'script': {},
        'data': {}
    }

    # 生成运行时数据结构代码
    _queryset = DataItem.objects.filter(implement_type='Model').order_by('dependency_order')
    # sorted_items = sort_data_items(_queryset)
    models_script, admin_script, fields_type_script = generate_models_admin_script(_queryset)

    print('写入项目文件...')
    object_files = [
        (f'./applications/models.py', models_script),
        (f'./applications/admin.py', admin_script),
        (f'./kernel/app_types.py', fields_type_script),
    ]
    for filename, content in object_files:
        write_project_file(filename, content)

    # source_code['script']['type']['models'] = models_script
    # source_code['script']['type']['admin'] = admin_script
    # result = SourceCode.objects.create(
    #     name = timezone.now().strftime('%Y%m%d%H%M%S'),
    #     project = project,
    #     code = json.dumps(source_code, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder),
    # )
    # print(f'作业脚本写入数据库成功, id: {result}')

    # makemigrations & migrate
    migrate_app()

    # 导入初始业务数据to kernel & applications
    import_init_data_from_data_item()
    import_service_from_design()
    copy_design_to_kernel()

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
