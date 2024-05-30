class TuringMachine:
    def __init__(self, program, initial_state):
        self.program = program  # 程序是一个字典，键为(状态, 读取的值)，值为(写入的值, 移动方向, 下一个状态)
        self.state = initial_state  # 图灵机的初始状态
        self.tape = [0] * 1000  # 初始化一个有1000个格的纸带，所有格初始化为0
        self.head = len(self.tape) // 2  # 读写头初始在纸带中间位置
        self.counter = 0  # 程序计数器

    def step(self):
        """执行图灵机的一个步骤"""
        key = (self.state, self.tape[self.head])
        if key in self.program:
            value, direction, next_state = self.program[key]
            self.tape[self.head] = value
            if direction == 'R':
                self.head += 1
            elif direction == 'L':
                self.head -= 1
            self.state = next_state
            self.counter += 1
        else:
            print("No valid instruction, machine halts.")
            return False
        return True

    def run(self):
        """运行图灵机，直到没有有效的指令为止"""
        while self.step():
            pass
        print("Machine halted after", self.counter, "steps.")
        print("Final tape state:", self.tape[self.head-10:self.head+10])

# 示例用法
program = {
    (0, 0): (1, 'R', 1),
    (1, 0): (1, 'L', 0),
    (1, 1): (0, 'R', 0),
    (0, 1): (1, 'L', 1),
}
tm = TuringMachine(program, 0)
tm.run()
