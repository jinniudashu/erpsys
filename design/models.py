from django.db import models
from django.db.models import Q
from django.db.utils import IntegrityError
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

import uuid
import re
import json
from pypinyin import Style, lazy_pinyin

from design.types import FieldType, ChoiceType, FormType, SystemResourceType, ServiceType
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
            label = re.sub(r'[^\u4e00-\u9fa5]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            # 使用正则表达式过滤掉label非汉字内容, 截取到8个汉字以内
            self.name = "_".join(lazy_pinyin(label[:8]))
            self.label = label
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

class VocabularyManager(models.Manager):
    def refresh(self):
        # 刷新所有的业务词汇
        for model in ['DataItem', 'Service',]:
            model_class = apps.get_model('design', model)
            for instance in model_class.objects.all():
                content_type=ContentType.objects.get_for_model(model_class)
                object_id=instance.id                    
                vocab, created = Vocabulary.objects.update_or_create(
                    content_type=content_type,
                    object_id=object_id,
                    defaults={'name': instance.name, 'label': instance.label, 'pym': instance.pym}
                )
                # 更新实例的Vocabulary外键
                instance.vocabulary = vocab
                instance.save()

class Vocabulary(ERPSysBase):
    q  = Q(app_label='design') & (Q(model = 'dataitem') | Q(model = 'service'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=q , null=True, blank=True, verbose_name="词汇类型")
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    objects = VocabularyManager()

    class Meta:
        verbose_name = "业务语汇"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.label

class DataItem(ERPSysBase):
    vocabulary = models.OneToOneField(Vocabulary, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="业务词汇")
    field_type = models.CharField(max_length=50, default='CharField', choices=FieldType, null=True, blank=True, verbose_name="数据项类型")
    related_dictionary = models.ForeignKey('DataItemDict', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="数据项定义")
    max_length = models.PositiveSmallIntegerField(default=100, null=True, blank=True, verbose_name="最大长度")
    max_digits = models.PositiveSmallIntegerField(default=10, verbose_name="最大位数", null=True, blank=True)
    decimal_places = models.PositiveSmallIntegerField(default=2, verbose_name="小数位数", null=True, blank=True)
    computed_logic = models.TextField(null=True, blank=True, verbose_name="计算逻辑")
    is_entity = models.BooleanField(default=False, verbose_name="业务实体")
    
    class Meta:
        verbose_name = "数据项"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return self.label

class DataItemDictManager(models.Manager):
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
                        dict, created = self.get_or_create(label=label)
                        if created:
                            dict.data_items.add(zhi_data_item)
                            dict.init_content = json.dumps([{'值': item} for item in enum], ensure_ascii=False)
                            dict.save()
                            # 向表单添加字典对应的数据项
                            form.data_items.add(dict.data_item)
                            print(f"Created DataItemDict: {dict}")
                except IntegrityError as e:
                    print(f"Error creating field: {e}")

        zhi_data_item = DataItem.objects.get_or_create(label='值', defaults={'field_type': 'CharField'})[0]
        for form in forms:
            entries = form.get('entries', [])
            _form = Form.objects.get_or_create(label=form['label'], defaults={'form_type': FormType.PRODUCE.name})[0]
            for entry in entries:
                _process_entry(entry, _form)

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
            dict = self.get_or_create(label=sheet_name)[0]

            # Parse the sheet into a DataFrame
            df = pd.read_excel(xls, sheet_name=sheet_name)

            # Parse the column names and their types
            fields = [{'name': col, 'type': dtype_map.get(str(df[col].dtype), 'CharField')} for col in df.columns]
            for field in fields:
                data_item = DataItem.objects.get_or_create(label=field['name'], defaults={'field_type': field['type']})[0]
                dict.data_items.add(data_item)
            
            # Parse the sheet data into a list of dictionaries
            data = df.to_dict(orient='records')
            dict.init_content = json.dumps(data, ensure_ascii=False)
            dict.save()

            # Add parsed information to the result
            result[sheet_name] = {
                'fields': fields,
                'data': data
            }
            print(f"Created DataItemDict: {sheet_name}, {result[sheet_name]}")

class DataItemDict(GenerateScriptMixin, ERPSysBase):
    data_item = models.OneToOneField(DataItem, on_delete=models.SET_NULL, related_name='data_item_dict', null=True, blank=True, verbose_name="数据项")
    data_items = models.ManyToManyField(DataItem, through='DataItemDictDetail', related_name='data_item_dicts', verbose_name="字段")
    system_resource_type = models.CharField(max_length=50, choices=[(entity_type.name, str(entity_type)) for entity_type in SystemResourceType], null=True, blank=True, verbose_name="系统资源类型")
    bind_system_object = models.CharField(max_length=50, choices=GLOBAL_INITIAL_STATES['SystemObject'], null=True, blank=True, verbose_name="绑定系统对象")
    init_content = models.JSONField(blank=True, null=True, verbose_name="初始内容")
    objects = DataItemDictManager()

    class Meta:
        verbose_name = "数据项字典"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.label
            
class DataItemDictDetail(models.Model):
    data_item_dict = models.ForeignKey(DataItemDict, on_delete=models.CASCADE, verbose_name="数据项字典")
    data_item = models.ForeignKey(DataItem, on_delete=models.CASCADE, null=True, verbose_name="数据项")
    is_multivalued= models.BooleanField(default=False, verbose_name="多值")
    default_value_char = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    order = models.PositiveSmallIntegerField(default=10, verbose_name="顺序")

    class Meta:
        verbose_name = "字典详情"
        verbose_name_plural = verbose_name
        ordering = ['order']

class Service(GenerateScriptMixin, ERPSysBase):
    vocabulary = models.OneToOneField(Vocabulary, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="业务词汇")
    form = models.ForeignKey('Form', blank=True, null=True, on_delete=models.SET_NULL, verbose_name="表单")
    q = Q(field_type='BusinessObject')
    work_order = models.ForeignKey(DataItem, on_delete=models.SET_NULL, limit_choices_to=q, blank=True, null=True, verbose_name="工单")
    program = models.JSONField(blank=True, null=True, verbose_name="服务程序")
    service_type = models.CharField(max_length=50, choices=[(service_type.name, service_type.value) for service_type in ServiceType], verbose_name="服务类型")
    estimated_time = models.IntegerField(blank=True, null=True, verbose_name="预计工时")
    estimated_cost = models.IntegerField(blank=True, null=True, verbose_name="预计成本")

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
    resource_object = models.ForeignKey(DataItem, on_delete=models.CASCADE, verbose_name="资源对象")
    quantity = models.PositiveIntegerField(default=1)  # 默认为1，至少需要一个单位资源
    
    class Meta:
        verbose_name = "资源组件"
        verbose_name_plural = verbose_name
        ordering = ['id']
    
    def __str__(self):
        return f"{self.service.name} -> {self.resource_object.name}"

class ServiceBOM:
    @staticmethod
    def add_component(name):
        component, created = Service.objects.get_or_create(name=name)
        return component

    @staticmethod
    def add_dependency(parent_name, child_name, quantity=1):
        parent = ServiceBOM.add_component(parent_name)
        child = ServiceBOM.add_component(child_name)
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

class Form(GenerateScriptMixin, ERPSysBase):
    data_items = models.ManyToManyField(DataItem, through='FormComponents', verbose_name="字段")
    form_type = models.CharField(max_length=50, choices=[(form_type.name, form_type.value) for form_type in FormType], verbose_name="类型")

    class Meta:
        verbose_name = "表单"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.label

class FormComponents(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name="表单")
    data_item = models.ForeignKey(DataItem, on_delete=models.CASCADE, null=True, verbose_name="字段")
    default_value = models.CharField(max_length=255, null=True, blank=True, verbose_name="默认值")
    choice_type = models.CharField(max_length=50, choices=ChoiceType, null=True, blank=True, verbose_name="选择类型")
    expand_dict = models.BooleanField(default=False, verbose_name="扩展字典")
    is_required = models.BooleanField(default=False, verbose_name="必填")
    is_list = models.BooleanField(default=False, verbose_name="列表字段")
    order = models.PositiveSmallIntegerField(default=10, verbose_name="顺序")

    class Meta:
        verbose_name = "表单字段"
        verbose_name_plural = verbose_name
        ordering = ['order']

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

# DataItem维护
@receiver(post_save, sender=DataItemDict)
def maintain_field(sender, instance, created, **kwargs):
    if created:
        data_item, created = DataItem.objects.update_or_create(
            name=instance.name, 
            defaults={
                'label': instance.label, 
                'pym': instance.pym,
                'field_type': 'DictionaryField',
                'related_dictionary': instance
            }
        )
        instance.data_item = data_item
        instance.save()
    else:
        field, created = DataItem.objects.update_or_create(
            name=instance.name, 
            defaults={
                'label': instance.label, 
                'pym': instance.pym,
                'field_type': 'DictionaryField',
                'related_dictionary': instance
            }
        )

@receiver(post_delete, sender=DataItemDict)
def delete_field(sender, instance, created, **kwargs):
    try:
        instance.field.delete()
    except:
        pass

# 业务词汇表维护
@receiver(post_save, sender=DataItem)
@receiver(post_save, sender=Service)
def maintain_vocabulary(sender, instance, created, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    object_id = instance.id

    if created:
        # 当实例被创建时，也创建一个新的Vocabulary实例
        vocab = Vocabulary(
            name=instance.name,
            label=instance.label,
            pym=instance.pym,
            content_type=content_type,
            object_id=object_id
        )
        vocab.save()
        instance.vocabulary = vocab
        instance.save()
    else:
        # 更新现有的Vocabulary实例
        vocab, created = Vocabulary.objects.update_or_create(
            content_type=content_type,
            object_id=object_id,
            defaults={
                'name': instance.name, 
                'label': instance.label,
                'pym': instance.pym
            }
        )

# 当模型实例被删除时，也删除对应的Vocabulary实例
@receiver(post_delete, sender=DataItem)
@receiver(post_delete, sender=Service)
def delete_vocabulary(sender, instance, **kwargs):
    if instance.vocabulary:
        instance.vocabulary.delete()

"""
客户 姓名
客户 年龄
客户 性别
客户 初诊日期
作业员 姓名
标准工单 日期
耗材 名称
耗材 规格
耗材 价格
耗材 库存数量
耗材 最小库存数量
耗材 条形码
耗材 SKU ID
诊室 名称
诊室 规格

"""