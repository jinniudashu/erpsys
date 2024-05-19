# Global Object
import json

from django.db.utils import IntegrityError
from design.models import Field, Dictionary, DictionaryFields

import pandas as pd

# 读取 Excel 文件
def read_excel(file_path: str, sheet_name: str,) -> pd.DataFrame:
    df = pd.read_excel(file_path, engine="openpyxl")
    # 显示 DataFrame 的前几行数据
    print(df.head())
    return df

"""
1. 业务对象结构
2. 业务过程描述
3. 初始数据引用(csv文件)
"""
# 全局业务常量
ORGANIZATION = "广州颜青医疗美容诊所"


"""
form数据结构规范
顶层结构
	•	类型: form
	•	标签: label
	•	条目: entries（列表）
条目结构
	•	类型: group 或 field
	•	标签: label
	•	条目: entries（仅适用于 group 类型）
字段结构
	•	字段类型: field_type
	•	String
	•	String可能有enum值（仅适用于String类型）
	•	Date
	•	Boolean
    •	Integer
    •	Decimal
    •	Text
嵌套结构
	•	group 类型条目可以包含其他 group 和 field 类型的条目
	•	field 类型条目只能包含字段相关信息

从FORMS中导入数据的业务逻辑(至 Field, Dictionary, DictionaryFields)
1. 遍历FORMS的所有form
2. 遍历form的所有entries里的所有条目
3. 如果条目的type是field且没有enum, 且Field中没有label名相同的对象, 则创建新Field对象, 使用条目的label作为新Field对象的label, field_type作为field_type;
4. 如果条目的type是field且有enum, 且Field中没有label名为label名+"名称"的对象, 则执行以下3个步骤: 
    step-1 获取或创建Field对象“值”;
    step-2 创建Dictionary对象, 使用条目的label做为该Dictionary对象的label, 将step-1获取的Field对象“值”加入到该Dictionary对象的多对多字段fields字段的值中, 将enum的值写入JSONField字段content中;
    step-3 创建Field对象, 使用条目的label做为该Field对象的label, 该Field对象的field_type为'DictionaryField', 该Field对象的related_dictionary为step-2创建的Dictionary对象;
5. field_type -> Field.field_type 映射关系：
	•	String -> CharField
	•	Date -> DateField
	•	Boolean -> BooleanField
    •	Integer -> IntegerField
    •	Decimal -> DecimalField
    •	Text    -> TextField

"""
FORMS = [
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

def abstract_forms_data(forms):
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
                    """
                        step-1 获取或创建Field对象“值”;
                        step-2 创建Dictionary对象, 使用条目的label做为该Dictionary对象的label, 将step-1获取的Field对象“值”加入到该Dictionary对象的多对多字段fields字段的值中, 将enum的值写入JSONField字段content中;
                        step-3 创建Field对象, 使用条目的label做为该Field对象的label, 该Field对象的field_type为'DictionaryField', 该Field对象的related_dictionary为step-2创建的Dictionary对象;
                    """
                    field = Field.objects.get_or_create(label='值', defaults={'field_type': field_type})[0]
                    dictionary, created = Dictionary.objects.get_or_create(label=label)
                    if created:
                        dictionary.fields.add(field)
                        dictionary.content = json.dumps(enum, ensure_ascii=False)
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

def abstract_excel_data(file_path):
    pass

# abstract_excel_data("design/business_data/initial_data.xlsx")

# Vocabulary
"""
Organization
Staff
Customer
Contract
Device
Material
Capital
Knowledge

Service
Operation
Process
Status
WorkOrder
Workpiece
Metrics
Event
Rule
Field
Form

Resource
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

LaborHours
EquipmentHours
Work-hourUnit
"""
