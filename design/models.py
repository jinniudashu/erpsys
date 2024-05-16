from django.db import models
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from enum import Enum
import uuid

from pypinyin import Style, lazy_pinyin

class DomainObject(Enum):
    """领域对象枚举类"""
    ENTITY_CLASS = "实体类"
    ENTITY_INSTANCE = "实体实例"
    SERVICE = "服务"
    OPERATION = "作业"
    STATE = "状态"
    EVENT = "事件"
    WORKORDER = "工单"
    ARTIFACT = "工件"
    ATTRIBUTE = "属性"
    RESOURCE = "资源"
    CONTRACT = "合约"
    SYSTEM_OBJECT = "系统对象"
    SYSTEM_SERVICE = "系统服务"
    LABEL = "标签"
    CONCEPT = "概念"
    ELEMENT = "元素"

class ResourceType(Enum):
    """资源类型枚举类"""
    Material = "物料"
    EquipmentWorkingTime = "设备工时"
    OperatorWorkingTime = "人工工时"
    Money = "资金"
    KNOWLEDGE = "知识"

class ServiceType(Enum):
    """服务类型枚举类"""
    OPERATION = "作业"
    SERVICE = "服务"

class FormType(Enum):
    """表单类型枚举类"""
    PRODUCE = "服务作业"
    WORK_ORDER = "服务工单"
    DICT = "字典"
    ENTITY = "实体"
    Document = "文档"


# ERPSys基类
class ERPSysBase(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="标签")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label:
            self.pym = ''.join(lazy_pinyin(self.label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(self.label))

        super().save(*args, **kwargs)


class Field(ERPSysBase):
    Field_type = [('CharField', '单行文本'), ('TextField', '多行文本'), ('IntegerField', '整数'), ('DecimalField', '固定精度小数'), ('DateTimeField', '日期时间'), ('DateField', '日期'),  ('FileField', '文件'), ('RelationField', '关联字段'), ('ComputedField', '计算字段')]
    field_type = models.CharField(max_length=50, default='CharField', choices=Field_type, null=True, blank=True, verbose_name="字段类型")
    related_content = models.CharField(max_length=100, null=True, blank=True, verbose_name="关联内容")
    related_field_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="关联字段名称")
    Choice_type = [('Select', '下拉单选'), ('RadioSelect', '单选按钮列表'), ('CheckboxSelectMultiple', '复选框列表'), ('SelectMultiple', '下拉多选')]
    choice_type = models.CharField(max_length=50, choices=Choice_type, null=True, blank=True, verbose_name="选择类型")
    max_length = models.PositiveSmallIntegerField(default=100, null=True, blank=True, verbose_name="最大长度")
    max_digits = models.PositiveSmallIntegerField(default=10, verbose_name="最大位数", null=True, blank=True)
    decimal_places = models.PositiveSmallIntegerField(default=2, verbose_name="小数位数", null=True, blank=True)
    API_FIELD_TYPE = [('hssc_group_no', '组别'), ('hssc_charge_staff', '责任人'), ('hssc_operator', '作业人员'), ('hssc_scheduled_time', '计划执行时间'), ('hssc_duration', '天数'), ('hssc_frequency', '频次'), ('hssc_name', '姓名'), ('hssc_customer_number', '居民档案号'),  ('hssc_phone_no', '联系电话'), ('hssc_address', '家庭地址')]
    api_field_type = models.CharField(max_length=50, choices=API_FIELD_TYPE, null=True, blank=True, verbose_name="API字段类型")
    API_FIELD_Default_Value = [('CurrentOperator', '当前用户'), ('SystemTime', '当前时间')]
    api_field_default_value = models.CharField(max_length=50, choices=API_FIELD_Default_Value, null=True, blank=True, verbose_name="API字段默认值")
    computed_logic = models.TextField(null=True, blank=True, verbose_name="计算逻辑")
    
    class Meta:
        verbose_name = "表单字段"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return str(self.label)

