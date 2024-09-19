from django.core.management import call_command
from django.utils import timezone
from django.db.models import Count
from django.utils.dateparse import parse_time, parse_date, parse_datetime
from django.core.exceptions import ValidationError

import logging
import json

from design.models import DataItem, DESIGN_CLASS_MAPPING, Customer as design_Customer, Role as design_Role, Operator as design_Operator, Resource as design_Resource, Material as design_Material, Equipment as design_Equipment, Device as design_Device, Capital as design_Capital, Knowledge as design_Knowledge, Service as design_Service, Event as design_Event, Instruction as design_Instruction, ServiceRule as design_ServiceRule
from design.models import ServiceConsists, MaterialRequirements, EquipmentRequirements, DeviceRequirements, CapitalRequirements, KnowledgeRequirements
from design.script_file_header import ScriptFileHeader, get_master_field_script, get_admin_script, get_model_footer

from kernel.models import Customer as kernel_Customer, Role as kernel_Role, Operator as kernel_Operator, Resource as kernel_Resource, Service as kernel_Service, Event as kernel_Event, Instruction as kernel_Instruction, ServiceRule as kernel_ServiceRule
from applications.models import CLASS_MAPPING
# Material as applications_Material, Equipment as applications_Equipment, Device as applications_Device, Capital as applications_Capital, Knowledge as applications_Knowledge

COPY_CLASS_MAPPING = {
    "Customer": (design_Customer, kernel_Customer),
    "Role": (design_Role, kernel_Role),
    "Operator": (design_Operator, kernel_Operator),
    "Resource": (design_Resource, kernel_Resource),
    "Event": (design_Event, kernel_Event),
    "Instruction": (design_Instruction, kernel_Instruction),
    # "Material": (design_Material, applications_Material),
    # "Equipment": (design_Equipment, applications_Equipment),
    # "Device": (design_Device, applications_Device),
    # "Capital": (design_Capital, applications_Capital),
    # "Knowledge": (design_Knowledge, applications_Knowledge),
}

# 加载初始数据
def load_init_data():
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
                    # 外键类型,返回dict_model_class.objects.get(label=value)的实例，
                    if value and dict_model_class:
                        try:
                            return dict_model_class.objects.get(label=value)
                        except model_class.DoesNotExist:
                            logging.warning(f"No {class_name} instance found with label '{value}'. Returning None.")
                            return None
                case _:
                    return value  # 对于其他类型，保持原样

        def insert_to_model(model_class):
            if model_class:
                model_class.objects.all().delete()

                init_content_list = json.loads(item.init_content)
                for content_dict in init_content_list:
                    name_dict = {}
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
                                # 获取类名对应的模型类
                                dict_model_class = CLASS_MAPPING.get(class_name, None)

                            converted_value = convert_value(value, field_type, dict_model_class)
                            name_dict[field_name] = converted_value
                        except DataItem.DoesNotExist:
                            logging.warning(f"DataItem with label '{key}' not found. Skipping this field.")
                        except ValueError as e:
                            logging.error(f"Error converting value for field '{key}': {str(e)}")
                    
                    if name_dict:
                        try:
                            instance = model_class(**name_dict)
                            instance.full_clean()  # 验证所有字段
                            instance.save()
                            logging.info(f"Created new {model_class.__name__} instance: {name_dict}")
                        except ValidationError as e:
                            logging.error(f"Validation error creating {model_class.__name__} instance: {str(e)}")
                        except Exception as e:
                            logging.error(f"Error creating {model_class.__name__} instance: {str(e)}")
                    else:
                        logging.warning(f"No valid fields found for {model_class.__name__}. Skipping creation.")
            else:
                # 处理未找到对应类的情况
                print(f"Class not found for label: {item.label}")

        for item in DataItem.objects.filter(field_type__in = ['TypeField', 'Reserved'], init_content__isnull=False):
            if item.field_type == 'Reserved':
                class_name = item.name
                model_class = DESIGN_CLASS_MAPPING.get(class_name)
            else:
                class_name = item.get_data_item_class_name()
                model_class = CLASS_MAPPING.get(class_name)

            print('插入初始数据：', class_name, item.init_content)
            insert_to_model(model_class)

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
                "subject": {
                    "erpsys_id": service.subject.erpsys_id,
                    "name": service.subject.get_data_item_class_name()
                } if service.subject else {},
                "price": str(service.price),
                # "form_config": [
                #     {
                #         "erpsys_id": config.data_item.erpsys_id,
                #         "name": config.data_item.name,
                #         "default_value": config.default_value,
                #         "readonly": config.readonly,
                #         "is_required": config.is_required
                #     }
                #     for config in FormConfig.objects.filter(service=service)
                # ],
                # "authorize_roles": [
                #     {"erpsys_id": role.erpsys_id, "name": role.name}
                #     for role in service.authorize_roles.all()
                # ],
                # "authorize_operators": [
                #     {"erpsys_id": operator.erpsys_id, "name": operator.name}
                #     for operator in service.authorize_operators.all()
                # ],
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
                erpsys_id=service.erpsys_id,
                config=service_json
            )
            print(f"Exported Service {service.name} to kernel")

        service_rules = design_ServiceRule.objects.all()
        kernel_ServiceRule.objects.all().delete()
        for rule in service_rules:
            kernel_rule = kernel_ServiceRule.objects.create(
                name=rule.name,
                label=rule.label,
                pym=rule.pym,
                erpsys_id=rule.erpsys_id,
                parameter_values=rule.parameter_values,
                order=rule.order,
            )
            _service = kernel_Service.objects.get(erpsys_id=rule.service.erpsys_id)
            kernel_rule.service = _service
            event = kernel_Event.objects.get(erpsys_id=rule.event.erpsys_id)
            kernel_rule.event = event
            system_operand = kernel_Instruction.objects.get(erpsys_id=rule.system_operand.erpsys_id)
            kernel_rule.system_operand = system_operand
            next_service = kernel_Service.objects.get(erpsys_id=rule.next_service.erpsys_id)
            kernel_rule.next_service = next_service
            kernel_rule.save()
            print(f"Exported ServiceRule {kernel_rule} to kernel")

    import_init_data_from_data_item()
    copy_design_to_kernel()
    import_service_from_design()

# 生成脚本, 被design.admin调用
def generate_source_code(project):
    def write_project_file(file_name, content):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    def migrate_app():
        try:
            print(f"Start migrating applications...")
            call_command('makemigrations', 'applications')
            call_command('migrate', 'applications')
            print(f"Successfully migrated applications")
        except Exception as e:
            print(f"Error migrating 'applications': {e}")

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
                if data_item.field_type == 'Reserved':
                    verbose_name = f'{data_item.field_type}-{data_item.label}'
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
    for filename, content in object_files:
        write_project_file(filename, content)

    # makemigrations & migrate
    print('迁移应用...')
    migrate_app()

    # 导入初始业务数据to kernel & applications
    print('导入初始业务数据...')
    load_init_data()

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
