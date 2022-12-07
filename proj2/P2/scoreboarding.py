import simulator

register = {f"R{i}": 0 for i in range(32)}
memory = {}
instruction = {}

if_unit = ["", ""]
pre_issue = ["", "", "", ""]
pre_alu = ["", ""]
post_alu = ""
pre_alu_b = ["", ""]
post_alu_b = ""
pre_mem = ["", ""]
post_mem = ""

is_stall = False
is_break = False
reg_ready = [True] * 32

cycle = 0
finish = 0


def if_get_instructions():
    return


def issue():
    return


def mem():
    return


def alu():
    return


def alu_b():
    return


def wb():
    return


def print_cycle():
    global cycle
    mark = f"Cycle:{cycle}"
    outcomes = ["-" * 20, mark]
    outcomes += simulator.show_reg()
    outcomes += simulator.show_mem()
    return outcomes


def operate():
    global cycle

    # 周期开始上升沿：处理四个周期的内容
    if_get_instructions()
    issue()
    mem()
    alu()
    alu_b()
    wb()

    # 周期结束上升沿：完成善后工作、buffer清除、占用解除等等

    # 打印每个周期内容
    outcomes = print_cycle()
    return outcomes


def execute(input_filename, simulation_name):
    global finish
    results = []
    simulator.initialization(input_filename)
    while not finish:
        outcome = operate()
        results += outcome
    with open(simulation_name, "w") as f:
        f.writelines("\n".join(results))
    return simulation_name
