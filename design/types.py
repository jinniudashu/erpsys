from enum import Enum

FieldType = [
    ('CharField', '单行文本'),
    ('IntegerField', '整数'),
    ('BusinessObject', '业务对象'),
    ('DictionaryField', '类型字典'),
    ('DecimalField', '固定精度小数'),
    ('TextField', '多行文本'),
    ('DateTimeField', '日期时间'),
    ('DateField', '日期'),
    ('JSONField', 'JSON'),
    ('FileField', '文件'),
    ('ComputedField', '计算字段'),
]

ChoiceType = [
    ('Select', '下拉单选'),
    ('RadioSelect', '单选按钮列表'),
    ('CheckboxSelectMultiple', '复选框列表'),
    ('SelectMultiple', '下拉多选')
]

class SystemResourceType(Enum):
    """资源类型枚举类"""
    MATERIAL = ("物料", "Consumption")
    EQUIPMENT = ("设备", "TDM")
    DEVICE = ("工具", "Recycle")
    OPERATOR = ("人员", "TDM")
    SPACE = ("空间", "TDM")
    CAPITAL = ("资金", "Consumption")
    KNOWLEDGE = ("知识", "Shared")
    SERVICE = ("服务", "Depend")

    def __init__(self, zh_label, category):
        self.zh_label = zh_label
        self.category = category

    def __str__(self):
        return self.zh_label

class ServiceType(Enum):
    """服务类型枚举类"""
    OPERATION = "作业"
    SERVICE = "服务"

class FormType(Enum):
    """表单类型枚举类"""
    PRODUCE = "服务作业"
    Document = "文档"

class DomainObject(Enum):
    """领域对象枚举类"""
    ENTITY_CLASS = "实体类"
    ENTITY_INSTANCE = "实体实例"
    SERVICE = "服务"
    OPERATION = "作业"
    STATUS = "状态"
    EVENT = "事件"
    INSTRUCTION = "指令"
    WORKPIECE = "工件"
    ATTRIBUTE = "属性"
    RESOURCE = "资源"
    CONTRACT = "合约"
    SYSTEM_OBJECT = "系统对象"
    SYSTEM_SERVICE = "系统服务"
    LABEL = "标签"
    CONCEPT = "概念"
    ELEMENT = "元素"