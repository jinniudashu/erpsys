# mcp_server.py
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erpsys.settings')
django.setup()

from fastmcp import FastMCP
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union
from design.models import DataItem, DataItemConsists
import uuid

# 初始化 FastMCP Server
mcp = FastMCP("ERPSysDataItemMCP")

# 公共工具函数
def safe_int_convert(value, default=None):
    """安全地将值转换为整数"""
    if value is None or value == '':
        return default
    try:
        return int(float(value)) if value != '' else default
    except (ValueError, TypeError):
        return default

# 定义 Pydantic 模型
class DataItemSchema(BaseModel):
    id: int
    label: Optional[str] = None
    name: Optional[str] = None
    pym: Optional[str] = None
    erpsys_id: Optional[str] = None
    field_type: Optional[str] = None
    business_type_id: Optional[int] = None
    sub_class: Optional[str] = None
    affiliated_to_id: Optional[int] = None
    implement_type: str = 'Field'
    dependency_order: int = 0
    default_value: Optional[str] = None
    is_multivalued: bool = False
    max_length: Optional[int] = 255
    max_digits: Optional[int] = 10
    decimal_places: Optional[int] = 2
    computed_logic: Optional[str] = None
    init_content: Optional[Dict[str, Any]] = None
    
    @field_validator('erpsys_id', mode='before')
    @classmethod
    def validate_erpsys_id(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
    
    @field_validator('init_content', mode='before')
    @classmethod
    def validate_init_content(cls, v):
        # Convert JSON string to dict if needed
        if isinstance(v, str) and v:
            try:
                import json
                parsed = json.loads(v)
                # If it's a list, convert to dict with index as keys
                if isinstance(parsed, list):
                    return {str(i): item for i, item in enumerate(parsed)}
                return parsed
            except (json.JSONDecodeError, ValueError):
                return None
        # If it's already a list, convert to dict
        elif isinstance(v, list):
            return {str(i): item for i, item in enumerate(v)}
        return v
    
    @field_validator('max_length', 'max_digits', 'decimal_places', mode='before')
    @classmethod
    def validate_numeric_fields(cls, v):
        if v is not None and isinstance(v, (float, str)):
            try:
                return int(v) if v != '' else None
            except (ValueError, TypeError):
                return v
        return v
    
    class Config:
        from_attributes = True

class DataItemConsistsSchema(BaseModel):
    id: int
    data_item_id: Optional[int] = None
    sub_data_item_id: Optional[int] = None
    order: int = 10
    default_value: Optional[str] = None
    map_api_field_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Resource 和 Tool 定义
@mcp.resource("dataitem://{item_id}")
def get_data_item(item_id: int) -> DataItemSchema:
    """获取指定ID的数据项"""
    try:
        data_item = DataItem.objects.get(id=item_id)
        return DataItemSchema.model_validate(data_item)
    except DataItem.DoesNotExist:
        raise ValueError(f"DataItem with id {item_id} not found")

@mcp.resource("dataitem://{item_id}/consists")
def get_data_item_consists(item_id: int) -> List[DataItemConsistsSchema]:
    """获取指定数据项的组成关系"""
    try:
        data_item = DataItem.objects.get(id=item_id)
        consists_relations = DataItemConsists.objects.filter(data_item=data_item)
        return [DataItemConsistsSchema.model_validate(relation) for relation in consists_relations]
    except DataItem.DoesNotExist:
        raise ValueError(f"DataItem with id {item_id} not found")

@mcp.resource("dataitem://{item_id}/ancestry")
def get_data_item_ancestry(item_id: int) -> Dict[str, List[DataItemSchema]]:
    """获取数据项的继承链和组成项"""
    try:
        data_item = DataItem.objects.get(id=item_id)
        ancestry_list, consists_list = data_item.get_ancestry_and_consists()
        
        return {
            "ancestry": [DataItemSchema.model_validate(item) for item in ancestry_list],
            "consists": [DataItemSchema.model_validate(item) for item in consists_list]
        }
    except DataItem.DoesNotExist:
        raise ValueError(f"DataItem with id {item_id} not found")

@mcp.tool()
def create_data_item(
    label: str,
    field_type: str = 'CharField',
    implement_type: str = 'Field',
    business_type_id: Optional[Union[int, str, float]] = None,
    sub_class: Optional[str] = None,
    affiliated_to_id: Optional[Union[int, str, float]] = None,
    dependency_order: Union[int, str, float] = 0,
    default_value: Optional[str] = None,
    is_multivalued: bool = False,
    max_length: Optional[Union[int, str, float]] = 255,
    max_digits: Optional[Union[int, str, float]] = 10,
    decimal_places: Optional[Union[int, str, float]] = 2,
    computed_logic: Optional[str] = None,
    init_content: Optional[Dict[str, Any]] = None
) -> DataItemSchema:
    """创建新的数据项"""
    # Convert numeric parameters to integers if they're strings or floats
    max_length = safe_int_convert(max_length, None)
    max_digits = safe_int_convert(max_digits, None)
    decimal_places = safe_int_convert(decimal_places, None)
    dependency_order = safe_int_convert(dependency_order, 0)
    business_type_id = safe_int_convert(business_type_id, None)
    affiliated_to_id = safe_int_convert(affiliated_to_id, None)
    
    business_type = None
    if business_type_id:
        try:
            business_type = DataItem.objects.get(id=business_type_id)
        except DataItem.DoesNotExist:
            raise ValueError(f"Business type DataItem with id {business_type_id} not found")
    
    affiliated_to = None
    if affiliated_to_id:
        try:
            affiliated_to = DataItem.objects.get(id=affiliated_to_id)
        except DataItem.DoesNotExist:
            raise ValueError(f"Affiliated DataItem with id {affiliated_to_id} not found")
    
    data_item = DataItem.objects.create(
        label=label,
        field_type=field_type,
        business_type=business_type,
        sub_class=sub_class,
        affiliated_to=affiliated_to,
        implement_type=implement_type,
        dependency_order=dependency_order,
        default_value=default_value,
        is_multivalued=is_multivalued,
        max_length=max_length,
        max_digits=max_digits,
        decimal_places=decimal_places,
        computed_logic=computed_logic,
        init_content=init_content
    )
    return DataItemSchema.model_validate(data_item)

@mcp.tool()
def update_data_item(item_id: Union[int, str, float], data: Dict[str, Any]) -> DataItemSchema:
    """更新数据项"""
    # Convert item_id to int if needed
    item_id = safe_int_convert(item_id)
    if item_id is None:
        raise ValueError("Invalid item_id")
    
    try:
        data_item = DataItem.objects.get(id=item_id)
        
        # Handle foreign key fields
        if 'business_type_id' in data and data['business_type_id']:
            try:
                business_type = DataItem.objects.get(id=data['business_type_id'])
                data_item.business_type = business_type
                del data['business_type_id']
            except DataItem.DoesNotExist:
                raise ValueError(f"Business type DataItem with id {data['business_type_id']} not found")
        
        if 'affiliated_to_id' in data and data['affiliated_to_id']:
            try:
                affiliated_to = DataItem.objects.get(id=data['affiliated_to_id'])
                data_item.affiliated_to = affiliated_to
                del data['affiliated_to_id']
            except DataItem.DoesNotExist:
                raise ValueError(f"Affiliated DataItem with id {data['affiliated_to_id']} not found")
        
        # Update other fields
        for field, value in data.items():
            if hasattr(data_item, field):
                setattr(data_item, field, value)
        
        data_item.save()
        return DataItemSchema.model_validate(data_item)
    except DataItem.DoesNotExist:
        raise ValueError(f"DataItem with id {item_id} not found")

@mcp.tool()
def delete_data_item(item_id: Union[int, str, float]) -> bool:
    """删除数据项"""
    # Convert item_id to int if needed
    item_id = safe_int_convert(item_id)
    if item_id is None:
        raise ValueError("Invalid item_id")
    
    try:
        deleted, _ = DataItem.objects.filter(id=item_id).delete()
        return deleted > 0
    except Exception as e:
        raise ValueError(f"Failed to delete DataItem with id {item_id}: {str(e)}")

@mcp.tool()
def add_data_item_consists(
    data_item_id: Union[int, str, float],
    sub_data_item_id: Union[int, str, float],
    order: Union[int, str, float] = 10,
    default_value: Optional[str] = None,
    map_api_field_id: Optional[Union[int, str, float]] = None
) -> DataItemConsistsSchema:
    """为数据项添加组成关系"""
    # Convert numeric parameters to int
    data_item_id = safe_int_convert(data_item_id)
    sub_data_item_id = safe_int_convert(sub_data_item_id)
    order = safe_int_convert(order, 10)
    map_api_field_id = safe_int_convert(map_api_field_id, None)
    
    if data_item_id is None or sub_data_item_id is None:
        raise ValueError("Invalid data_item_id or sub_data_item_id")
    
    try:
        data_item = DataItem.objects.get(id=data_item_id)
        sub_data_item = DataItem.objects.get(id=sub_data_item_id)
        
        map_api_field = None
        if map_api_field_id:
            from design.models import ApiFields
            try:
                map_api_field = ApiFields.objects.get(id=map_api_field_id)
            except ApiFields.DoesNotExist:
                raise ValueError(f"ApiField with id {map_api_field_id} not found")
        
        consists_relation = DataItemConsists.objects.create(
            data_item=data_item,
            sub_data_item=sub_data_item,
            order=order,
            default_value=default_value,
            map_api_field=map_api_field
        )
        return DataItemConsistsSchema.model_validate(consists_relation)
    except DataItem.DoesNotExist as e:
        raise ValueError(f"DataItem not found: {str(e)}")

@mcp.tool()
def remove_data_item_consists(data_item_id: Union[int, str, float], sub_data_item_id: Union[int, str, float]) -> bool:
    """移除数据项的组成关系"""
    # Convert parameters to int
    data_item_id = safe_int_convert(data_item_id)
    sub_data_item_id = safe_int_convert(sub_data_item_id)
    
    if data_item_id is None or sub_data_item_id is None:
        raise ValueError("Invalid data_item_id or sub_data_item_id")
    
    try:
        deleted, _ = DataItemConsists.objects.filter(
            data_item_id=data_item_id,
            sub_data_item_id=sub_data_item_id
        ).delete()
        return deleted > 0
    except Exception as e:
        raise ValueError(f"Failed to remove consists relation: {str(e)}")

@mcp.tool()
def list_data_items(
    field_type: Optional[str] = None,
    implement_type: Optional[str] = None,
    business_type_id: Optional[Union[int, str, float]] = None,
    limit: Union[int, str, float] = 50
) -> List[DataItemSchema]:
    """列出数据项（支持过滤）"""
    # Convert numeric parameters to int
    business_type_id = safe_int_convert(business_type_id, None)
    limit = safe_int_convert(limit, 50)
    if limit <= 0:
        limit = 50
    
    queryset = DataItem.objects.all()
    
    if field_type:
        queryset = queryset.filter(field_type=field_type)
    if implement_type:
        queryset = queryset.filter(implement_type=implement_type)
    if business_type_id:
        queryset = queryset.filter(business_type_id=business_type_id)
    
    queryset = queryset[:limit]
    return [DataItemSchema.model_validate(item) for item in queryset]

@mcp.tool()
def search_data_items(query: str, limit: Union[int, str, float] = 20) -> List[DataItemSchema]:
    """搜索数据项（按标签和名称）"""
    from django.db.models import Q
    
    # Convert limit to int
    limit = safe_int_convert(limit, 20)
    if limit <= 0:
        limit = 20
    
    queryset = DataItem.objects.filter(
        Q(label__icontains=query) | 
        Q(name__icontains=query) |
        Q(pym__icontains=query)
    )[:limit]
    
    return [DataItemSchema.model_validate(item) for item in queryset]

# 运行服务器（STDIO模式）
if __name__ == "__main__":
    mcp.run()