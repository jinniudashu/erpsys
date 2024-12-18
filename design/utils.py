from django.core.management import call_command
from django.utils import timezone
from django.db.models import Count
from django.utils.dateparse import parse_time, parse_date, parse_datetime
from django.core.exceptions import ValidationError
from django.db import models

import logging
import json

from design.models import DataItem, DESIGN_CLASS_MAPPING, Organization as design_Organization, Role as design_Role, Operator as design_Operator, Resource as design_Resource, Material as design_Material, Equipment as design_Equipment, Device as design_Device, Capital as design_Capital, Knowledge as design_Knowledge, Service as design_Service, Event as design_Event, Instruction as design_Instruction, ServiceProgram as design_ServiceProgram, ServiceRule as design_ServiceRule, WorkOrder as design_WorkOrder, Form as design_Form
from design.models import ServiceConsists, MaterialRequirements, EquipmentRequirements, DeviceRequirements, CapitalRequirements, KnowledgeRequirements
from design.script_file_header import ScriptFileHeader, get_master_field_script, get_admin_script, get_model_footer

from kernel.models import Organization as kernel_Organization, Role as kernel_Role, Operator as kernel_Operator, Resource as kernel_Resource, Service as kernel_Service, Event as kernel_Event, Instruction as kernel_Instruction, ServiceProgram as kernel_ServiceProgram, ServiceRule as kernel_ServiceRule, WorkOrder as kernel_WorkOrder, Form as kernel_Form, SysParams as kernel_SysParams
from applications.models import CLASS_MAPPING
# Material as applications_Material, Equipment as applications_Equipment, Device as applications_Device, Capital as applications_Capital, Knowledge as applications_Knowledge

COPY_CLASS_MAPPING = {
    # 基础模型（无依赖）
    "Organization": (design_Organization, kernel_Organization),
    "Resource": (design_Resource, kernel_Resource),
    "Event": (design_Event, kernel_Event),
    "Instruction": (design_Instruction, kernel_Instruction),
    "Form": (design_Form, kernel_Form),
    # "Material": (design_Material, applications_Material),
    # "Equipment": (design_Equipment, applications_Equipment),
    # "Device": (design_Device, applications_Device),
    # "Capital": (design_Capital, applications_Capital),
    # "Knowledge": (design_Knowledge, applications_Knowledge),
    
    # 一级依赖
    "Service": (design_Service, kernel_Service),      # 先复制Service，因为Role依赖它
    "Role": (design_Role, kernel_Role),              # Role依赖Service
    
    # 二级依赖
    "Operator": (design_Operator, kernel_Operator),   # 依赖Organization和Role
    "ServiceProgram": (design_ServiceProgram, kernel_ServiceProgram),  # 依赖Operator
    
    # 三级依赖
    "ServiceRule": (design_ServiceRule, kernel_ServiceRule),  # 依赖Service、Event、Instruction、ServiceProgram
    "WorkOrder": (design_WorkOrder, kernel_WorkOrder),  # 业务上依赖Service
}

