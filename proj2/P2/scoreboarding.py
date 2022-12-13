register = {f"R{i}": 0 for i in range(32)}
memory = {}
instruction = {}

if_unit = ["", ""]
if_unit_tmp = ""
pre_issue = []
pre_issue_tmp = []
pre_alu = []
pre_alu_tmp = []
post_alu = ""
post_alu_tmp = ""
pre_alu_b = []
pre_alu_b_tmp = []
post_alu_b = ""
post_alu_b_tmp = ""
pre_mem = []
pre_mem_tmp = []
post_mem = ""
post_mem_tmp = ""

finish = False
is_stall = False
is_break = False
reg_read_ready = {f"R{i}": True for i in range(32)}
reg_write_ready = {f"R{i}": True for i in range(32)}
reg_write_dst = {f"R{i}": 4 for i in range(32)}

alu_b_cnt = 1
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
    global finish, if_unit_tmp
    ins_split = ins.split()
    if ins_split[0] in ["J", "JR"]:
        if_unit[0] = ""
        if_unit_tmp = ins
    elif ins_split[0] in ["BEQ", "BLTZ", "BGTZ"]:
        if_unit[0] = ""
        if_unit_tmp = ins
    elif ins_split[0] == "BREAK":
        if_unit[0] = ""
        if_unit_tmp = ins
    elif ins_split[0] == "NOP":
        if_unit[0] = ""
        if_unit_tmp = ins
    else:
        pre_issue_tmp.append(f"[{ins}]")


def get_instruction():
    """取一条指令"""
    global address
    ins = instruction[address].lstrip("0123456789 ").strip()
    address += 4
    return ins


def is_branch(ins_name):
    if ins_name in ["J", "JR", "BEQ", "BLTZ", "BGTZ"]:
        return True


def is_not_branch_stall(ins):
    ins_split = ins.split()
    unused = []
    for pre_ins in pre_issue:
        pre_ins = pre_ins.strip("[]")
        pre_ins_split = pre_ins.split()
        if pre_ins_split[0] in ["ADD", "SUB", "MUL", "AND", "NOR", "SLT"]:
            unused.append(pre_ins_split[-3].strip(","))
        elif pre_ins_split[0] in ["SLL", "SRL", "SRA"]:
            unused.append(pre_ins_split[-3].strip(","))
        elif pre_ins_split[0] in ["LW"]:
            unused.append(pre_ins_split[-2].strip(","))
    if ins_split[0] == "JR":
        if ins_split[-1] in unused:
            return False
        return reg_read_ready[ins_split[-1]]
    if ins_split[0] == "BEQ":
        if ins_split[-2].strip(",") in unused:
            return False
        if ins_split[-3].strip(",") in unused:
            return False
        rs = reg_read_ready[ins_split[-3].strip(",")]
        rt = reg_read_ready[ins_split[-2].strip(",")]
        return rs and rt
    if ins_split[0] in ["BLTZ", "BGTZ"]:
        if ins_split[-2].strip(",") in unused:
            return False
        return reg_read_ready[ins_split[-2].strip(",")]
    return True


def if_get_i_():
    global is_stall, address, finish
    if is_stall:  # 上周期停止，本次不取指，并判断此时是否满足情况
        is_stall = False
        if not is_not_branch_stall(if_unit[0]):  # 判断 is_stall 是否变更为 True
            is_stall = True
        else:
            if_parse(if_unit[0])
        return
    # if if_unit[0] != "":  # 存在 wait 的分支指令，执行它 (((此处需要考虑此时pre buffer满是否能执行)))
    #     if not is_not_branch_stall(if_unit[0]):  # 判断 is_stall 是否变更为 True
    #         is_stall = True
    #         return
    #     if_parse(if_unit[0])
    #     return
    if if_unit[1] != "":
        ins_split = if_unit[1].split()
        if ins_split[0] in ["J", "JR"]:
            j(if_unit[1])
        elif ins_split[0] in ["BEQ", "BLTZ", "BGTZ"]:
            b(if_unit[1])
        if_unit[1] = ""
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


def if_finish():
    global pre_issue, pre_issue_tmp, if_unit_tmp, finish
    if_unit[1] = if_unit_tmp
    if if_unit[1] == "BREAK":
        finish = True
    pre_issue += pre_issue_tmp
    pre_issue_tmp = []
    if_unit_tmp = ""


