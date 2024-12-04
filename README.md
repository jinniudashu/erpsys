# django-erp-os-framework

"""
进程控制块 - ProcessControlBlock, 用于在多个语义层级上管理业务进程
每个层级是独立的语义空间, 都有各自的独立业务上下文, 有适宜本层语义空间的Assistants Manager对当前层次的进程依照本层级业务规则进行特定操作, 包括：业务事件、调度规则、现场调度控制、初始化进程
1. 跟踪合约进程的状态，确定特定会员的合约执行接下来要做什么？为其中的哪位客户进行哪个服务项目？输出一个服务序列
2. 跟踪服务进程的状态，确定特定客户的服务项目接下来要做什么，什么时候做，谁做？输出一个任务序列
3. 跟踪任务进程的状态，确定特定任务接下来的操作序列是什么？输出一个操作序列

schedule_context: 
进程的优先级
估计或测量的执行时间
截止日期或其他时间限制
资源需求（CPU、内存、I/O 等）
安全或访问控制信息
其他调度策略或参数

control_context:
进程标识和属性（例如 PID、父进程、用户 ID、组 ID）
进程状态（例如，运行、暂停、终止）
进程调度参数（例如，量子、优先级提升、抢占）
进程资源使用情况（例如 CPU 时间、内存、I/O）
进程通信通道（例如管道、套接字、共享内存）
处理安全和访问控制信息
其他过程控制参数或标志

process_program:
解释性语言（例如 Python、Ruby、JavaScript）的字节码文件
shell 或命令语言（例如 Bash、PowerShell、cmd）中的脚本文件

process_data:
程序中定义的全局或静态变量
在运行时分配的动态或堆变量
过程的输入或输出参数
进程使用的临时或中间数据
进程的配置或设置
进程的元数据或统计信息（例如创建时间、修改时间、访问时间）
与过程相关的其他数据或状态信息    

# Linux命令 taskset => 把进程和特定的CPU绑定在一起
# 公平分享CPU资源 Round-Robin
# 医生每位患者面诊15分钟，是一种轮转调度算法
# 动态优先级调度算法 MLFQ(Multi-Level Feedback Queue)
# Linux调度算法 CFS(Completely Fair Scheduler)
# 调度参数：nice值，优先级（权重？），实时性，时间片大小，调度策略
# 不同岗位的操作员 => 异构处理器

Operating System Services Provide:
1. User Interface: CLI, GUI
2. Program Execution: Source code -> Compiler -> Object code -> Executor
3. I/O Operations
4. File System Manipulation
5. Communications: Inter-process communication, Networking
6. Error Detection: Hardware, Software
7. Resource Allocation: CPU, Memory, I/O devices
8. Accounting: Usage statistics, Billing information -- Which users use how much and what kinds of resources
9. Protection and Security: User authentication, File permissions, Encryption

Types of System Calls
1. Process Control
2. File Manipulation
3. Device Management
4. Information Maintenance
5. Communications

Types of System Programs
1. File Management
2. Status Information
3. File Modification
4. Programming Language Support
5. Program Loading and Execution
6. Communications

"""
