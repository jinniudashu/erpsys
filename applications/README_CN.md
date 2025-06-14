# 应用层

**应用层**代表了通过设计层配置的业务领域模型的最终实例化。该目录包含从DataItem元定义自动生成的具体业务实体，专门针对医美行业领域进行配置。

## 目的

该层展示了元框架如何将抽象的业务定义转换为可操作的Django模型，具有以下特性：
- 自动中文语言支持和拼音生成
- 通过外键关系进行流程集成
- 所有模型的标准化字段模式
- 从内核组件继承业务逻辑

## 领域实现：医美诊所

### 字典模型 (Dict-*)
医疗操作的核心参考数据：
- **服务类别** (FuWuLeiBie) - 服务分类
- **入出库操作** (RuChuKuCaoZuo) - 库存操作
- **客户来源** (KeHuLaiYuan) - 客户来源
- **症状/诊断** (ZhengZhuang/ZhenDuan) - 症状和诊断
- **收费类型** (ShouFeiLeiXing) - 计费类型

### 资源模型
来自设计层的资源抽象：
- **Material** - 带库存跟踪的医疗用品
- **Equipment/Device** - 医疗设备和工具
- **Capital** - 财务资源
- **Knowledge** - 带文件/文本存储的医疗知识库

### 操作模型
业务流程实现：
- **Profile** - 患者人口统计和医疗记录
- **YuYueJiLu** - 带服务集成的预约调度
- **WuLiaoTaiZhang** - 带有效期跟踪的物料台账
- **ZhiLiaoXiangMu** - 各种治疗程序的记录

### 治疗记录
医美项目的专门模型：
- **RouDuSuZhiLiaoJiLu** - 肉毒素治疗记录
- **ChaoShengPaoZhiLiaoJiLu** - 超声炮治疗记录
- **ShuiGuangZhenZhiLiaoJiLu** - 水光针治疗记录
- **GuangZiZhiLiaoJiLu** - 光子治疗记录

### 财务模型
- **ChongZhiJiLu** - 预付账户充值
- **XiaoFeiJiLu/ShouFeiJiLu** - 消费和计费记录
- **ZhiLiaoXiangMuHeXiaoJiLu** - 治疗验证记录

### 流程集成模型
- **SuiFangJiLu** - 随访护理跟踪
- **DengLuQianDaoJiLu** - 签到记录
- **YuYueTiXingJiLu** - 预约提醒

## 模型特性

### 标准字段
所有模型继承通用模式：
- `label` - 中文显示名称
- `name` - 基于拼音的系统名称
- `pym` - 拼音缩写代码
- `erpsys_id` - 唯一系统标识符
- `pid` - 通过外键进行流程集成
- `created_time/updated_time` - 审计时间戳

### 业务逻辑
- 从中文标签自动生成拼音
- 基于UUID的唯一标识符
- 用于工作流集成的流程绑定
- 通过`master`字段的主从关系

### 流程集成
模型通过以下方式连接到内核流程引擎：
- **流程外键** - 将记录链接到工作流流程
- **主从关系** - 连接到操作员实体
- **服务引用** - 链接到配置的服务定义

## 生成模式

这些模型展示了从设计定义的运行时生成：
1. 设计层中的**DataItem定义**指定结构
2. **元编程**生成Django模型类
3. **流程集成**连接到工作流引擎
4. **业务逻辑**从基础模式继承

末尾的`CLASS_MAPPING`字典为框架的元编程能力启用动态模型访问。

## 使用

模型通过以下方式访问：
- Django管理界面进行数据管理
- 前端集成的API端点
- 自动化的流程工作流触发器
- AI助手交互的MCP服务器