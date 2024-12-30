from django.dispatch import Signal

# 人工指令信号
ux_input_signal = Signal(["process"])

# 作业开始
operand_started = Signal(['pid'])

# 作业变更
operand_changed = Signal(['pid', 'request', 'form_data', 'formset_data'])

# 作业完成
operand_finished = Signal(['pid', 'request', 'form_data', 'formset_data'])
