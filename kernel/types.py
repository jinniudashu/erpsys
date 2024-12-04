from enum import Enum, auto

class ProcessState(Enum):
    """进程状态枚举"""
    NEW = auto()
    READY = auto()
    RUNNING = auto()
    WAITING = auto()
    TERMINATED = auto()

    @property
    def description(self):
        return {
            ProcessState.NEW: "新建",
            ProcessState.READY: "就绪",
            ProcessState.RUNNING: "执行中",
            ProcessState.WAITING: "等待",
            ProcessState.TERMINATED: "终止"
        }[self]

ChoiceType = [
    ('Select', '下拉单选'),
    ('RadioSelect', '单选按钮列表'),
    ('CheckboxSelectMultiple', '复选框列表'),
    ('SelectMultiple', '下拉多选')
]