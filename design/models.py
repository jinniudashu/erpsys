from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q

import uuid
import re

from pypinyin import Style, lazy_pinyin

from design.types import FieldType, ChoiceType, SystemObject, ImplementType, ServiceType
from design.script_file_header import ScriptFileHeader

# ERPSys基类
class ERPSysBase(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.label)

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w\u4e00-\u9fa5]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            # 使用正则表达式过滤掉label非汉字内容, 截取到10个汉字以内
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)

class DataItem(ERPSysBase):
    consists = models.ManyToManyField('self', through='DataItemConsists', related_name='parent', symmetrical=False, verbose_name="数据项组成")
    field_type = models.CharField(max_length=50, default='CharField', choices=FieldType, null=True, blank=True, verbose_name="数据类型")
    business_type = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='instances', null=True, blank=True, verbose_name="业务类型")
    implement_type = models.CharField(max_length=50, choices=ImplementType, default='Field', verbose_name="实现类型")
    dependency_order = models.PositiveSmallIntegerField(default=0, verbose_name="依赖顺序")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    is_multivalued= models.BooleanField(default=False, verbose_name="多值")
    max_length = models.PositiveSmallIntegerField(default=100, null=True, blank=True, verbose_name="最大长度")
    max_digits = models.PositiveSmallIntegerField(default=10, verbose_name="最大位数", null=True, blank=True)
    decimal_places = models.PositiveSmallIntegerField(default=2, verbose_name="小数位数", null=True, blank=True)
    computed_logic = models.TextField(null=True, blank=True, verbose_name="计算逻辑")
    init_content = models.JSONField(blank=True, null=True, verbose_name="初始内容")

    class Meta:
        verbose_name = "数据项"
        verbose_name_plural = verbose_name
        ordering = ['implement_type', 'dependency_order', 'field_type', 'id']

    def _generate_model_script(self):
        fields_script = ''
        field_type_dict = {}
        fields_script, field_type_dict = self._generate_field_definitions()

        return fields_script, field_type_dict

    def _generate_admin_script(self):
        if self.business_type is None:
            class_name = self.get_data_item_classname()
        else:
            class_name = self.business_type.name
        admin_script = f'''
@admin.register({class_name})
class {class_name}Admin(admin.ModelAdmin):
    list_display = [field.name for field in {class_name}._meta.fields]
    list_display_links = ['id']
maor_site.register({class_name}, {class_name}Admin)
'''        
        return admin_script

    def _generate_field_definitions(self):
        field_definitions = ''
        field_type_dict = {}

        for consist_item in self.consists.all():
            field_name = consist_item.name
            field_type = consist_item.field_type
            field_type_dict.update({field_name: field_type})
            match field_type:
                case 'CharField':
                    field_definitions += f"    {field_name} = models.CharField(max_length={consist_item.max_length}, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                case 'TextField':
                    field_definitions += f"    {field_name} = models.TextField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
                case 'IntegerField':
                    field_definitions += f"    {field_name} = models.IntegerField(blank=True, null=True, verbose_name='{consist_item.label}')\n"
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
                    if consist_item.business_type:
                        _field_type = consist_item.business_type.name
                        if consist_item.is_multivalued:
                            field_definitions += f"    {field_name} = models.ManyToManyField({_field_type}, related_name='{field_name}', blank=True, verbose_name='{consist_item.label}')\n"
                        else:
                            field_definitions += f"    {field_name} = models.ForeignKey({_field_type}, on_delete=models.SET_NULL, related_name='{field_name}', blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    else:
                        _field_type = consist_item.get_data_item_classname()
                        field_definitions += f"    {field_name} = models.ForeignKey({_field_type}, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    field_type_dict.update({field_name: _field_type})
                case 'User':
                    field_definitions += f"    {field_name} = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    field_type_dict.update({field_name: 'User'})
                case 'Service':
                    field_definitions += f"    {field_name} = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='{consist_item.label}')\n"
                    field_type_dict.update({field_name: 'Service'})
                case 'ComputedField':
                    pass
                case _:
                    pass

        return field_definitions, field_type_dict

    def _generate_model_footer_script(self):
        verbose_name = self.label
        if self.field_type == 'Reserved':
            verbose_name = f'{self.field_type}-{self.label}'
        if self.dependency_order == 0:
            verbose_name = f'Dict-{self.label}'
        footer = f'''
    class Meta:
        verbose_name = "{verbose_name}"
        verbose_name_plural = verbose_name
        ordering = ["id"]
'''
        return footer
    
    def generate_script(self):
        if self.field_type == 'Reserved':
            model_head = f'class {self.name}(ERPSysBase):\n'
            match self.name:
                # Add Reserved body script here
                case 'Service':
                    model_head = model_head + ScriptFileHeader['Service_Reserved_body_script']
                case 'Form':
                    model_head = model_head + ScriptFileHeader['Form_Reserved_body_script']
        else:
            model_head = f'class {self.get_data_item_classname()}(ERPSysBase):\n'
        model_fields, fields_type_dict = self._generate_model_script()
        model_footer = self._generate_model_footer_script()
        model_script = f'{model_head}{model_fields}{model_footer}\n'

        # construct admin script
        admin_script = self._generate_admin_script()

        return model_script, admin_script, fields_type_dict
    
    def get_data_item_classname(self):
        pinyin_list = lazy_pinyin(self.label)
        class_name = ''.join(word[0].upper() + word[1:] for word in pinyin_list)
        return class_name

    def get_ancestry_and_consists(self):
        """
        Returns two lists:
        1. Ancestry list: A list of DataItem instances from the given item to the root of its inherit tree.
        2. Consists list: A list of DataItem instances that are in the consists field of each item in the ancestry list.
        
        :param item: DataItem instance
        :return: (ancestry_list, consists_list)
        """
        ancestry_list = []
        consists_list = []

        # Traverse up the inheritance tree to find all ancestors
        current_item = self
        while current_item is not None:
            ancestry_list.append(current_item)
            current_item = current_item.business_type

        # Reverse ancestry list to have root at the beginning
        ancestry_list.reverse()
        
        for item in ancestry_list:
            consists_list.extend(item.consists.all())

        return ancestry_list, consists_list

