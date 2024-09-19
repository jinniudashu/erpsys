from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

import uuid
import re

from pypinyin import Style, lazy_pinyin

from design.types import FieldType, ChoiceType, ImplementType, ServiceType, ResourceType

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
    sub_class = models.CharField(max_length=255, null=True, blank=True, verbose_name="子类")
    affiliated_to = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='property_set', null=True, blank=True, verbose_name="业务隶属")
    implement_type = models.CharField(max_length=50, choices=ImplementType, default='Field', verbose_name="实现类型")
    dependency_order = models.PositiveSmallIntegerField(default=0, verbose_name="依赖顺序")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    is_multivalued= models.BooleanField(default=False, verbose_name="多值")
    max_length = models.PositiveSmallIntegerField(default=255, null=True, blank=True, verbose_name="最大长度")
    max_digits = models.PositiveSmallIntegerField(default=10, verbose_name="最大位数", null=True, blank=True)
    decimal_places = models.PositiveSmallIntegerField(default=2, verbose_name="小数位数", null=True, blank=True)
    computed_logic = models.TextField(null=True, blank=True, verbose_name="计算逻辑")
    init_content = models.JSONField(blank=True, null=True, verbose_name="初始内容")

    class Meta:
        verbose_name = "数据项"
        verbose_name_plural = verbose_name
        ordering = ['implement_type', 'dependency_order', 'field_type', 'id']

    def __str__(self):
        return self.label

    def get_data_item_class_name(self):
        if self.field_type == 'Reserved':
            return self.name
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
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    map_api_field = models.ForeignKey('ApiFields', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="映射API字段")

    class Meta:
        verbose_name = "数据项组成"
        verbose_name_plural = verbose_name
        ordering = ['order', 'id']
        unique_together = ('data_item', 'sub_data_item')

    def __str__(self):
        return self.sub_data_item.label

class Organization(ERPSysBase):
    class Meta:
        verbose_name = "服务-组织"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Customer(ERPSysBase):
    class Meta:
        verbose_name = "服务-客户"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Role(ERPSysBase):
    services = models.ManyToManyField('Service', related_name='roles', blank=True, verbose_name="服务项目")
    class Meta:
        verbose_name = "服务-角色"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Operator(ERPSysBase):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='design_operator', verbose_name="用户")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="角色")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="组织")

    class Meta:
        verbose_name = "服务-人员"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Resource(ERPSysBase):
    res_type = models.CharField(max_length=50, default='Consumption', choices=ResourceType, null=True, blank=True, verbose_name="资源类型")

    class Meta:
        verbose_name = "服务-资源"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Material(ERPSysBase):
    class Meta:
        verbose_name = "资源-物料"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Equipment(ERPSysBase):
    class Meta:
        verbose_name = "资源-设备"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Device(ERPSysBase):
    class Meta:
        verbose_name = "资源-器材"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Capital(ERPSysBase):
    class Meta:
        verbose_name = "资源-资金"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Knowledge(ERPSysBase):
    zhi_shi_wen_jian = models.FileField(blank=True, null=True, verbose_name='知识文件')
    zhi_shi_wen_ben = models.TextField(blank=True, null=True, verbose_name='知识文本')

    class Meta:
        verbose_name = "资源-知识"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Service(ERPSysBase):
    consists = models.ManyToManyField('self', through='ServiceConsists', symmetrical=False, verbose_name="服务组成")
    material_requirements = models.ManyToManyField(Material, through='MaterialRequirements', verbose_name="物料需求")
    equipment_requirements = models.ManyToManyField(Equipment, through='EquipmentRequirements', verbose_name="设备需求")
    device_requirements = models.ManyToManyField(Device, through='DeviceRequirements', verbose_name="器材需求")
    capital_requirements = models.ManyToManyField(Capital, through='CapitalRequirements', verbose_name="资金需求")
    knowledge_requirements = models.ManyToManyField(Knowledge, through='KnowledgeRequirements', verbose_name="知识需求")
    subject = models.ForeignKey(DataItem, on_delete=models.SET_NULL, limit_choices_to=Q(implement_type='Model'), related_name='served_services', blank=True, null=True, verbose_name="作业记录")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='价格')
    # authorize_roles = models.ManyToManyField(Role, related_name='roles_authorized', blank=True, verbose_name="允许角色")
    # authorize_operators = models.ManyToManyField(Operator, related_name='operators_authorized', blank=True, verbose_name="允许操作员")
    route_to = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='services_routed_from', blank=True, null=True, verbose_name="传递至")
    reference = models.ManyToManyField(DataItem, related_name='referenced_services', blank=True, verbose_name="引用")
    program = models.JSONField(blank=True, null=True, verbose_name="服务程序")
    service_type = models.CharField(max_length=50, choices=[(service_type.name, service_type.value) for service_type in ServiceType], default='OPERATION', verbose_name="服务类型")

    class Meta:
        verbose_name = "服务"
        verbose_name_plural = verbose_name
        ordering = ['service_type', 'id']

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

class MaterialRequirements(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
    resource_object = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="资源对象")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个单位资源
    
    class Meta:
        verbose_name = "物料资源"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.service.name + '->' + self.resource_object.name

