from django.db import models
from django.db.models import Q
from django.db.utils import IntegrityError
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

import uuid
import re
import json
from pypinyin import Style, lazy_pinyin

from design.types import FieldType, ChoiceType, FormType, ResourceType, ServiceType
from design.business_data.preprocessing.specification import GLOBAL_INITIAL_STATES

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
        if self.label and self.name is None:
            self.pym = ''.join(lazy_pinyin(self.label, style=Style.FIRST_LETTER))
            # 使用正则表达式过滤掉label非汉字内容, 截取到8个汉字以内
            truncated_label = re.sub(r'[^\u4e00-\u9fa5]', '', self.label)[:8]
            self.name = "_".join(lazy_pinyin(truncated_label))
        super().save(*args, **kwargs)

class GenerateScriptMixin(object):
    def _create_model_script(self):
        _fields_script = _autocomplete_fields = _radio_fields = ''
        for form_components in FormComponents.objects.filter(form=self).order_by('position'):
            component=form_components.component

            # construct fields script
            _script = self._create_field_script(component, self)
            
            _fields_script = _fields_script + _script
            
            # 如果是关联字段，构造ModelAdmin内容
            if component.content_object.__class__.__name__ == 'RelatedField':
                field_name = component.content_object.name
                # 判断是否单选，如果是单选，是否Radio
                if component.content_object.related_content.related_content_type == 'dictionaries':
                    if component.content_object.__dict__['type'] == 'RadioSelect':
                        _radio_fields = _radio_fields + f'"{field_name}": admin.VERTICAL, '  # 或admin.HORIZONTAL
                # 判断是否需要autocomplete_fields
                else:
                    _autocomplete_fields = _autocomplete_fields + f'"{field_name}", '

        return _fields_script, _autocomplete_fields, _radio_fields

    def _create_admin_script(self):
        pass 
    
    def _create_field_script(self):
        pass

    def _create_model_footer_script(self):
        pass

    def generate_script(self, domain):
        print(f'Generate Script for {domain}')
        # construct model script
        model_head = f'class {self.name.capitalize()}(models.Model):'
        model_fields, autocomplete_fields, radio_fields = self._create_model_script()
        model_footer = self._create_model_footer_script()
        model_script = f'{model_head}{model_fields}{model_footer}\n\n'
        print(f'Model Script: {model_script}')

        # construct admin script
        modeladmin_body = {}
        if radio_fields:
            modeladmin_body['radio_fields'] = radio_fields
        if autocomplete_fields:
            modeladmin_body['autocomplete_fields'] = autocomplete_fields
        admin_script = self._create_admin_script(modeladmin_body)
        print(f'Admin Script: {admin_script}')

        return {'models': model_script, 'admin': admin_script}

