register = {f"R{i}": 0 for i in range(32)}
memory = {}
instruction = {}

if_unit = ["", ""]
pre_issue = []
pre_alu = []
post_alu = ""
pre_alu_b = []
post_alu_b = ""
pre_mem = []
post_mem = ""

finish = False
is_finish_wait = False
is_stall = False
is_break = False
reg_ready = {f"R{i}": True for i in range(32)}

cycle = 0
address = 64


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
                instruction[int(ins_split[6])] = line.lstrip("01 ").strip()
            else:
                instruction[int(ins_split[6])] = line.lstrip("01 ").strip()


def j(ins):
    global address
    ins_split = ins.split()
    if ins_split[0] == "J":
        offset = int(ins_split[-1].strip("#"))
        offset_binary = "{:028b}".format(offset)
        pc_binary = "{:032b}".format(address)
        address = int(pc_binary[:4] + offset_binary, 2)
    else:
        address = register[ins_split[-1]]
    return address


def b(ins):
    global address
    ins_split = ins.split()
    offset = int(ins_split[-1].strip("#"))
    if ins_split[0] == "BEQ":
        rs = register[ins_split[-3].strip(",")]
        rt = register[ins_split[-2].strip(",")]
        if rs == rt:
            address += offset
    elif ins_split[0] == "BLTZ":
        rs = register[ins_split[-2].strip(",")]
        if rs < 0:
            address += offset
    else:
        rs = register[ins_split[-2].strip(",")]
        if rs > 0:
            address += offset


def if_parse(ins):
    """调用它的指令一定会执行，只需要检测跳转指令"""
    global finish
    ins_split = ins.split()
    if ins_split[0] in ["J", "JR"]:
        j(ins)
        if_unit[1] = ins
    elif ins_split[0] in ["BEQ", "BLTZ", "BGTZ"]:
        b(ins)
        if_unit[1] = ins
    elif ins_split[0] == "BREAK":
        finish = True
        if_unit[1] = ins
    elif ins_split[0] == "NOP":
        if_unit[1] = ins
    else:
        pre_issue.append(f"[{ins}]")


def get_instruction():
    """取一条指令"""
    global address
    return instruction[address].lstrip("0123456789 ").strip()


def is_branch(ins_name):
    if ins_name in ["J", "JR", "BEQ", "BLTZ", "BGTZ"]:
        return True


def is_not_branch_stall(ins):
    ins_split = ins.split()
    if ins_split[0] == "JR":
        return reg_ready[ins_split[-1]]
    if ins_split[0] == "BEQ":
        rs = reg_ready[ins_split[-3].strip(",")]
        rt = reg_ready[ins_split[-2].strip(",")]
        return rs and rt
    if ins_split[0] in ["BLTZ", "BGTZ"]:
        return reg_ready[ins_split[-2].strip(",")]


def if_get_i_():
    global is_stall, address, is_finish_wait, finish
    if is_stall:  # 上周期停止，本次不取指，并判断此时是否满足情况
        is_stall = False
        if not is_not_branch_stall(if_unit[0].split()):  # 判断 is_stall 是否变更为 True
            is_stall = True
        return
    if if_unit[0] != "":  # 存在 wait 的分支指令，执行它 (((此处需要考虑此时pre buffer满是否能执行)))
        if_parse(if_unit[0])
        is_finish_wait = True
        return
    if len(pre_issue) == 4:  # pre_issue 满，本次不取指
        return
    if len(pre_issue) == 3:  # pre_issue 一个空槽，取一条指令
        ins = get_instruction()
        ins_split = ins.split()
        if is_branch(ins_split[0]):  # 判断是否为分支指令
            if not is_not_branch_stall(ins):  # 判断 is_stall 是否变更为 True
                if_unit[0] = ins
                is_stall = True
                return
            if_parse(ins)
        else:
            if_parse(ins)
            address += 4
    else:  # 一个周期取两条指令
        ins = get_instruction()
        ins_split = ins.split()
        if is_branch(ins_split[0]):  # 判断第一条指令是否为分支指令，是的话不再取第二条指令
            if not is_not_branch_stall(ins):  # 判断 is_stall 是否变更为 True
                if_unit[0] = ins
                is_stall = True
                return
            if_parse(ins)
        else:  # 第一条指令不是分支指令，且上一条指令不是 break，取第二条指令
            if_parse(ins)
            address += 4
            if finish:
                return
            ins = get_instruction()
            ins_split = ins.split()
            if is_branch(ins_split[0]):  # 判断是否为分支指令
                if not is_not_branch_stall(ins):  # 判断 is_stall 是否变更为 True
                    if_unit[0] = ins
                    is_stall = True
                    return
                if_parse(ins)
            else:
                if_parse(ins)
                address += 4
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
    return [
        "IF Unit:",
        f"\tWaiting Instruction:{if_unit[0]}",
        f"\tExecuted Instruction:{if_unit[1]}",
    ]


def show_pre_issue():
    """展示 pre issue"""
    while len(pre_issue) < 4:
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
    while len(pre_alu) < 2:
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
    while len(pre_alu_b) < 2:
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
    while len(pre_mem) < 2:
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
    global is_stall, is_finish_wait
    # 周期开始上升沿：处理四个周期的内容
    if_get_i_()
    issue_()
    mem_()
    alu_()
    alu_b_()
    wb_()

    # 周期结束上升沿：完成善后工作、buffer清除、占用解除等等
    if is_finish_wait:
        if_unit[0] = ""
        is_finish_wait = False

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