class DataItemConsists(models.Model):
    data_item = models.ForeignKey(DataItem, on_delete=models.CASCADE, related_name='subset', null=True, verbose_name="数据项")
    sub_data_item = models.ForeignKey(DataItem, on_delete=models.CASCADE, related_name='superset', null=True, verbose_name="子数据项")
    order = models.PositiveSmallIntegerField(default=10, verbose_name="顺序")

    class Meta:
        verbose_name = "数据项组成"
        verbose_name_plural = verbose_name
        ordering = ['id']
        unique_together = ('data_item', 'sub_data_item')

class Operator(ERPSysBase):
    class Meta:
        verbose_name = "人员"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Role(ERPSysBase):
    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Material(ERPSysBase):
    class Meta:
        verbose_name = "物料"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Equipment(ERPSysBase):
    class Meta:
        verbose_name = "设备"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Device(ERPSysBase):
    class Meta:
        verbose_name = "器材"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Space(ERPSysBase):
    class Meta:
        verbose_name = "空间"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Capital(ERPSysBase):
    class Meta:
        verbose_name = "资金"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Event(ERPSysBase):
    class Meta:
        verbose_name = "事件"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Information(ERPSysBase):
    class Meta:
        verbose_name = "信息"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Knowledge(ERPSysBase):
    zhi_shi_wen_jian = models.FileField(blank=True, null=True, verbose_name='知识文件')
    zhi_shi_wen_ben = models.TextField(blank=True, null=True, verbose_name='知识文本')

    class Meta:
        verbose_name = "知识"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Form(ERPSysBase):
    consists_config = models.ManyToManyField(DataItem, through='FormComponentsConfig', related_name='root_form', verbose_name="字段配置")

    class Meta:
        verbose_name = "表单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class FormComponentsConfig(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name="表单")
    data_item = models.ForeignKey(DataItem, on_delete=models.CASCADE, verbose_name="字段")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    readonly = models.BooleanField(default=False, verbose_name="只读")
    choice_type = models.CharField(max_length=50, choices=ChoiceType, null=True, blank=True, verbose_name="选择类型")
    is_required = models.BooleanField(default=False, verbose_name="必填")
    is_list = models.BooleanField(default=False, verbose_name="列表字段")
    expand_data_item = models.BooleanField(default=False, verbose_name="展开字段")
    is_aggregate = models.BooleanField(default=False, verbose_name="聚合字段")
    order = models.PositiveSmallIntegerField(default=10, verbose_name="顺序")

    class Meta:
        verbose_name = "表单配置"
        verbose_name_plural = verbose_name
        ordering = ['id']
        
