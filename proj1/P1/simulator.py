register = {f"R{i}": 0 for i in range(32)}
memory = {}
instruction = {}


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


def op(address):
    ins_split = instruction[address].split()
    address += 4
    rs = register[ins_split[-2].strip(",")]
    if ins_split[-1].startswith("#"):
        rt = int(ins_split[-1].strip("#"))
    else:
        rt = register[ins_split[-1]]
    if ins_split[7] == "ADD":
        register[ins_split[-3].strip(",")] = rs + rt
    elif ins_split[7] == "SUB":
        register[ins_split[-3].strip(",")] = rs - rt
    elif ins_split[7] == "MUL":
        register[ins_split[-3].strip(",")] = rs * rt
    elif ins_split[7] == "AND":
        register[ins_split[-3].strip(",")] = rs and rt
    elif ins_split[7] == "NOR":
        register[ins_split[-3].strip(",")] = not (rs or rt)
    else:
        register[ins_split[-3].strip(",")] = rs < rt
    return address


def j(address):
    ins_split = instruction[address].split()
    address += 4
    if ins_split[7] == "J":
        offset = int(ins_split[-1].strip("#"))
        offset_binary = "{:028b}".format(offset)
        pc_binary = "{:032b}".format(address)
        address = int(pc_binary[:4] + offset_binary, 2)
    else:
        address = register[ins_split[-1]]
    return address


def b(address):
    ins_split = instruction[address].split()
    address += 4
    offset = int(ins_split[-1].strip("#"))
    if ins_split[7] == "BEQ":
        rs = register[ins_split[-3].strip(",")]
        rt = register[ins_split[-2].strip(",")]
        if rs == rt:
            # offset_binary = "{:018b}".format(offset)
            # pc_binary = "{:032b}".format(address)
            # address = int(pc_binary[:14] + offset_binary, 2)
            address += offset
    elif ins_split[7] == "BLTZ":
        rs = register[ins_split[-2].strip(",")]
        if rs < 0:
            # offset_binary = "{:018b}".format(offset)
            # pc_binary = "{:032b}".format(address)
            # address = int(pc_binary[:14] + offset_binary, 2)
            address += offset
    else:
        rs = register[ins_split[-2].strip(",")]
        if rs > 0:
            # offset_binary = "{:018b}".format(offset)
            # pc_binary = "{:032b}".format(address)
            # address = int(pc_binary[:14] + offset_binary, 2)
            address += offset
    return address


def ls(address):
    ins_split = instruction[address].split()
    address += 4
    index = ins_split[-1].find("(")
    offset = int(ins_split[-1][:index])
    base = ins_split[-1][index + 1 :].strip(")")
    if ins_split[7] == "SW":
        memory[offset + register[base]] = register[ins_split[-2].strip(",")]
    else:
        register[ins_split[-2].strip(",")] = int(memory[offset + register[base]])
    return address


def s(address):
    ins_split = instruction[address].split()
    address += 4
    rt = register[ins_split[-2].strip(",")]
    sa = int(ins_split[-1].strip("#"))
    if ins_split[7] == "SLL":
        register[ins_split[-3].strip(",")] = rt << sa
    elif ins_split[7] == "SRL":
        if rt >= 0:
            register[ins_split[-3].strip(",")] = rt >> sa
        else:
            register[ins_split[-3].strip(",")] = (rt + 0x100000000) >> sa
    else:
        register[ins_split[-3].strip(",")] = rt >> sa
    return address


def parse(cycle, address):
    finish = 0
    ins_split = instruction[address].split()
    if ins_split[7] in ["ADD", "SUB", "MUL", "AND", "NOR", "SLT"]:
        address = op(address)
    elif ins_split[7] in ["J", "JR"]:
        address = j(address)
    elif ins_split[7] in ["BEQ", "BLTZ", "BGTZ"]:
        address = b(address)
    elif ins_split[7] in ["SW", "LW"]:
        address = ls(address)
    elif ins_split[7] in ["SLL", "SRL", "SRA"]:
        address = s(address)
    elif ins_split[7] in ["NOP"]:
        address += 4
    else:
        finish = 1
    return f"Cycle:{cycle}" + instruction[address][37:], address, finish


def show_reg():
    reg = [
        "Registers",
        "R00:" + "".join([f"\t{register['R'+str(i)]}" for i in range(16)]),
        "R16:" + "".join([f"\t{register['R'+str(i+16)]}" for i in range(16)]) + "\n",
    ]
    return reg


def show_mem():
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


def operate(cycle, address):
    mark, address, finish = parse(cycle, address)
    outcomes = ["-" * 20, mark]
    outcomes += show_reg()
    outcomes += show_mem()
    return outcomes, address, finish


def execute(filename):
    simulation_name = "simulation.txt"
    finish = 0
    cycle = 0
    address = 64
    results = []
    initialization(filename)
    while not finish:
        cycle += 1
        outcome, address, finish = operate(cycle, address)
        results += outcome
    with open(simulation_name, "w") as f:
        f.writelines("\n".join(results))
    return simulation_name
