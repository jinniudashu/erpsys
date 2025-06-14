# Django ERP 系统的 MCP 服务器

该目录包含Django ERP系统的模型上下文协议（MCP）服务器实现，提供对DataItem和DataItemConsists模型的访问。

## 功能特性

- **DataItem管理**：创建、读取、更新、删除DataItem记录
- **关系管理**：管理DataItemConsists关系
- **搜索和查询**：按各种条件搜索和过滤DataItems
- **祖先跟踪**：获取继承链和组合关系

## 验证方法

### 1. Django管理命令

#### 基础测试
```bash
python manage.py test_mcp_server
```

#### 带数据创建的完整测试
```bash
python manage.py test_mcp_server --create-test-data --test-mcp-functions
```

#### 运行MCP服务器
```bash
python manage.py run_mcp_server
```

### 2. 独立验证
```bash
python mcp_servers/verify_mcp.py
```

### 3. STDIO模式测试
```bash
python test_mcp_stdio.py
```

## 可用工具

- `create_data_item()` - 创建新的DataItem
- `update_data_item()` - 更新现有DataItem
- `delete_data_item()` - 删除DataItem
- `list_data_items()` - 带过滤的DataItems列表
- `search_data_items()` - 按文本搜索DataItems
- `add_data_item_consists()` - 添加组合关系
- `remove_data_item_consists()` - 移除组合关系

## 可用资源

- `dataitem://{item_id}` - 获取特定DataItem
- `dataitem://{item_id}/consists` - 获取DataItem组合关系
- `dataitem://{item_id}/ancestry` - 获取DataItem继承链和组合

## 使用示例

### 创建DataItem
```python
from mcp_servers.mcp_server import create_data_item

new_item = create_data_item(
    label="新数据项",
    field_type="CharField",
    implement_type="Field",
    max_length=100
)
```

### 搜索DataItems
```python
from mcp_servers.mcp_server import search_data_items

results = search_data_items("测试", limit=10)
```

### 获取带关系的DataItem
```python
from mcp_servers.mcp_server import get_data_item_ancestry

ancestry_data = get_data_item_ancestry(item_id)
print(f"祖先: {len(ancestry_data['ancestry'])}")
print(f"组成: {len(ancestry_data['consists'])}")
```

## 与Django的集成

MCP服务器与Django完全集成：

1. **Django设置**：使用`erpsys.settings`配置
2. **Django模型**：直接访问`design.models.DataItem`和`DataItemConsists`
3. **Django ORM**：所有数据库操作使用Django ORM
4. **Django管理**：通过Django管理命令访问

## 验证结果

正确配置后，您应该看到：

```
=== MCP服务器Django集成测试 ===
✓ MCP服务器导入成功
✓ Django模型可访问。DataItem数量: XX
✓ list_data_items 返回 X 项
✓ get_data_item 检索: [item_label]
✓ get_data_item_consists 返回 X 关系
✓ get_data_item_ancestry 返回祖先: X, 组成: X
✓ search_data_items 找到 X 项
✓ create_data_item 创建: [new_item_label] (ID: XX)
=== 测试完成 ===
```

## 故障排除

### 常见问题

1. **导入错误**：确保Django正确配置且应用在INSTALLED_APPS中
2. **数据库错误**：如果DataItem表不存在，运行迁移
3. **UUID验证**：服务器自动处理UUID到字符串的转换

### 调试模式

在开发期间设置Django DEBUG=True以获得详细的错误消息。

## 服务器信息

- **服务器名称**：ERPSysDataItemMCP
- **传输**：STDIO（默认）
- **协议**：模型上下文协议（MCP）
- **Django集成**：完整ORM访问

## AI助手集成

MCP服务器使AI助手能够：

### 业务建模支持
- **实体设计**：帮助创建和修改业务实体定义
- **关系管理**：协助设置复杂的实体关系
- **继承设计**：指导业务类型继承结构
- **组合模式**：优化数据项组合关系

### 自动化配置
- **字段推荐**：基于业务需求建议字段类型
- **验证规则**：帮助定义数据验证逻辑
- **默认值设置**：智能推荐字段默认值
- **API映射**：协助外部系统集成

### 文档生成
- **模型文档**：自动生成业务模型文档
- **关系图**：创建实体关系图
- **配置指南**：生成系统配置说明
- **最佳实践**：提供设计模式建议

### 问题诊断
- **模型验证**：检查模型定义的一致性
- **性能分析**：识别潜在的性能问题
- **依赖检查**：验证模型间的依赖关系
- **错误修复**：协助解决配置问题

MCP服务器作为设计层和AI助手之间的桥梁，实现智能化的业务建模和配置优化。