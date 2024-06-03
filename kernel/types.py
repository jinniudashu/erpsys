from enum import Enum

class ProcessState(Enum):
    """Process状态枚举类"""
    NEW = "新建"
    READY = "就绪"
    EXECUTING = "执行中"
    WAITING = "等待"
    TERMINATED = "终止"