class Field(ERPSysBase):
    field_type = models.CharField(max_length=50, default='CharField', choices=FieldType, null=True, blank=True, verbose_name="字段类型")
    related_dictionary = models.ForeignKey("Dictionary", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联字典")
    is_entity = models.BooleanField(default=False, verbose_name="业务实体")
    choice_type = models.CharField(max_length=50, choices=ChoiceType, null=True, blank=True, verbose_name="选择类型")
    max_length = models.PositiveSmallIntegerField(default=100, null=True, blank=True, verbose_name="最大长度")
    max_digits = models.PositiveSmallIntegerField(default=10, verbose_name="最大位数", null=True, blank=True)
    decimal_places = models.PositiveSmallIntegerField(default=2, verbose_name="小数位数", null=True, blank=True)
    API_FIELD_TYPE = [('hssc_group_no', '组别'), ('hssc_charge_staff', '责任人'), ('hssc_operator', '作业人员'), ('hssc_scheduled_time', '计划执行时间'), ('hssc_duration', '天数'), ('hssc_frequency', '频次'), ('hssc_name', '姓名'), ('hssc_customer_number', '居民档案号'),  ('hssc_phone_no', '联系电话'), ('hssc_address', '家庭地址')]
    api_field_type = models.CharField(max_length=50, choices=API_FIELD_TYPE, null=True, blank=True, verbose_name="API字段类型")
    API_FIELD_Default_Value = [('CurrentOperator', '当前用户'), ('SystemTime', '当前时间')]
    api_field_default_value = models.CharField(max_length=50, choices=API_FIELD_Default_Value, null=True, blank=True, verbose_name="API字段默认值")
    computed_logic = models.TextField(null=True, blank=True, verbose_name="计算逻辑")
    
    class Meta:
        verbose_name = "字段"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.label

class DictionaryManager(models.Manager):
    # 抽取Forms数据
    def abstract_forms_data(self, forms=GLOBAL_INITIAL_STATES['Forms']):
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

        def _process_entry(entry):
            if entry['type'] == 'group':
                for entry in entry['entries']:
                    _process_entry(entry)
            elif entry['type'] == 'field':
                label = entry.get('label')
                field_type = _map_field_type(entry.get('field_type'))
                enum = entry.get('enum', None)
                try:
                    if enum is None:
                        field = Field.objects.get_or_create(label=label, defaults={'field_type': field_type})[0]
                        print(f"Created Field: {field.label if field else 'None'}")
                    else:
                        dictionary, created = self.get_or_create(label=label)
                        if created:
                            field = Field.objects.get_or_create(label='值', defaults={'field_type': field_type})[0]
                            dictionary.fields.add(field)
                            dictionary.content = json.dumps([{'值': item} for item in enum], ensure_ascii=False)
                            dictionary.save()
                            # 创建字典对应的Field对象
                            field, created = Field.objects.get_or_create(label=label, related_dictionary=dictionary, defaults={'field_type': 'DictionaryField'})
                            print(f"Created Dictionary: {field.label if field else 'None'}")
                except IntegrityError as e:
                    print(f"Error creating field: {e}")

        for form in forms:
            entries = form.get('entries', [])
            for entry in entries:
                _process_entry(entry)

    # 抽取excel数据
    def abstract_excel_data(self, file_path="design/business_data/preprocessing/initial_data.xlsx"):
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
            dictionary = self.get_or_create(label=sheet_name)[0]

            # Parse the sheet into a DataFrame
            df = pd.read_excel(xls, sheet_name=sheet_name)

            # Parse the column names and their types
            fields = [{'name': col, 'type': dtype_map.get(str(df[col].dtype), 'CharField')} for col in df.columns]
            for field in fields:
                _field = Field.objects.get_or_create(label=field['name'], defaults={'field_type': field['type']})[0]
                dictionary.fields.add(_field)
            
            # Parse the sheet data into a list of dictionaries
            data = df.to_dict(orient='records')
            dictionary.init_content = json.dumps(data, ensure_ascii=False)
            dictionary.save()

            # 创建字典对应的Field对象
            field = Field.objects.get_or_create(label=sheet_name, related_dictionary=dictionary, defaults={'field_type': 'DictionaryField'})[0]

            # Add parsed information to the result
            result[sheet_name] = {
                'fields': fields,
                'data': data
            }
            print(f"Created Dictionary: {sheet_name}, {result[sheet_name]}")

# 字典列表
class Dictionary(GenerateScriptMixin, ERPSysBase):
    fields = models.ManyToManyField(Field, through='DictionaryFields', verbose_name="字段")
    bind_system_object = models.CharField(max_length=50, choices=GLOBAL_INITIAL_STATES['SystemObject'], null=True, blank=True, verbose_name="绑定系统对象")
    init_content = models.JSONField(blank=True, null=True, verbose_name="初始内容")
    objects = DictionaryManager()

    class Meta:
        verbose_name = "字典"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.label
            
class DictionaryFields(models.Model):
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE, verbose_name="字典")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="字段")
    is_multivalued= models.BooleanField(default=False, verbose_name="多值")
    default_value_char = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    order = models.PositiveSmallIntegerField(default=10, verbose_name="顺序")

    class Meta:
        verbose_name = "字典字段"
        verbose_name_plural = verbose_name
        ordering = ['order']

class Form(GenerateScriptMixin, ERPSysBase):
    fields = models.ManyToManyField(Field, through='FormComponents', verbose_name="字段")
    form_type = models.CharField(max_length=50, choices=[(form_type.name, form_type.value) for form_type in FormType], verbose_name="类型")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="描述")

    class Meta:
        verbose_name = "表单"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.label

class FormComponents(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name="表单")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="字段")
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
    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="字段")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    inherit_value = models.BooleanField(default=True, verbose_name="继承值")
    is_required = models.BooleanField(default=False, verbose_name="是否必填")
    order = models.PositiveSmallIntegerField(default=100, verbose_name="顺序")

    class Meta:
        verbose_name = '表单列表字段'
        verbose_name_plural = verbose_name
        ordering = ['order']