def is_reg_not_used(ins, index):
    is_ok = True
    ins_split = ins.split()
    if ins_split[0] in ["ADD", "SUB", "MUL", "AND", "NOR", "SLT"]:
        if reg_write_dst[ins_split[-3].strip(",")] < index:
            is_ok = False
        else:
            reg_write_dst[ins_split[-3].strip(",")] = index
        if reg_write_dst[ins_split[-2].strip(",")] < index:
            is_ok = False
        if ins_split[-1].startswith("#"):
            pass
        else:
            if reg_write_dst[ins_split[-1]] < index:
                is_ok = False
        return is_ok
    if ins_split[0] in ["SLL", "SRL", "SRA"]:
        if reg_write_dst[ins_split[-3].strip(",")] < index:
            is_ok = False
        else:
            reg_write_dst[ins_split[-3].strip(",")] = index
        if reg_write_dst[ins_split[-2].strip(",")] < index:
            is_ok = False
        return is_ok
    if ins_split[0] == "SW":
        index = ins_split[-1].find("(")
        base = ins_split[-1][index + 1 :].strip(")")
        if reg_write_dst[base] < index:
            is_ok = False
        if reg_write_dst[ins_split[-2].strip(",")] < index:
            is_ok = False
        return is_ok
    if ins_split[0] == "LW":
        index = ins_split[-1].find("(")
        base = ins_split[-1][index + 1 :].strip(")")
        if reg_write_dst[base] < index:
            is_ok = False
        if reg_write_dst[ins_split[-2].strip(",")] < index:
            is_ok = False
        else:
            reg_write_dst[ins_split[-2].strip(",")] = index
        return is_ok


def issue_parse(ins, cnt):
    ins_split = ins.split()
    if ins_split[0] in ["ADD", "SUB", "AND", "NOR", "SLT"]:
        if len(pre_alu + pre_alu_tmp) < 2:
            reg_write_dst[ins_split[-3].strip(",")] = -1
            reg_read_ready[ins_split[-3].strip(",")] = False
            pre_alu_tmp.append(f"[{ins}]")
            return cnt + 1, True
    if ins_split[0] in ["SLL", "SRL", "SRA", "MUL"]:
        if len(pre_alu_b + pre_alu_b_tmp) < 2:
            reg_write_dst[ins_split[-3].strip(",")] = -1
            reg_read_ready[ins_split[-3].strip(",")] = False
            pre_alu_b_tmp.append(f"[{ins}]")
            return cnt + 1, True
    if ins_split[0] in ["SW", "LW"]:
        if len(pre_mem + pre_mem_tmp) < 2:
            if ins_split[0] == "LW":
                reg_write_dst[ins_split[-2].strip(",")] = -1
                reg_read_ready[ins_split[-2].strip(",")] = False
            pre_mem_tmp.append(f"[{ins}]")
            return cnt + 1, True
    return cnt, False


def issue_():
    cnt = 0
    issue_i = 0
    del_issue = []
    while cnt <= 2 and issue_i < len(pre_issue):
        ins = pre_issue[issue_i].strip("[]")
        if not is_reg_not_used(ins, issue_i):  # 先判断指令对应寄存器是否被占用，无论是否被占用，都要占用相应寄存器
            issue_i += 1
            continue
        cnt, is_del = issue_parse(ins, cnt)  # 寄存器没有占用，发往对应 buffer
        if is_del:
            del_issue.append(issue_i)
        issue_i += 1
    for index in reversed(del_issue):
        del pre_issue[index]


def issue_finish():
    global pre_alu, pre_alu_tmp, pre_alu_b, pre_alu_b_tmp, pre_mem, pre_mem_tmp
    pre_alu += pre_alu_tmp
    pre_alu_b += pre_alu_b_tmp
    pre_mem += pre_mem_tmp
    pre_alu_tmp = []
    pre_alu_b_tmp = []
    pre_mem_tmp = []


def mem_():
    # global post_mem, post_mem_tmp
    # if post_mem != "":
    #     post_mem_tmp = post_mem
    # if len(pre_mem) > 0:
    #     ins = pre_mem[0].strip("[]")
    #     ins_split = ins.split()
    #     if ins_split[0] == "LW":
    #         post_mem = pre_mem[0]
    #         del pre_mem[0]
    #     else:
    #         index = ins_split[-1].find("(")
    #         offset = int(ins_split[-1][:index])
    #         base = ins_split[-1][index + 1 :].strip(")")
    #         memory[offset + register[base]] = register[ins_split[-2].strip(",")]
    #         del pre_mem[0]
    # else:
    #     post_mem = ""
    global post_mem, post_mem_tmp
    if len(pre_mem) > 0:
        ins = pre_mem[0].strip("[]")
        ins_split = ins.split()
        if ins_split[0] == "LW":
            post_mem_tmp = pre_mem[0]
            del pre_mem[0]
        else:
            index = ins_split[-1].find("(")
            offset = int(ins_split[-1][:index])
            base = ins_split[-1][index + 1 :].strip(")")
            memory[offset + register[base]] = register[ins_split[-2].strip(",")]
            del pre_mem[0]


def alu_():
    # global post_alu, post_alu_tmp
    # if post_alu != "":
    #     post_alu_tmp = post_alu
    # if len(pre_alu) > 0:
    #     post_alu = pre_alu[0]
    #     del pre_alu[0]
    # else:
    #     post_alu = ""
    global post_alu, post_alu_tmp
    if len(pre_alu) > 0:
        post_alu_tmp = pre_alu[0]
        del pre_alu[0]