class Form(ERPSysBase):
    """表单"""
    fields = models.ManyToManyField(Field, through='FormComponents', verbose_name="字段")
    form_type = models.CharField(max_length=50, choices=[(form_type.name, form_type.value) for form_type in FormType], verbose_name="类型")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="描述")

    class Meta:
        verbose_name = "表单"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.name)


class FormComponents(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name="表单")
    component = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="字段")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    inherit_value = models.BooleanField(default=True, verbose_name="继承值")
    is_required = models.BooleanField(default=False, verbose_name="是否必填")
    order = models.PositiveSmallIntegerField(default=10, verbose_name="顺序")

    class Meta:
        verbose_name = "表单字段"
        verbose_name_plural = verbose_name
        ordering = ['order']


# 表单列表字段
class FormListComponents(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name="表单")
    component = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="字段")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    inherit_value = models.BooleanField(default=True, verbose_name="继承值")
    is_required = models.BooleanField(default=False, verbose_name="是否必填")
    order = models.PositiveSmallIntegerField(default=100, verbose_name="顺序")

    class Meta:
        verbose_name = '表单列表字段'
        verbose_name_plural = verbose_name
        ordering = ['order']


# *********************************************************
# DAG 版 ServiceBOM 业务配置
# *********************************************************
"""
[('超声炮', 'EQUIPMENT'), ('肉毒素注射', 'KNOWLEDGE'), ('超声软组织理疗', 'KNOWLEDGE'), ('Q开关激光', 'KNOWLEDGE'), ('保妥适100单位', 'MATERIAL'), ('超声炮刀头', 'MATERIAL'), ('超声炮炮头', 'MATERIAL'), ('乔雅登极致0.8ml', 'MATERIAL'), ('医生', 'OPERATOR'), ('护士', 'OPERATOR'), ('客服', 'OPERATOR'), ('治疗', 'SKILL'), ('随访', 'SKILL'), ('预约', 'SKILL'), ('备料', 'SKILL')]
"""
class ResourceObject(models.Model):
    name = models.CharField(max_length=50, verbose_name="名称")
    resource_type = models.CharField(max_length=50, choices=[(entity_type.name, entity_type.value) for entity_type in ResourceType], verbose_name="类型")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="描述")
    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE, verbose_name="关联内容")
    object_id = models.UUIDField(blank=True, null=True, verbose_name="关联ID")
    content_object = GenericForeignKey('content_type', 'object_id')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "资源对象"
        verbose_name_plural = verbose_name
        ordering = ['resource_type', 'id']
    
    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        try:
            # 创建资源对象时自动在content_type对应的资源类Model中创建一个资源类对象实例
            if self.content_type is None and self.object_id is None:
                # 获取资源Model的名称
                model_class_name = self.resource_type
                model_class = apps.get_model('resource', model_class_name)  # 可能抛出 LookupError
                # 尝试获取ContentType，如果不存在，则抛出ContentType.DoesNotExist异常
                self.content_type = ContentType.objects.get_for_model(model_class)
                instance = model_class.objects.create(name=self.name)
                self.object_id = instance.id
        except LookupError:
            # 处理模型未找到的情况
            print(f"Model '{model_class_name}' not found.")
        except ContentType.DoesNotExist:
            # 处理ContentType未找到的情况
            print(f"ContentType for model '{model_class_name}' does not exist.")
        except Exception as e:
            # 处理其他未预料到的异常
            print(f"An unexpected error occurred: {e}")

        super().save(*args, **kwargs)