class EquipmentRequirements(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
    resource_object = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="资源对象")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个单位资源
    
    class Meta:
        verbose_name = "设备资源"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.service.name + '->' + self.resource_object.name

class DeviceRequirements(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
    resource_object = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="资源对象")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个单位资源
    
    class Meta:
        verbose_name = "器材资源"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.service.name + '->' + self.resource_object.name
    
class CapitalRequirements(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
    resource_object = models.ForeignKey(Capital, on_delete=models.CASCADE, verbose_name="资源对象")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个单位资源
    
    class Meta:
        verbose_name = "资金资源"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.service.name + '->' + self.resource_object.name

class KnowledgeRequirements(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
    resource_object = models.ForeignKey(Knowledge, on_delete=models.CASCADE, verbose_name="资源对象")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个单位资源
    
    class Meta:
        verbose_name = "知识资源"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.service.name + '->' + self.resource_object.name

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

class Event(ERPSysBase):
    description = models.TextField(max_length=255, blank=True, null=True, verbose_name="描述表达式")
    expression = models.TextField(max_length=1024, blank=True, null=True, verbose_name="表达式")
    is_timer = models.BooleanField(default=False, verbose_name="定时事件")
    parameters = models.JSONField(blank=True, null=True, verbose_name="事件参数")

    class Meta:
        verbose_name = "服务-事件"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Instruction(ERPSysBase):
    sys_call = models.CharField(max_length=255, verbose_name="系统调用")
    parameters = models.JSONField(blank=True, null=True, verbose_name="参数")

    class Meta:
        verbose_name = "系统指令"
        verbose_name_plural = verbose_name
        ordering = ['id']

class ServiceRule(ERPSysBase):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True, verbose_name="服务")
    event = models.ForeignKey(Event, on_delete=models.CASCADE,  blank=True, null=True, verbose_name="事件")
    system_operand = models.ForeignKey(Instruction, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='系统指令')
    next_service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, related_name="ruled_as_next_service", verbose_name="后续服务")
    parameter_values = models.JSONField(blank=True, null=True, verbose_name="参数值")
    order = models.SmallIntegerField(default=0, verbose_name="顺序")

    class Meta:
        verbose_name = "服务-规则"
        verbose_name_plural = verbose_name
        ordering = ['event', 'event', 'order']

class Form(ERPSysBase):
    service = models.OneToOneField(Service, on_delete=models.CASCADE, verbose_name="服务")
    fields = models.ManyToManyField(DataItem, through='FormFields', verbose_name="表单字段")
    is_list = models.BooleanField(default=False, verbose_name="列表")

    class Meta:
        verbose_name = "表单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class FormFields(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name="表单")
    field = models.ForeignKey(DataItem, on_delete=models.CASCADE, verbose_name="字段")
    expand_data_item = models.BooleanField(default=False, verbose_name="展开数据项")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    readonly = models.BooleanField(default=False, verbose_name="只读")
    is_required = models.BooleanField(default=False, verbose_name="必填")
    choice_type = models.CharField(max_length=50, choices=ChoiceType, null=True, blank=True, verbose_name="选择类型")
    is_aggregate = models.BooleanField(default=False, verbose_name="聚合字段")
    order = models.PositiveSmallIntegerField(default=10, verbose_name="顺序")

    class Meta:
        verbose_name = "表单字段"
        verbose_name_plural = verbose_name
        ordering = ['order', 'id']
        unique_together = ('form', 'field')

class Api(ERPSysBase):
    provider = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="提供者")
    url = models.CharField(max_length=255, null=True, blank=True, verbose_name="URL")
    RequestMethod = [('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')]
    request_method = models.CharField(max_length=10, null=True, blank=True, choices=RequestMethod, default='POST', verbose_name="请求方法")
    content_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="内容类型")
    response_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="响应类型")
    document_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="文档URL")

    class Meta:
        verbose_name = "外部API"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.label if self.label else ''

class ApiFields(ERPSysBase):
    api = models.ForeignKey(Api, on_delete=models.CASCADE, verbose_name="API")
    ReqRes = [('Request', '请求'), ('Response', '响应')]
    req_res = models.CharField(max_length=50, null=True, blank=True, choices=ReqRes, default='Response', verbose_name="请求/响应")
    field_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="字段名称")
    field_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="字段类型")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")

    class Meta:
        verbose_name = "API字段"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return (f'{self.api.label}_{self.label}') if self.label else ''

class MenuItem(ERPSysBase):
    form = models.OneToOneField(Form, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="表单")
    path = models.CharField(max_length=100, null=True, blank=True, verbose_name="路径")
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name="标题")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="父菜单")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="图标名称")
    redirect = models.CharField(max_length=100, null=True, blank=True, verbose_name="默认子菜单项")
    hide_in_menu = models.BooleanField(default=False, verbose_name="隐藏菜单")
    hide_breadcrumb = models.BooleanField(default=False, verbose_name="隐藏面包屑")

    class Meta:
        verbose_name = "菜单项"
        verbose_name_plural = verbose_name
        ordering = ['id']

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
    "Knowledge": Knowledge,
    "Event": Event,
    "Service": Service,
}
