register = {f"R{i}": 0 for i in range(32)}
memory = {}
instruction = {}

if_unit = []
pre_issue = []
pre_alu = []
post_alu = ""
pre_alu_b = []
post_alu_b = ""
pre_mem = []
post_mem = ""

is_stall = False
is_break = False
reg_ready = [True] * 32

cycle = 0
finish = 0


def initialization(filename):
    """
    Initialize memory and instructions
    :param filename: assembly file
    :return: No return value
    """
    break_flag = 0
    with open(filename, "r") as f:
        for line in f.readlines():
            ins_split = line.split()
            if break_flag == 1:
                memory[int(ins_split[1])] = ins_split[2]
            elif "BREAK" in line:
                break_flag = 1
                instruction[int(ins_split[6])] = line
            else:
                instruction[int(ins_split[6])] = line


def if_get_i_():
    global is_stall
    if is_stall:
        is_stall = False
        return

    return


def issue_():
    return


def mem_():
    return


def alu_():
    return


def alu_b_():
    return


def wb_():
    return


def show_if_unit():
    """展示 if unit"""
    while len(if_unit) != 2:
        if_unit.append("")
    return [
        "IF Unit:",
        f"\tWaiting Instruction:{if_unit[0]}",
        f"\tExecuted Instruction:{if_unit[1]}",
    ]


def show_pre_issue():
    """展示 pre issue"""
    while len(pre_issue) != 4:
        pre_issue.append("")
    return [
        "Pre-Issue Buffer:",
        f"\tEntry 0:{pre_issue[0]}",
        f"\tEntry 1:{pre_issue[1]}",
        f"\tEntry 2:{pre_issue[2]}",
        f"\tEntry 3:{pre_issue[3]}",
    ]


def show_pre_alu():
    """展示 pre alu"""
    while len(pre_alu) != 2:
        pre_alu.append("")
    return [
        "Pre-ALU Queue:",
        f"\tEntry 0:{pre_alu[0]}",
        f"\tEntry 1:{pre_alu[1]}",
    ]


def show_post_alu():
    """展示 post alu"""
    return [f"Post-ALU Buffer:{post_alu}"]


def show_pre_alu_b():
    """展示 pre alub"""
    while len(pre_alu_b) != 2:
        pre_alu_b.append("")
    return [
        "Pre-ALUB Queue:",
        f"\tEntry 0:{pre_alu_b[0]}",
        f"\tEntry 1:{pre_alu_b[1]}",
    ]


def show_post_alu_b():
    """展示 post alub"""
    return [f"Post-ALUB Buffer:{post_alu_b}"]


def show_pre_mem():
    """展示 pre mem"""
    while len(pre_mem) != 2:
        pre_mem.append("")
    return [
        "Pre-MEM Queue:",
        f"\tEntry 0:{pre_mem[0]}",
        f"\tEntry 1:{pre_mem[1]}",
    ]


def show_post_mem():
    """展示 post mem"""
    return [f"Post-MEM Buffer:{post_mem}\n"]


def show_reg():
    """
    格式化展示寄存器的值
    :return:reg
    """
    reg = [
        "Registers",
        "R00:" + "".join([f"\t{register['R' + str(i)]}" for i in range(8)]),
        "R08:" + "".join([f"\t{register['R' + str(i + 8)]}" for i in range(8)]),
        "R16:" + "".join([f"\t{register['R' + str(i + 16)]}" for i in range(8)]),
        "R24:" + "".join([f"\t{register['R' + str(i + 24)]}" for i in range(8)]) + "\n",
    ]
    return reg


def show_mem():
    """
    格式化展示内存的值
    :return:mem
    """
    mem = ["Data"]
    keys = list(memory.keys())
    keys.sort()
    while len(keys) // 8:
        mem.append(
            str(keys[0]) + ":" + "".join([f"\t{memory[keys[i]]}" for i in range(8)])
        )
        keys = keys[8:]
    if len(keys):
        mem.append(
            str(keys[0])
            + ":"
            + "".join([f"\t{memory[keys[i]]}" for i in range(len(keys))])
        )
    mem[-1] = mem[-1] + "\n"
    return mem


def print_cycle():
    """单个周期展示结果"""
    global cycle
    cycle += 1
    outcomes = ["-" * 20, f"Cycle:{cycle}\n"]
    outcomes += show_if_unit()
    outcomes += show_pre_issue()
    outcomes += show_pre_alu()
    outcomes += show_post_alu()
    outcomes += show_pre_alu_b()
    outcomes += show_post_alu_b()
    outcomes += show_pre_mem()
    outcomes += show_post_mem()
    outcomes += show_reg()
    outcomes += show_mem()
    return outcomes


def operate():
    # 周期开始上升沿：处理四个周期的内容
    if_get_i_()
    issue_()
    mem_()
    alu_()
    alu_b_()
    wb_()

    # 周期结束上升沿：完成善后工作、buffer清除、占用解除等等

    # 打印每个周期内容
    outcomes = print_cycle()
    return outcomes


def execute(input_filename, simulation_name):
    global finish
    results = []
    initialization(input_filename)
    while not finish:
        outcome = operate()
        results += outcome
    with open(simulation_name, "w") as f:
        f.writelines("\n".join(results))
    return simulation_name
