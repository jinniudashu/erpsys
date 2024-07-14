from django.dispatch import Signal

# 人工指令信号
ux_input_signal = Signal()

# 作业完成信号
process_terminated_signal = Signal()