class ServiceBOM(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="名称")
    service_type = models.CharField(max_length=50, choices=[(service_type.name, service_type.value) for service_type in ServiceType], verbose_name="服务类型")
    resource_object = models.ForeignKey(ResourceObject, blank=True, null=True, on_delete=models.CASCADE, verbose_name="资源对象")
    work_order = models.ForeignKey(Form, blank=True, null=True, on_delete=models.SET_NULL, related_name="work_order_bom", verbose_name="服务工单")
    produce = models.ForeignKey(Form, blank=True, null=True, on_delete=models.SET_NULL, related_name="produce_bom", verbose_name="服务产出")
    api_fields = models.JSONField(blank=True, null=True, verbose_name="API字段")
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="单位")
    estimated_time = models.IntegerField(blank=True, null=True, verbose_name="预计工时")
    estimated_cost = models.IntegerField(blank=True, null=True, verbose_name="预计成本")
    program = models.JSONField(blank=True, null=True, verbose_name="服务程序")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="描述")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "服务BOM"
        verbose_name_plural = verbose_name
        ordering = ['service_type', 'name', 'id']
    
    def __str__(self):
        return str(self.name)
    
    # def save(self, *args, **kwargs):
    #     if self.work_order is None and self.produce is None:
    #         init_field = Field.objects.get(name='name')

    #         kwargs['name'] = f'表单-服务工单-{self.name}'
    #         kwargs['form_type'] = FormType.WORK_ORDER.name
    #         kwargs['description'] = f'为-{self.name}-自动生成的服务工单'
    #         form_work_order = super().create(*args, **kwargs)
    #         form_work_order.fields.add(init_field)
    #         self.work_order = form_work_order

    #         kwargs['name'] = f'表单-服务产出-{self.name}'
    #         kwargs['form_type'] = FormType.PRODUCE.name
    #         kwargs['description'] = f'为服务BOM-{self.name}-自动生成的服务产出'
    #         produce_form = super().create(*args, **kwargs)
    #         produce_form.fields.add(init_field)
    #         self.produce = produce_form

    #     super().save(*args, **kwargs)

class ServiceBOMDependency(models.Model):
    parent = models.ForeignKey(ServiceBOM, related_name='children', on_delete=models.CASCADE, verbose_name="父组件")
    child = models.ForeignKey(ServiceBOM, related_name='parents', on_delete=models.CASCADE, verbose_name="子组件")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个子组件
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        verbose_name = "组件依赖"
        verbose_name_plural = verbose_name
        ordering = ['id']
        unique_together = ('parent', 'child')  # 确保每对父子组件关系唯一
    
    def __str__(self):
        return f"{self.parent.name} -> {self.child.name}"

class BOMService:
    @staticmethod
    def add_component(name):
        component, created = ServiceBOM.objects.get_or_create(name=name)
        return component

    @staticmethod
    def add_dependency(parent_name, child_name, quantity=1):
        parent = BOMService.add_component(parent_name)
        child = BOMService.add_component(child_name)
        dependency, created = ServiceBOMDependency.objects.get_or_create(parent=parent, child=child)
        dependency.quantity = quantity
        dependency.save()
        return dependency

    @staticmethod
    def find_direct_children(component_name):
        component = ServiceBOM.objects.get(name=component_name)
        children_info = [{'child': dep.child.name, 'quantity': dep.quantity} for dep in component.children.all()]
        return children_info

    @staticmethod
    def find_direct_parents(component_name):
        component = ServiceBOM.objects.get(name=component_name)
        parents_info = [{'parent': dep.parent.name, 'quantity': dep.quantity} for dep in component.parents.all()]
        return parents_info


# 角色表
class Role(ERPSysBase):
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="岗位描述")

    class Meta:
        verbose_name = "业务岗位"
        verbose_name_plural = verbose_name
        ordering = ['id']

# 业务实体
class Entity(ERPSysBase):
    base_form = models.OneToOneField(Form, on_delete=models.SET_NULL, null=True, verbose_name="基础表单")
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属项目")

    class Meta:
        verbose_name = "管理实体"
        verbose_name_plural = verbose_name

# 项目
class Project(ERPSysBase):
    domain = models.CharField(max_length=255, null=True, blank=True, verbose_name="域名")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name='项目描述')  # 项目描述
    roles = models.ManyToManyField(Role, blank=True, verbose_name='角色')  # 项目角色
    # services = models.ManyToManyField(Service, blank=True, verbose_name="服务")

    class Meta:
        verbose_name = '项目列表'
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return str(self.label)

# 输出脚本
class SourceCode(models.Model):
    code = models.TextField(null=True, verbose_name="源代码")
    description = models.TextField(max_length=255, verbose_name="描述", null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, verbose_name="项目")

    class Meta:
        verbose_name = "作业系统脚本"
        verbose_name_plural = verbose_name
        ordering = ['id']