register = [0] * 32
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


def parse(cycle, address):
    finish = 0
    if "BREAK" in instruction[address]:
        finish = 1
    return f"Cycle:{cycle}" + instruction[address][37:], address + 4, finish


def show_reg():
    reg = [
        "Registers",
        "R00:" + "".join([f"\t{register[i]}" for i in range(16)]),
        "R16:" + "".join([f"\t{register[i+16]}" for i in range(16)]) + "\n",
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