# *********************************************************
# DAG 版 Service 业务配置
# *********************************************************
class ResourceBusinessType(ERPSysBase):
    dictionary = models.ForeignKey(Dictionary, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="字典")
    resource_type = models.CharField(max_length=50, choices=[(entity_type.name, str(entity_type)) for entity_type in ResourceType], verbose_name="资源类型")
    class Meta:
        verbose_name = "资源业务类型"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.label

class Resource(ERPSysBase):
    representation = models.OneToOneField(Field, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="术语表示")
    resource_business_type = models.ForeignKey(ResourceBusinessType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="资源业务类型")

    class Meta:
        verbose_name = "资源"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.label

class Service(GenerateScriptMixin, ERPSysBase):
    form = models.ForeignKey(Form, blank=True, null=True, on_delete=models.SET_NULL, related_name="produce_bom", verbose_name="表单")
    work_order = models.ForeignKey(Dictionary, blank=True, null=True, on_delete=models.SET_NULL, related_name="work_order_bom", verbose_name="工单")
    program = models.JSONField(blank=True, null=True, verbose_name="服务程序")
    service_type = models.CharField(max_length=50, choices=[(service_type.name, service_type.value) for service_type in ServiceType], verbose_name="服务类型")
    estimated_time = models.IntegerField(blank=True, null=True, verbose_name="预计工时")
    estimated_cost = models.IntegerField(blank=True, null=True, verbose_name="预计成本")
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="单位")

    class Meta:
        verbose_name = "服务"
        verbose_name_plural = verbose_name
        ordering = ['service_type', 'name', 'id']
    
    def __str__(self):
        return self.label

class ServiceDependency(models.Model):
    parent = models.ForeignKey(Service, related_name='children', on_delete=models.CASCADE, verbose_name="父服务")
    child = models.ForeignKey(Service, related_name='parents', on_delete=models.CASCADE, verbose_name="子服务组件")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个子服务
    
    class Meta:
        verbose_name = "服务组件"
        verbose_name_plural = verbose_name
        ordering = ['id']
        unique_together = ('parent', 'child')  # 确保每对父子服务关系唯一
    
    def __str__(self):
        return f"{self.parent.name} -> {self.child.name}"

class ResourceDependency(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
    resource_object = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name="资源对象")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个单位资源
    
    class Meta:
        verbose_name = "资源组件"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return f"{self.service.name} -> {self.resource_object.name}"

class BOMService:
    @staticmethod
    def add_component(name):
        component, created = Service.objects.get_or_create(name=name)
        return component

    @staticmethod
    def add_dependency(parent_name, child_name, quantity=1):
        parent = BOMService.add_component(parent_name)
        child = BOMService.add_component(child_name)
        dependency, created = ServiceDependency.objects.get_or_create(parent=parent, child=child)
        dependency.quantity = quantity
        dependency.save()
        return dependency

    @staticmethod
    def find_direct_children(component_name):
        component = Service.objects.get(name=component_name)
        children_info = [{'child': dep.child.name, 'quantity': dep.quantity} for dep in component.children.all()]
        return children_info

    @staticmethod
    def find_direct_parents(component_name):
        component = Service.objects.get(name=component_name)
        parents_info = [{'parent': dep.parent.name, 'quantity': dep.quantity} for dep in component.parents.all()]
        return parents_info

class Vocabulary(ERPSysBase):
    q  = Q(app_label='design') & (Q(model = 'field') | Q(model = 'dictionary'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=q , null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "业务词汇"
        verbose_name_plural = verbose_name
        ordering = ['id']

# class Contract(ERPSysBase):
#     customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, verbose_name="客户")
#     staff = models.ForeignKey('staff.Staff', on_delete=models.CASCADE, verbose_name="员工")
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="服务")
#     start_time = models.DateTimeField(verbose_name="开始时间")
#     end_time = models.DateTimeField(verbose_name="结束时间")
#     price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
#     status = models.CharField(max_length=50, choices=[('draft', '草稿'), ('confirmed', '已确认'), ('cancelled', '已取消')], default='draft', verbose_name="状态")
#     document = models.FileField(upload_to='contract/', verbose_name="合同文件")

# 项目
class Project(ERPSysBase):
    domain = models.CharField(max_length=255, null=True, blank=True, verbose_name="域名")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name='项目描述')  # 项目描述
    services = models.ManyToManyField(Service, blank=True, verbose_name="服务")

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.label

    def get_queryset_by_model(self, model_name):
        if model_name == 'Service':
            return self.services.all()
        # else:
        #     return eval(model_name).objects.all()

# 源码
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
