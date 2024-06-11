"""
1. 业务对象描述
2. 业务过程描述
3. 初始数据(initial_data.xlsx, Forms)

# Vocabulary
Organization
Customer
Contract

Service
- Operation
Process
Status
WorkOrder
Workpiece
Metrics
Event
Rule

Form
Field

Resource
- Staff
- Equipment
- Material
- Capital
- Knowledge

Guide
Instruction
Tutorial
Document
Sample

Schedule
Dashboard

Role
Membership
Account(充值记录，消费记录)
ServiceType(["光电类", "护肤品类", "化学焕肤", "手术类", "仪器类", "注射填充类"])
TreatmentRecord
InformedConsent
Precautions
Bill

LaborHours = GenerateTimeSlot([Staff], Calendar, {'Work-hourUnit': config})
EquipmentHours = GenerateTimeSlot([Equipment], Calendar, {'Work-hourUnit': config})

[('超声炮', 'EQUIPMENT'), ('肉毒素注射', 'KNOWLEDGE'), ('超声软组织理疗', 'KNOWLEDGE'), ('Q开关激光', 'KNOWLEDGE'), ('保妥适100单位', 'MATERIAL'), ('超声炮刀头', 'MATERIAL'), ('超声炮炮头', 'MATERIAL'), ('乔雅登极致0.8ml', 'MATERIAL'), ('医生', 'OPERATOR'), ('护士', 'OPERATOR'), ('客服', 'OPERATOR'), ('治疗', 'SKILL'), ('随访', 'SKILL'), ('预约', 'SKILL'), ('备料', 'SKILL')]

# CPU -> 总线 -> 内存、I/O设备...
# 总线提供I/O设备的虚拟化，负责注册、转发
# PCIE总线自带中断控制器
# PCIE总线 -> USB总线 -> USB设备

# 设备驱动程序除了读写, 还要处理配置, 非数据的设备功能依赖ioctl

# Linux命令 taskset => 把进程和特定的CPU绑定在一起
# 公平分享CPU资源 Round-Robin
# 医生每位患者面诊15分钟，是一种轮转调度算法
# 动态优先级调度算法 MLFQ(Multi-Level Feedback Queue)
# Linux调度算法 CFS(Completely Fair Scheduler)
# 调度参数：nice值，优先级（权重？），实时性，时间片大小，调度策略
# 不同岗位的操作员 => 异构处理器

Operating System Services Provide:
1. User Interface: CLI, GUI
2. Program Execution: Source code -> Compiler -> Object code -> Executor
3. I/O Operations
4. File System Manipulation
5. Communications: Inter-process communication, Networking
6. Error Detection: Hardware, Software
7. Resource Allocation: CPU, Memory, I/O devices
8. Accounting: Usage statistics, Billing information -- Which users use how much and what kinds of resources
9. Protection and Security: User authentication, File permissions, Encryption

Types of System Calls
1. Process Control
2. File Manipulation
3. Device Management
4. Information Maintenance
5. Communications

Types of System Programs
1. File Management
2. Status Information
3. File Modification
4. Programming Language Support
5. Program Loading and Execution
6. Communications

syscalls[num]():
SYS_fork
SYS_exit
SYS_wait
SYS_pipe
SYS_read
SYS_kill
SYS_exec
SYS_fstat
SYS_chdir
SYS_dup
SYS_getpid
SYS_sbrk
SYS_sleep
SYS_uptime
SYS_open
SYS_write
SYS_mknod
SYS_unlink
SYS_link
SYS_mkdir
SYS_close
"""

"""
业务表单

form数据结构说明
1. 顶层结构
    •	类型: form
    •	标签: label
    •	条目: entries（列表）
2. 条目结构
    •	类型: group 或 field
    •	标签: label
    •	条目: entries（仅适用于 group 类型）
3. 字段结构
    •	字段类型: field_type
    •	String
    •	String可能有enum值（仅适用于String类型）
    •	Date
    •	Boolean
    •	Integer
    •	Decimal
    •	Text
4. 嵌套结构
    •	group 类型条目可以包含其他 group 和 field 类型的条目
    •	field 类型条目只能包含字段相关信息

从FORMS中导入数据的业务逻辑(至 Field, Dictionary, DictionaryFields)
1. 遍历FORMS的所有form
2. 遍历form的所有entries里的所有条目
3. 如果条目的type是field且没有enum, 且Field中没有label名相同的对象, 则创建新Field对象, 使用条目的label作为新Field对象的label, field_type作为field_type;
4. 如果条目的type是field且有enum, 且Field中没有label名为label名+"名称"的对象, 则执行以下2个步骤: 
    step-1 创建Dictionary对象, 使用条目的label做为该Dictionary对象的label, 获取或创建Field对象“值”加入到该Dictionary对象的多对多字段fields字段的值中, 将enum的值写入JSONField字段content中;
    step-2 创建Field对象, 使用条目的label做为该Field对象的label, 该Field对象的field_type为'DictionaryField', 该Field对象的related_dictionary为step-2创建的Dictionary对象;
5. field_type -> Field.field_type 映射关系：
    •	String -> CharField
    •	Date -> DateField
    •	Boolean -> BooleanField
    •	Integer -> IntegerField
    •	Decimal -> DecimalField
    •	Text    -> TextField

"""

