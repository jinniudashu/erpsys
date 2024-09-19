from enum import Enum

FieldType = [
    ('CharField', '单行文本'),
    ('IntegerField', '整数'),
    ('TypeField', '类型'),
    ('BooleanField', '是否'),
    ('User', '系统用户'),
    ('Reserved', '系统保留'),
    ('DecimalField', '固定精度小数'),
    ('TextField', '多行文本'),
    ('DateTimeField', '日期时间'),
    ('DateField', '日期'),
    ('TimeField', '时间'),
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

SystemObject = [
    ('User', '系统用户'), 
    ('DateTime', '系统时间'),
    ('Timer', '系统计时器'),
    ('Service', '服务'),
    ('CreateService', '创建服务'),
    ('CallService', '调用服务'),
]

ImplementType = [
    ('Field', '字段'),
    ('Model', '数据表'),
    ('View', '视图'),
    ('MenuItem', '菜单项'),
    ('KernelModel', '系统表'),
    ('Program', '程序'),
]

ResourceType = [
    ('Consumption', '消耗'),
    ('TDM', '分时复用'),
    ('Recycle', '回收'),
    ('Shared', '共享'),
]

class SystemResourceType(Enum):
    """资源类型枚举类"""
    MATERIAL = ("物料", "Consumption")
    EQUIPMENT = ("设备", "TDM")
    DEVICE = ("工具", "Recycle")
    OPERATOR = ("人员", "TDM")
    SPACE = ("空间", "TDM")
    CAPITAL = ("资金", "Consumption")
    KNOWLEDGE = ('知识', "Shared")
    INFORMATION = ("信息", "Shared")
    SERVICE = ("服务", "Depend")

    def __init__(self, zh_label, category):
        self.zh_label = zh_label
        self.category = category

    def __str__(self):
        return self.zh_label

class ServiceType(Enum):
    """服务类型枚举类"""
    USER = "用户"
    SYSTEM = "系统"

class FormType(Enum):
    """表单类型枚举类"""
    PRODUCE = "服务作业"
    DOCUMENT = "文档"

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