# 生成脚本, 被design.admin调用
def generate_source_code(project):
    # 将设计内容添加到design和applications
    def import_init_data_from_data_item():
        def convert_value(value, field_type, dict_model_class):
            """
            转换数据类型
            """
            match field_type:
                case 'CharField', 'TextField':
                    return str(value)
                case 'IntegerField':
                    return int(value)
                case 'FloatField', 'DecimalField':
                    print('DecimalField:', value)
                    return float(value)
                case 'BooleanField':
                    return bool(value)
                case 'TimeField':
                    return parse_time(value)
                case 'DateField':
                    return parse_date(value)
                case 'DateTimeField':
                    return parse_datetime(value)
                case 'TypeField':
                    # 外键类型,返回dict_model_class.objects.get(label=value)的实例
                    if value and dict_model_class:
                        try:
                            return dict_model_class.objects.get(label=value)
                        except dict_model_class.DoesNotExist:
                            logging.warning(f"No {dict_model_class.__name__} instance found with label '{value}'. Returning None.")
                            return None
                case _:
                    return value  # 对于其他类型，保持原样

        def insert_to_model(model_class):
            if not model_class:
                print(f"Class not found for label: {item.label}")
                return

            init_content_list = json.loads(item.init_content)
            for content_dict in init_content_list:
                name_dict = {}
                lookup_fields = {}  # 用于查找已存在记录的字段

                for key, value in content_dict.items():
                    try:
                        key_data_item = DataItem.objects.get(label=key)
                        field_name = key_data_item.name
                        field_type = key_data_item.field_type
                        
                        class_name, dict_model_class = None, None
                        # 如果字段类型是'TypeField'且实现类型是'Model', 使用data_item类名；如果实现类型是'Field', 使用data_item.business_type的类名
                        if field_type == 'TypeField':
                            if key_data_item.implement_type == 'Model':
                                class_name = key_data_item.get_data_item_class_name()
                            elif key_data_item.implement_type == 'Field':
                                class_name = key_data_item.business_type.get_data_item_class_name()
                            dict_model_class = CLASS_MAPPING.get(class_name, None)

                        converted_value = convert_value(value, field_type, dict_model_class)
                        name_dict[field_name] = converted_value

                        # 使用label作为查找条件
                        if field_name == 'label' and converted_value:
                            lookup_fields[field_name] = converted_value

                    except DataItem.DoesNotExist:
                        logging.warning(f"DataItem with label '{key}' not found. Skipping this field.")
                    except ValueError as e:
                        logging.error(f"Error converting value for field '{key}': {str(e)}")
                
                if name_dict:
                    try:
                        # 使用label查找或创建
                        instance, created = model_class.objects.update_or_create(
                            label=lookup_fields['label'],
                            defaults=name_dict
                        )

                        action = "Created" if created else "Updated"
                        logging.info(f"{action} {model_class.__name__} instance: {name_dict}")
                        
                    except ValidationError as e:
                        logging.error(f"Validation error for {model_class.__name__} instance: {str(e)}")
                    except Exception as e:
                        logging.error(f"Error handling {model_class.__name__} instance: {str(e)}")
                else:
                    logging.warning(f"No valid fields found for {model_class.__name__}. Skipping creation.")

        for item in DataItem.objects.filter(field_type__in = ['TypeField', 'Reserved'], init_content__isnull=False):
            if item.field_type == 'Reserved':
                class_name = item.name
                model_class = DESIGN_CLASS_MAPPING.get(class_name)
            else:
                class_name = item.get_data_item_class_name()
                model_class = CLASS_MAPPING.get(class_name)

            print('导入初始数据：', class_name, item.init_content)
            insert_to_model(model_class)

    # 将设计内容加载到运行时kernel
    def copy_design_to_kernel():
        def handle_foreign_key(field, value):
            if value is None:
                return None
            related_model = field.related_model
            if related_model.__name__ in COPY_CLASS_MAPPING:
                _, target_related_model = COPY_CLASS_MAPPING[related_model.__name__]
                try:
                    # 使用 erpsys_id 查找对应的目标模型实例
                    return target_related_model.objects.get(erpsys_id=value.erpsys_id)
                except target_related_model.DoesNotExist:
                    print(f"Warning: No matching {target_related_model.__name__} found for erpsys_id={value.erpsys_id}")
                    return None
            return value

        def prepare_service_config(service):
            return {
                "erpsys_id": service.erpsys_id,
                "serve_content_type": service.serve_model_name,
                "consists": [
                    {"erpsys_id": sub.sub_service.erpsys_id, "name": sub.sub_service.name, "quantity": sub.quantity}
                    for sub in ServiceConsists.objects.filter(service=service)
                ],
                "action": {
                    "action_func_name": service.action_func_name,
                    "action_api_url": service.action_api.url if service.action_api else None,
                    "action_api_params": service.action_api_params
                },
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
                "subject": {
                    "erpsys_id": service.subject.erpsys_id,
                    "name": service.subject.get_data_item_class_name()
                } if service.subject else {},
                "price": str(service.price),
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

        # 按照依赖顺序复制模型
        for model_name, models_tuple in COPY_CLASS_MAPPING.items():
            source_model, target_model = models_tuple
            source_objects = source_model.objects.all()
            object_mapping = {}
            
            print(f"\nProcessing {model_name}...")
            
            # 首先复制基本字段
            for obj in source_objects:
                defaults = {}
                for field in source_model._meta.fields:
                    if field.name in [f.name for f in target_model._meta.fields] and field.name != 'id':
                        value = getattr(obj, field.name)
                        if isinstance(field, models.ForeignKey):
                            value = handle_foreign_key(field, value)
                        defaults[field.name] = value
                
                # 特殊处理Service模型的config字段
                if model_name == "Service":
                    defaults["config"] = prepare_service_config(obj)
                
                new_obj, created = target_model.objects.update_or_create(
                    erpsys_id=obj.erpsys_id,
                    defaults=defaults
                )
                object_mapping[obj] = new_obj
                print(f"{'Created' if created else 'Updated'} {model_name}: {obj.label}")
            
            # 处理多对多字段的关系复制
            for obj in source_objects:
                new_obj = object_mapping[obj]  # 获取之前创建的新对象实例
                # 遍历源模型中的所有多对多字段
                for field in source_model._meta.many_to_many:
                    # 检查目标模型是否也有这个多对多字段
                    if field.name in [f.name for f in target_model._meta.many_to_many]:
                        # 获取源对象中该字段关联的所有对象
                        source_related_objects = getattr(obj, field.name).all()
                        target_related_objects = []

                        # 遍历源对象的每个关联对象
                        for related_obj in source_related_objects:
                            if related_obj:
                                # 获取关联对象的模型类
                                related_model = field.related_model
                                # 检查关联模型是否在需要复制的模型映射中
                                if related_model.__name__ in COPY_CLASS_MAPPING:
                                    # 获取目标关联模型类
                                    _, target_related_model = COPY_CLASS_MAPPING[related_model.__name__]
                                    try:
                                        # 通过 erpsys_id 在目标模型中查找对应的关联对象
                                        target_related_obj = target_related_model.objects.get(erpsys_id=related_obj.erpsys_id)
                                        target_related_objects.append(target_related_obj)
                                        print(f"Added {field.name} relation: {related_obj.label} -> {target_related_obj.label}")
                                    except target_related_model.DoesNotExist:
                                        print(f"Warning: No matching {target_related_model.__name__} found for erpsys_id={related_obj.erpsys_id}")

                        # 如果找到了对应的目标关联对象，则建立多对多关系
                        if target_related_objects:
                            getattr(new_obj, field.name).set(target_related_objects)

        # CreateOrUpdate entity_content_types to kernel.SysParams
        entity_content_types = design_Service.get_unique_content_types()
        kernel_SysParams.objects.update_or_create(
            label='实体类型',
            defaults={
                'config': entity_content_types
            }
        )

    # 生成脚本
    def generate_script(data_item):
        def _generate_field_definitions(data_item):
            field_definitions = ''
            field_type_dict = {}

            data_item_consists = data_item.subset.all().order_by('order')
            
            sub_data_items = DataItem.objects.filter(id__in=data_item_consists.values_list('sub_data_item', flat=True))
            _items_with_non_unique_business_type = sub_data_items.values('business_type').annotate(business_type_count=Count('id')).filter(business_type_count__gt=1)
            fields_need_related_name = sub_data_items.filter(business_type__in=[item['business_type'] for item in _items_with_non_unique_business_type])

            for item in data_item_consists:
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
                    case 'TimeField':
                        field_definitions += f"    {field_name} = models.TimeField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'JSONField':
                        field_definitions += f"    {field_name} = models.JSONField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'FileField':
                        field_definitions += f"    {field_name} = models.FileField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    case 'TypeField':
                        _field_type = ''
                        _related_name = ''
                        if consist_item.business_type:
                            _field_type = consist_item.business_type.get_data_item_class_name()
                            if consist_item in fields_need_related_name:
                                _related_name =  f"related_name='{field_name}_{data_item.name}', "
                        else:
                            _field_type = consist_item.get_data_item_class_name()
                        if consist_item.is_multivalued:
                            field_definitions += f"    {field_name} = models.ManyToManyField({_field_type}, related_name='{field_name}', blank=True, verbose_name='{consist_item.label}')\n"
                        else:
                            field_definitions += f"    {field_name} = models.ForeignKey({_field_type}, on_delete=models.SET_NULL, blank=True, null=True, {_related_name}verbose_name='{consist_item.label}')\n"
                        field_type_dict.update({field_name: _field_type})
                    case 'User':
                        field_definitions += f"    {field_name} = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                        field_type_dict.update({field_name: 'User'})
                    case 'ComputedField':
                        pass
                    case _:
                        pass

            return field_definitions, field_type_dict

        def _generate_model_footer_script(data_item, is_dict):
            verbose_name = data_item.label
            if is_dict:
                verbose_name = f'Dict-{data_item.label}'
            else:
                verbose_name = f'{data_item.label}'
            return get_model_footer(verbose_name)

        is_dict = (data_item.dependency_order < 20)
    
        if data_item.field_type == 'Reserved':
            model_head = f'class {data_item.name}(models.Model):'
        else:
            model_head = f'class {data_item.get_data_item_class_name()}(models.Model):'
        model_head = model_head + ScriptFileHeader['class_base_fields']

        # 添加master ForeignKey
        if data_item.affiliated_to is not None:
            master = data_item.affiliated_to
            while master.implement_type == 'Field':
                master = master.business_type
            model_head = model_head + get_master_field_script(data_item, master.get_data_item_class_name())
        
        model_fields, fields_type_dict = _generate_field_definitions(data_item)
        model_footer = _generate_model_footer_script(data_item, is_dict)
        model_script = f'{model_head}{model_fields}{model_footer}\n'

        # construct admin script
        if data_item.business_type is None:
            class_name = data_item.get_data_item_class_name()
        else:
            class_name = data_item.name
        admin_script = get_admin_script(class_name, is_dict)

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
            class_name = item.get_data_item_class_name()
        class_mappings_str = f'{class_mappings_str}    "{class_name}": {class_name},\n'

    models_script = models_script + class_mappings_str + '}\n\n'
    fields_type_script = f'{fields_type_script}{fields_type}'

    print('写入项目文件...')
    object_files = [
        (f'./applications/models.py', models_script),
        (f'./applications/admin.py', admin_script),
        (f'./kernel/app_types.py', fields_type_script),
    ]
    for file_name, content in object_files:
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    # migrate applications 数据库
    try:
        print(f"开始迁移应用...")
        call_command('makemigrations', 'applications', '--noinput')
        print(f"创建迁移脚本成功")
        call_command('migrate', 'applications', '--noinput')
        print(f"迁移applications数据库成功")
    except Exception as e:
        print(f"Error migrating 'applications': {e}")
        return f"Error migrating 'applications': {e}"

    # 导入初始业务数据to kernel & applications
    print('导入初始业务数据...')
    # 将设计内容加载到运行时kernel
    copy_design_to_kernel()
    # 根据 DataItem 的 field_type，将初始数据导入到对应的 design 或 applications 模型中
    import_init_data_from_data_item()