class Service(ERPSysBase):
    consists = models.ManyToManyField('self', through='ServiceConsists', symmetrical=False, verbose_name="服务组成")
    subject = models.ForeignKey(DataItem, on_delete=models.SET_NULL, related_name='served_services', blank=True, null=True, verbose_name="作业对象")
    form = models.OneToOneField(Form, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="表单")
    allowed_roles = models.ManyToManyField(Role, related_name='role_allowed_services', blank=True, verbose_name="允许角色")
    allowed_operators = models.ManyToManyField(Operator, related_name='operator_allowed_services', blank=True, verbose_name="允许操作员")
    route_to = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='routed_services', blank=True, null=True, verbose_name="传递至")
    reference = models.ManyToManyField(DataItem, related_name='referenced_services', blank=True, verbose_name="参考对象")
    program = models.JSONField(blank=True, null=True, verbose_name="服务程序")
    service_type = models.CharField(max_length=50, choices=[(service_type.name, service_type.value) for service_type in ServiceType], verbose_name="服务类型")
    attributes = models.ManyToManyField(DataItem, through='ServiceAttributes', symmetrical=False, verbose_name="属性")

    class Meta:
        verbose_name = "服务"
        verbose_name_plural = verbose_name
        ordering = ['service_type', 'name', 'id']

class ServiceConsists(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='sub_services', verbose_name="服务")
    sub_service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='parent_services', verbose_name="子服务")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "服务组成"
        verbose_name_plural = verbose_name
        ordering = ['id']
        unique_together = ('service', 'sub_service')  # 确保每对父子服务关系唯一
    
    def __str__(self):
        return self.service.name + '->' + self.sub_service.name

class ResourceDependency(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
    resource_object = models.ForeignKey(DataItem, on_delete=models.CASCADE, verbose_name="资源对象")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个单位资源
    
    class Meta:
        verbose_name = "资源组件"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.service.name + '->' + self.resource_object.name

class ServiceAttributes(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
    attribute = models.ForeignKey(DataItem, on_delete=models.CASCADE, verbose_name="属性")

    class Meta:
        verbose_name = "服务属性"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.service.name + '->' + self.attribute.name

class ServiceBOM:
    @staticmethod
    def add_sub_service(name):
        service, created = Service.objects.get_or_create(name=name)
        return service

    @staticmethod
    def add_sub_service(parent_name, sub_name, quantity=1):
        service = ServiceBOM.add_sub_service(parent_name)
        sub_service = ServiceBOM.add_sub_service(sub_name)
        relationship, created = ServiceConsists.objects.get_or_create(service=service, sub_service=sub_service)
        relationship.quantity = quantity
        relationship.save()
        return relationship

    @staticmethod
    def direct_children(component_name):
        service = Service.objects.get(name=component_name)
        sub_services_info = [{{'sub_service': relationship.sub_service.name, 'quantity': relationship.quantity}} for relationship in service.sub_services.all()]
        return sub_services_info

    @staticmethod
    def direct_parents(component_name):
        service = Service.objects.get(name=component_name)
        parent_services_info = [{{'service': relationship.service.name, 'quantity': relationship.quantity}} for relationship in service.parent_services.all()]
        return parent_services_info

class Project(ERPSysBase):
    domain = models.CharField(max_length=255, null=True, blank=True, verbose_name="域名")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name='项目描述')  # 项目描述
    # services = models.ManyToManyField(Service, blank=True, verbose_name="服务")

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name
        ordering = ['id']
    
class SourceCode(models.Model):
    name = models.CharField(max_length=255, null=True, verbose_name="名称")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, verbose_name="项目")
    code = models.TextField(null=True, verbose_name="源代码")
    description = models.TextField(max_length=255, verbose_name="描述", null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  

    class Meta:
        verbose_name = "项目源码"
        verbose_name_plural = verbose_name
        ordering = ['id']

DESIGN_CLASS_MAPPING = {
    "Role": Role,
    "Operator": Operator,
    "Material": Material,
    "Equipment": Equipment,
    "Device": Device,
    "Capital": Capital,
    "Space": Space,
    "Information": Information,
    "Form": Form,
    "Knowledge": Knowledge,
    "Event": Event,
    "Service": Service,
}