from enum import Enum, auto

class SystemCall(Enum):
    """系统调用枚举类"""
    CreateService = auto()
    CallService = auto()

    def __str__(self):
        return self.name

class Scheduler:
    def __init__(self):
        self.job_handlers = {
            SystemCall.CreateService: self.create_service,
            SystemCall.CallService: self.call_service,
        }

    def schedule(self, sys_call, **kwargs):
        handler = self.job_handlers.get(sys_call)
        if handler:
            return handler(**kwargs)
        else:
            raise ValueError(f"Unhandled job type: {sys_call}")

    # Define job functions
    def create_service(self, **kwargs):
        print("Creating service...")
        # Actual implementation here

    def call_service(self, **kwargs):
        print("Call service...")
        # Actual implementation here

GLOBAL_INITIAL_STATES = {
    # 系统对象
    'SystemObject': [
        ('User', '系统用户'), 
        ('DateTime', '系统时间'),
        ('Timer', '系统计时器'),
        ('MATERIAL','物料'),
        ('EQUIPMENT','设备'),
        ('DEVICE','工具'),
        ('OPERATOR','人员'),
        ('SPACE','空间'),
        ('CAPITAL','资金'),
        ('KNOWLEDGE','知识'),
        ('Service', '服务'),
        (SystemCall.CreateService, '创建服务'),
        (SystemCall.CallService, '调用服务'),
    ],

    # 资源分类
    'SystemResourceType': {
        "Material": {
            "quantity": "int",
            "unit": "string",
            "supplier": "string"
        },
        "Device": {
            "serial_number": "string",
            "status": "string",
            "purchase_date": "date"
        },
        "Equipment": {
            "type": "string",
            "maintenance_cycle": "int",
            "last_maintenance_date": "date"
        },
        "Operator": {
            "role": "string",
            "skill_level": "string",
            "hire_date": "date"
        },
        "Capital": {
            "amount": "float",
            "type": "string",
            "source": "string"
        },
        "Knowledge": {
            "subject": "string",
            "description": "string",
            "importance_level": "string"
        }
    },

    # 全局业务常量
    'Organization': '广州颜青医疗美容诊所',
    
    # 业务表单
    'Forms': [
        {
            "type": "form",
            "label": "基本信息调查",
            "entries": [
                {
                    "type": "group",
                    "label": "您的基本信息",
                    "entries": [
                        {
                            "type": "field",
                            "label": "姓名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "性别",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "出生日期",
                            "field_type": "Date"
                        },
                        {
                            "type": "field",
                            "label": "婚否",
                            "field_type": "String",
                            "enum": [
                                "已婚",
                                "未婚"
                            ]
                        },
                        {
                            "type": "field",
                            "label": "电话",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "常住区域",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "职业",
                            "field_type": "String",
                            "enum": [
                                "公务员",
                                "自由职业",
                                "企业管理人员",
                                "企业主",
                                "职员",
                                "医生",
                                "教师",
                                "律师",
                                "媒体人",
                                "其他"
                            ]
                        },
                        {
                            "type": "field",
                            "label": "来源",
                            "field_type": "String",
                            "enum": [
                                "微信公众号",
                                "网络",
                                "介绍",
                                "广告",
                                "其他"
                            ]
                        },
                        {
                            "type": "field",
                            "label": "初诊日期",
                            "field_type": "Date"
                        }
                    ]
                },{
                    "type": "group",
                    "label": "您的身体情况及既往史",
                    "entries": [
                        {
                            "type": "group",
                            "label": "1、是否有以下过敏？",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "过敏史",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "化妆/护肤品",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "药品",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "酒精",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "花粉",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "果酸",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "动物",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "香料",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "光敏感",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "牛奶/鸡蛋/海鲜",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "其他",
                                    "field_type": "String"
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "2、是否患有或曾经患有下述，但不限于下述的任何疾病？",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "高血压",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "糖尿病",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "心脏病",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "免疫性疾病",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "血液疾病",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "良恶性肿瘤",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "精神或心理",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "荨麻疹",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "神经系统疾患",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "任何传染性疾患",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "其他",
                                    "field_type": "String"
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "3、近6个月是否有以下情况？",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "失眠",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "焦虑",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "抑郁",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "曾经看过心理医生或就诊过精神科室",
                                    "field_type": "Boolean"
                                }
                            ]                
                        },{
                            "type": "field",
                            "label": "4、体内是否有任何植入物？如心脏起搏器等。",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "5、是否有疤痕体质？",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "6、是否属于高敏体质？",
                            "field_type": "Boolean"
                        },{
                            "type": "group",
                            "label": "7、是否怀孕或哺乳期？",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "怀孕或哺乳期",
                                    "field_type": "Boolean"
                                },
                                {
                                    "type": "field",
                                    "label": "未次月经时间",
                                    "field_type": "Date"
                                }
                            ]
                        },{
                            "type": "field",
                            "label": "8、是否备孕期？",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "9、近3个月内是否有用药品、保健品吗？",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "10、近3年内是否接受过手术或任何非手术医学美容治疗？",
                            "field_type": "Boolean"
                        }
                    ]
                },{
                    "type": "group",
                    "label": "您目前最想改善的问题",
                    "entries": [
                        {
                            "type": "field",
                            "label": "敏纹",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "色素",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "痤疮",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "痘印痘疤",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "暗黄",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "毛孔",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "敏感",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "轮廓",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "眼部",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "颈部",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "手足",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "纹绣",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "毛发",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "调理",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "体重",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "身材",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "妊娠纹",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "瘦肩",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "瘦小腿",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "瘦手臂",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "其他",
                            "field_type": "String"
                        }
                    ]
                }
            ]
        },
        {
            "type": "form",
            "label": "专科评估",
            "entries": [
                {
                    "type": "group",
                    "label": "皮肤基本情况",
                    "entries": [
                        {
                            "type": "field",
                            "label": "干性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "油性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "耐受性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "敏感性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "色素沉着性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "非色素沉着性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "松弛性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "紧致性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "皱纹性",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "下垂",
                            "field_type": "Boolean"
                        },
                        {
                            "type": "field",
                            "label": "其他",
                            "field_type": "String"
                        }
                    ]
                },{
                    "type": "group",
                    "label": "皮肤详细状况",
                    "entries": [
                        {
                            "type": "group",
                            "label": "肤色与光泽",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "部位",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "肤色",
                                    "field_type": "String",
                                    "enum": [
                                        "白皙",
                                        "中等",
                                        "萎黄",
                                        "暗黑"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "均匀度",
                                    "field_type": "String",
                                    "enum": [
                                        "均匀",
                                        "中等",
                                        "不匀"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "光泽度",
                                    "field_type": "String",
                                    "enum": [
                                        "明亮",
                                        "中等",
                                        "暗哑"
                                    ]
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "肤质及弹性",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "部位",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "弹性度",
                                    "field_type": "String",
                                    "enum": [
                                        "Q弹",
                                        "一般",
                                        "较松软",
                                        "松软"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "光滑度",
                                    "field_type": "String",
                                    "enum": [
                                        "光滑",
                                        "较光滑",
                                        "中等",
                                        "较粗糙",
                                        "粗糙"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "毛孔",
                                    "field_type": "String",
                                    "enum": [
                                        "细腻",
                                        "较细腻",
                                        "中等",
                                        "较粗大",
                                        "粗大"
                                    ]
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "皱纹与轮廓",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "部位",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "皱纹",
                                    "field_type": "String",
                                    "enum": [
                                        "静态纹",
                                        "动态纹",
                                        "静态+动态纹"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "大轮廓",
                                    "field_type": "String",
                                    "enum": [
                                        "下颌缘模糊",
                                        "双下巴",
                                        "太阳穴凹陷",
                                        "苹果肌移位",
                                        "侧颜线条不流畅",
                                        "咬肌肥大",
                                        "颊凹"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "小轮廓",
                                    "field_type": "String",
                                    "enum": [
                                        "印第安纹",
                                        "法令纹",
                                        "木偶纹",
                                        "泪沟",
                                        "眼袋"
                                    ]
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "色素问题",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "部位",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "种类",
                                    "field_type": "String",
                                    "enum": [
                                        "多种",
                                        "三种",
                                        "两种",
                                        "一种"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "颜色",
                                    "field_type": "String",
                                    "enum": [
                                        "棕褐色",
                                        "棕黄色",
                                        "青褐色",
                                        "浅黑色",
                                        "浅黄色"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "并皮下炎症",
                                    "field_type": "String",
                                    "enum": [
                                        "无",
                                        "轻度",
                                        "中度",
                                        "重度"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "形态",
                                    "field_type": "String",
                                    "enum": [
                                        "散在点状",
                                        "簇集点状",
                                        "点片状",
                                        "小片状"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "大片状",
                                    "field_type": "String",
                                    "enum": [
                                        "边界清晰",
                                        "模糊"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "色斑活跃度",
                                    "field_type": "String",
                                    "enum": [
                                        "活跃",
                                        "静止",
                                        "退行"
                                    ]
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "血管性问题",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "部位",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "颜色",
                                    "field_type": "String",
                                    "enum": [
                                        "黄黑",
                                        "黑红",
                                        "紫红",
                                        "红色",
                                        "鲜红",
                                        "粉红"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "形态",
                                    "field_type": "String",
                                    "enum": [
                                        "迂曲扩张",
                                        "均与片状",
                                        "弥漫潮红"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "边界",
                                    "field_type": "String",
                                    "enum": [
                                        "清晰",
                                        "模糊"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "增生情况",
                                    "field_type": "String",
                                    "enum": [
                                        "平滑无增生",
                                        "增生突出表皮",
                                        "角质化"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "玻片实验",
                                    "field_type": "String",
                                    "enum": [
                                        "不褪色",
                                        "部分褪色",
                                        "完全褪色"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "充盈速度",
                                    "field_type": "String",
                                    "enum": [
                                        "快",
                                        "中等",
                                        "慢"
                                    ]
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "痤疮及痘痕",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "部位",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "皮疹种类",
                                    "field_type": "String",
                                    "enum": [
                                        "白头粉刺",
                                        "黑头粉刺",
                                        "炎性丘疹",
                                        "脓疱",
                                        "结节",
                                        "囊肿",
                                        "疤痕"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "临床分级",
                                    "field_type": "String",
                                    "enum": [
                                        "I轻度",
                                        "II中度",
                                        "III中度",
                                        "IV重度"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "痘印颜色",
                                    "field_type": "String",
                                    "enum": [
                                        "鲜红色",
                                        "暗红色",
                                        "红褐色",
                                        "浅褐色",
                                        "深褐色"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "痘坑类型",
                                    "field_type": "String",
                                    "enum": [
                                        "冰锥样",
                                        "厢车样",
                                        "滚石样-密",
                                        "滚石样-疏"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "增生性疤痕",
                                    "field_type": "String",
                                    "enum": [
                                        "有",
                                        "无"
                                    ]
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "毛发问题",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "部位",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "密度",
                                    "field_type": "String",
                                    "enum": [
                                        "过密",
                                        "中等",
                                        "稀疏"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "质地",
                                    "field_type": "String",
                                    "enum": [
                                        "毛糙",
                                        "中等",
                                        "光滑"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "韧度",
                                    "field_type": "String",
                                    "enum": [
                                        "脆弱",
                                        "中等",
                                        "强韧"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "光泽",
                                    "field_type": "String",
                                    "enum": [
                                        "佳",
                                        "中等",
                                        "不佳"
                                    ]
                                }
                            ]
                        },{
                            "type": "group",
                            "label": "问题部位的皮肤情况",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "油脂",
                                    "field_type": "String",
                                    "enum": [
                                        "旺盛",
                                        "中等",
                                        "干燥"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "脱屑",
                                    "field_type": "String",
                                    "enum": [
                                        "无",
                                        "少",
                                        "多"
                                    ]
                                },
                                {
                                    "type": "field",
                                    "label": "炎症",
                                    "field_type": "String",
                                    "enum": [
                                        "无",
                                        "轻度",
                                        "中度",
                                        "重度"
                                    ]
                                }
                            ]
                        }
                    ]
                },{
                    "type": "field",
                    "label": "其他问题评估",
                    "field_type": "String",
                },{
                    "type": "field",
                    "label": "客户姓名",
                    "field_type": "String",
                },{
                    "type": "field",
                    "label": "医生姓名", 
                    "field_type": "String",
                } 
            ]
        },    
        {
            "type": "form",
            "label": "广州颜青医疗问诊记录单",
            "entries": [
                {
                    "type": "field",
                    "label": "日期",
                    "field_type": "Date"
                },
                {
                    "type": "group",
                    "label": "基本信息",
                    "entries": [
                        {
                            "type": "field",
                            "label": "姓名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "性别",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "出生年月",
                            "field_type": "Date"
                        },
                        {
                            "type": "field",
                            "label": "年龄",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "居住地 (省、市)",
                            "field_type": "String"
                        }
                    ]
                },
                {
                    "type": "field",
                    "label": "药物过敏史",
                    "field_type": "String"
                },
                {
                    "type": "field",
                    "label": "是否怀孕",
                    "field_type": "Boolean"
                },
                {
                    "type": "field",
                    "label": "孕期",
                    "field_type": "Integer"
                },
                {
                    "type": "field",
                    "label": "是否经期",
                    "field_type": "Boolean"
                },
                {
                    "type": "field",
                    "label": "是否哺乳期",
                    "field_type": "Boolean"
                },
                {
                    "type": "group",
                    "label": "主诉",
                    "entries": [
                        {
                            "type": "field",
                            "label": "主诉",
                            "field_type": "Text"
                        }
                    ]
                },
                {
                    "type": "group",
                    "label": "治疗意见",
                    "entries": [
                        {
                            "type": "field",
                            "label": "治疗意见",
                            "field_type": "Text"
                        }
                    ]
                }
            ]
        },
        {
            "type": "form",
            "label": "CC光治疗记录单",
            "entries": [
                {
                    "type": "group",
                    "label": "患者信息",
                    "entries": [
                        {
                            "type": "field",
                            "label": "姓名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "病案号",
                            "field_type": "String"
                        }
                    ]
                },
                {
                    "type": "group",
                    "label": "治疗记录",
                    "entries": [
                        {
                            "type": "field",
                            "label": "日期",
                            "field_type": "Date"
                        },
                        {
                            "type": "field",
                            "label": "波段 (nm)",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "能量密度 (J/CM2)",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "脉宽 (ms)",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "冷却温度 (°C)",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "终点反应",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "患者签名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "操作人签名",
                            "field_type": "String"
                        }
                    ]
                }
            ]
        },
        {
            "type": "form",
            "label": "肉毒素注射治疗记录表",
            "entries": [
                {
                    "type": "group",
                    "label": "患者信息",
                    "entries": [
                        {
                            "type": "field",
                            "label": "姓名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "病历号",
                            "field_type": "String"
                        }
                    ]
                },
                {
                    "type": "group",
                    "label": "治疗记录",
                    "entries": [
                        {
                            "type": "group",
                            "label": "治疗详情",
                            "entries": [
                                {
                                    "type": "field",
                                    "label": "日期",
                                    "field_type": "Date"
                                },
                                {
                                    "type": "field",
                                    "label": "次数",
                                    "field_type": "Integer"
                                },
                                {
                                    "type": "field",
                                    "label": "图例",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "手术医生",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "患者知情同意签字",
                                    "field_type": "String"
                                },
                                {
                                    "type": "field",
                                    "label": "随访记录",
                                    "field_type": "Text"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "type": "form",
            "label": "调Q治疗参数记录单",
            "entries": [
                {
                    "type": "group",
                    "label": "患者信息",
                    "entries": [
                        {
                            "type": "field",
                            "label": "姓名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "病案号",
                            "field_type": "String"
                        }
                    ]
                },
                {
                    "type": "group",
                    "label": "治疗参数记录",
                    "entries": [
                        {
                            "type": "field",
                            "label": "日期",
                            "field_type": "Date"
                        },
                        {
                            "type": "field",
                            "label": "波段",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "频率",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "能量",
                            "field_type": "Decimal"
                        },
                        {
                            "type": "field",
                            "label": "光斑",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "终点反应",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "患者签名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "操作人签名",
                            "field_type": "String"
                        }
                    ]
                }
            ]
        },
        {
            "type": "form",
            "label": "酸类治疗记录",
            "entries": [
                {
                    "type": "group",
                    "label": "患者信息",
                    "entries": [
                        {
                            "type": "field",
                            "label": "姓名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "性别",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "年龄",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "病历号",
                            "field_type": "String"
                        }
                    ]
                },
                {
                    "type": "group",
                    "label": "治疗记录",
                    "entries": [
                        {
                            "type": "field",
                            "label": "治疗次数",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "治疗日期",
                            "field_type": "Date"
                        },
                        {
                            "type": "field",
                            "label": "酸浓度",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "停留时间",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "红斑程度 (0-3分)",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "刺痛发痒 (0-9分)",
                            "field_type": "Integer"
                        },
                        {
                            "type": "field",
                            "label": "发白结霜 (0-3分)",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "其他",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "患者签名",
                            "field_type": "String"
                        },
                        {
                            "type": "field",
                            "label": "操作签名",
                            "field_type": "String"
                        }
                    ]
                }
            ]
        },
    ]
}
