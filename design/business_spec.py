# Global Object

"""
1. 业务对象结构
2. 业务过程描述
3. 初始数据引用(csv文件)
"""
# 全局业务常量
ORGANIZATION = {
    "name": "",
    "roles": {"type": "String", "enum": ["医生", "护士", "客服", "管理员"]},
    "staff": {"type": "List", "items": {
        "name": {},
        "roles": {}
    }}
}


# 工件定义
WORKPIECE = [
    {
        "name": "基本信息",
        "body": {
            "您的基本信息": {
                "姓名": {"type": "String"},
                "性别": {"type": "String"},
                "出生日期": {"type": "Date"},
                "婚否": {"type": "String", "enum": ["已婚", "未婚"]},
                "电话": {"type": "String"},
                "常住区域": {"type": "String"},
                "职业": {"type": "String", "enum": ["公务员", "自由职业", "企业管理人员", "企业主", "职员", "医生", "教师", "律师", "媒体人", "其他"]},
                "来源": {"type": "String", "enum": ["微信公众号", "网络", "介绍", "广告", "其他"]},
                "初诊日期": {"type": "Date"}
            },
            "您的身体情况及既往史": {
                "1、是否有以下过敏？": {
                    "过敏史": {"type": "Boolean"},
                    "化妆/护肤品": {"type": "Boolean"},
                    "药品": {"type": "Boolean"},
                    "酒精": {"type": "Boolean"},
                    "花粉": {"type": "Boolean"},
                    "果酸": {"type": "Boolean"},
                    "动物": {"type": "Boolean"},
                    "香料": {"type": "Boolean"},
                    "光敏感": {"type": "Boolean"},
                    "牛奶/鸡蛋/海鲜": {"type": "Boolean"},
                    "其他": {"type": "String"}
                },
                "2、是否患有或曾经患有下述，但不限于下述的任何疾病？": {
                    "高血压": {"type": "Boolean"},
                    "糖尿病": {"type": "Boolean"},
                    "心脏病": {"type": "Boolean"},
                    "免疫性疾病": {"type": "Boolean"},
                    "血液疾病": {"type": "Boolean"},
                    "良恶性肿瘤": {"type": "Boolean"},
                    "精神或心理": {"type": "Boolean"},
                    "荨麻疹": {"type": "Boolean"},
                    "神经系统疾患": {"type": "Boolean"},
                    "任何传染性疾患": {"type": "Boolean"},
                    "其他": {"type": "String"}
                },
                "3、近6个月是否有失眠、焦虑、抑郁等情况？是否曾经看过心理医生或就诊过精神科室？": {"type": "Boolean"},
                "4、体内是否有任何植入物？如心脏起搏器等。": {"type": "Boolean"},
                "5、是否有疤痕体质？": {"type": "Boolean"},
                "6、是否属于高敏体质？": {"type": "Boolean"},
                "7、是否怀孕或哺乳期？": {
                    "": {"type": "Boolean"},
                    "未次月经时间：": {"type": "Date"},
                },
                "8、是否备孕期？": {"type": "Boolean"},
                "9、近3个月内是否有用药品、保健品吗？": {"type": "Boolean"},
                "10、近3年内是否接受过手术或任何非手术医学美容治疗？": {"type": "Boolean"},
            },
            "您目前最想改善的问题": {
                "敏纹": {"type": "Boolean"},
                "色素": {"type": "Boolean"},
                "痤疮": {"type": "Boolean"},
                "痘印痘疤": {"type": "Boolean"},
                "暗黄": {"type": "Boolean"},
                "毛孔": {"type": "Boolean"},
                "敏感": {"type": "Boolean"},
                "轮廓": {"type": "Boolean"},
                "眼部": {"type": "Boolean"},
                "颈部": {"type": "Boolean"},
                "手足": {"type": "Boolean"},
                "纹绣": {"type": "Boolean"},
                "毛发": {"type": "Boolean"},
                "调理": {"type": "Boolean"},
                "体重": {"type": "Boolean"},
                "身材": {"type": "Boolean"},
                "妊娠纹": {"type": "Boolean"},
                "瘦肩": {"type": "Boolean"},
                "瘦小腿": {"type": "Boolean"},
                "瘦手臂": {"type": "Boolean"},
                "其他": {"type": "String"}
            },           
        },
    },
    {
        "name": "专科评估",
        "body": {
            "皮肤基本情况": {
                "干性": {
                    "type": "Boolean",
                },
                "油性": {
                    "type": "Boolean",
                },
                "耐受性": {
                    "type": "Boolean",
                },
                "敏感性": {
                    "type": "Boolean",
                },
                "色素沉着性": {
                    "type": "Boolean",
                },
                "非色素沉着性": {
                    "type": "Boolean",
                },
                "松弛性": {
                    "type": "Boolean",
                },
                "紧致性": {
                    "type": "Boolean",
                },
                "皱纹性": {
                    "type": "Boolean",
                },
                "下垂": {
                    "type": "Boolean",
                },
                "其他": {
                    "type": "String",
                }                
            },
            "皮肤详细状况": {
                "肤色与光泽": {
                    "部位": {
                        "type": "String",
                    },
                    "肤色": {
                        "type": "String",
                        "enum": [
                            "白皙",
                            "中等",
                            "萎黄",
                            "暗黑",
                        ],
                    },
                    "均匀度": {
                        "type": "String",
                        "enum": [
                            "均匀",
                            "中等",
                            "不匀",
                        ],
                    },
                    "光泽度": {
                        "type": "String",
                        "enum": [
                            "明亮",
                            "中等",
                            "暗哑",
                        ],
                    },
                },
                "肤质及弹性": {
                    "部位": {
                        "type": "String",
                    },
                    "弹性度": {
                        "type": "String",
                        "enum": ["Q弹", "一般", "较松软", "松软", ],
                    },
                    "光滑度": {
                        "type": "String",
                        "enum": ["光滑","较光滑","中等","较粗糙","粗糙", ],
                    },
                    "毛孔": {
                        "type": "String",
                        "enum": ["细腻","较细腻","中等","较粗大","粗大", ],
                    },
                },
                "皱纹与轮廓": {
                    "部位": {
                        "type": "String",
                    },
                    "皱纹": {
                        "type": "String",
                        "enum": ["静态纹","动态纹","静态+动态纹", ],
                    },
                    "大轮廓": {
                        "type": "String",
                        "enum": ["下颌缘模糊","双下巴","太阳穴凹陷","苹果肌移位","侧颜线条不流畅","咬肌肥大","颊凹", ],
                    },
                    "小轮廓": {
                        "type": "String",
                        "enum": ["印第安纹","法令纹","木偶纹","泪沟","眼袋", ],
                    },
                },
                "色素问题": {
                    "部位": {
                        "type": "String",
                    },
                    "种类": {
                        "type": "String",
                        "enum": ["多种","三种","两种","一种", ],
                    },
                    "颜色": {
                        "type": "String",
                        "enum": ["棕褐色","棕黄色", "青褐色", "浅黑色", "浅黄色", ],
                    },
                    "并皮下炎症": {
                        "type": "String",
                        "enum": ["无","轻度", "中度","重度", ],
                    },
                    "形态": {"type": "String", "enum": ["散在点状", "簇集点状", "点片状", "小片状"]},
                    "大片状": {"type": "String", "enum": ["边界清晰", "模糊"]},
                    "色斑活跃度": {"type": "String", "enum": ["活跃", "静止", "退行"]}
                },
                "血管性问题": {
                    "部位": {"type": "String"},
                    "颜色": {"type": "String", "enum": ["黄黑", "黑红", "紫红", "红色", "鲜红", "粉红"]},
                    "形态": {"type": "String", "enum": ["迂曲扩张", "均与片状", "弥漫潮红"]},
                    "边界": {"type": "String", "enum": ["清晰", "模糊"]},
                    "增生情况": {"type": "String", "enum": ["平滑无增生", "增生突出表皮", "角质化"]},
                    "玻片实验": {"type": "String", "enum": ["不褪色", "部分褪色", "完全褪色"]},
                    "充盈速度": {"type": "String", "enum": ["快", "中等", "慢"]}
                },
                "痤疮及痘痕": {
                    "部位": {"type": "String"},
                    "皮疹种类": {"type": "String", "enum": ["白头粉刺", "黑头粉刺", "炎性丘疹", "脓疱", "结节", "囊肿", "疤痕"]},
                    "临床分级": {"type": "String", "enum": ["I轻度", "II中度", "III中度", "IV重度"]},
                    "痘印颜色": {"type": "String", "enum": ["鲜红色", "暗红色", "红褐色", "浅褐色", "深褐色"]},
                    "痘坑类型": {"type": "String", "enum": ["冰锥样", "厢车样", {"滚石样": {"type": "String", "enum": ["密", "疏"]}}]},
                    "增生性疤痕": {"type": "String", "enum": ["有", "无"]},
                },
                "毛发问题": {
                    "部位": {"type": "String"},
                    "密度": {"type": "String", "enum": ["过密", "中等", "稀疏"]},
                    "质地": {"type": "String", "enum": ["毛糙", "中等", "光滑"]},
                    "韧度": {"type": "String", "enum": ["脆弱", "中等", "强韧"]},
                    "光泽": {"type": "String", "enum": ["佳", "中等", "不佳"]},
                },
                "问题部位的皮肤情况": {
                    "油脂": {"type": "String", "enum": ["旺盛", "中等", "干燥"]},
                    "脱屑": {"type": "String", "enum": ["无", "少", "多"]},
                    "炎症": {"type": "String", "enum": ["无", "轻度", "中度", "重度"]},
                }
            },
            "其他问题评估": {
                "type": "String",
            },
            "客户姓名": {
                "type": "String",
            },
            "医生姓名": {
                "type": "String",
            },    
        },
    },
]