def alu_b_():
    # global post_alu_b, alu_b_cnt, post_alu_b_tmp
    # if len(pre_alu_b) > 0:
    #     if alu_b_cnt == 2:
    #         post_alu_b = pre_alu_b[0]
    #         post_alu_b_tmp = post_alu_b
    #         del pre_alu_b[0]
    #         alu_b_cnt = 1
    #     else:
    #         alu_b_cnt += 1
    global post_alu_b, post_alu_b_tmp, alu_b_cnt
    if len(pre_alu_b) > 0:
        if alu_b_cnt == 2:
            post_alu_b_tmp = pre_alu_b[0]
            del pre_alu_b[0]
            alu_b_cnt = 1
        else:
            alu_b_cnt += 1


def deal_finish():
    global post_alu_tmp, post_alu, post_alu_b_tmp, post_alu_b, post_mem_tmp, post_mem
    if post_alu_tmp != "":
        post_alu = post_alu_tmp
        post_alu_tmp = ""
    if post_alu_b_tmp != "":
        post_alu_b = post_alu_b_tmp
        post_alu_b_tmp = ""
    if post_mem_tmp != "":
        post_mem = post_mem_tmp
        post_mem_tmp = ""


def wb_():
    global post_mem, post_alu, post_alu_b
    if post_mem != "":
        ins = post_mem.strip("[]")
        ins_split = ins.split()
        index = ins_split[-1].find("(")
        offset = int(ins_split[-1][:index])
        base = ins_split[-1][index + 1 :].strip(")")
        register[ins_split[-2].strip(",")] = int(memory[offset + register[base]])
        reg_write_dst[ins_split[-2].strip(",")] = 4
        reg_read_ready[ins_split[-2].strip(",")] = True
        post_mem = ""
    if post_alu != "":
        ins = post_alu.strip("[]")
        ins_split = ins.split()
        rs = register[ins_split[-2].strip(",")]
        if ins_split[-1].startswith("#"):
            rt = int(ins_split[-1].strip("#"))
        else:
            rt = register[ins_split[-1]]
        if ins_split[0] == "ADD":
            register[ins_split[-3].strip(",")] = rs + rt
        elif ins_split[0] == "SUB":
            register[ins_split[-3].strip(",")] = rs - rt
        elif ins_split[0] == "AND":
            register[ins_split[-3].strip(",")] = rs and rt
        elif ins_split[0] == "NOR":
            register[ins_split[-3].strip(",")] = not (rs or rt)
        else:
            register[ins_split[-3].strip(",")] = rs < rt
        reg_write_dst[ins_split[-3].strip(",")] = 4
        reg_read_ready[ins_split[-3].strip(",")] = True
        post_alu = ""
    if post_alu_b != "":
        ins = post_alu_b.strip("[]")
        ins_split = ins.split()
        if ins_split[0] == "MUL":
            rs = register[ins_split[-2].strip(",")]
            if ins_split[-1].startswith("#"):
                rt = int(ins_split[-1].strip("#"))
            else:
                rt = register[ins_split[-1]]
            register[ins_split[-3].strip(",")] = rs + rt
            reg_write_dst[ins_split[-3].strip(",")] = 4
            reg_read_ready[ins_split[-3].strip(",")] = True
        else:
            rt = register[ins_split[-2].strip(",")]
            sa = int(ins_split[-1].strip("#"))
            if ins_split[0] == "SLL":
                register[ins_split[-3].strip(",")] = rt << sa
            elif ins_split[0] == "SRL":
                if rt >= 0:
                    register[ins_split[-3].strip(",")] = rt >> sa
                else:
                    register[ins_split[-3].strip(",")] = (rt + 0x100000000) >> sa
            else:
                register[ins_split[-3].strip(",")] = rt >> sa
            reg_write_dst[ins_split[-3].strip(",")] = 4
            reg_read_ready[ins_split[-3].strip(",")] = True
        post_alu_b = ""


def show_if_unit():
    """展示 if unit"""
    return [
        "IF Unit:",
        f"\tWaiting Instruction:{if_unit[0]}",
        f"\tExecuted Instruction:{if_unit[1]}",
    ]


def delete_empty_string():
    cnt = 0
    for string in pre_issue:
        if string == "":
            cnt += 1
    for i in range(cnt):
        pre_issue.remove("")

    cnt = 0
    for string in pre_alu:
        if string == "":
            cnt += 1
    for i in range(cnt):
        pre_alu.remove("")

    cnt = 0
    for string in pre_alu_b:
        if string == "":
            cnt += 1
    for i in range(cnt):
        pre_alu_b.remove("")

    cnt = 0
    for string in pre_mem:
        if string == "":
            cnt += 1
    for i in range(cnt):
        pre_mem.remove("")


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
    mem[-1] = mem[-1]
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
    delete_empty_string()
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
    if_finish()
    issue_finish()
    deal_finish()
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
