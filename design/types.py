from enum import Enum

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
