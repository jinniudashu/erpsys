from enum import Enum, auto

class ProcessState(Enum):
    """进程状态枚举"""
    NEW = auto()
    READY = auto()
    RUNNING = auto()
    WAITING = auto()
    TERMINATED = auto()
    SUSPENDED = auto()
    ERROR = auto()

    @property
    def description(self):
        return {
            ProcessState.NEW: "新建",
            ProcessState.READY: "就绪",
            ProcessState.RUNNING: "运行",
            ProcessState.WAITING: "等待",
            ProcessState.SUSPENDED: "挂起",
            ProcessState.TERMINATED: "终止",
            ProcessState.ERROR: "错误"
        }[self]

ChoiceType = [
    ('Select', '下拉单选'),
    ('RadioSelect', '单选按钮列表'),
    ('CheckboxSelectMultiple', '复选框列表'),
    ('SelectMultiple', '下拉多选')
]

# JSON Schema用于上下文验证（生产环境中应更完整）
CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "frames": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "process_id": {"type": "string"},
                    "status": {"type": "string"},
                    "local_vars": {"type": "object"},
                    "inherited_context": {"type": "object"},
                    "return_value": {},
                    "error_info": {},
                    "program_pointer": {},
                    "registers": {"type": "object"},
                    "resource_management": {"type": "object"},
                    "accounting": {"type": "object"},
                    "scheduling_info": {"type": "object"},
                    "events_triggered_log": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["process_id", "status", "local_vars", "inherited_context"]
            }
        },
        # "timestamp": {"type": "string", "format": "date-time"}
    },
    "required": ["frames"]
}