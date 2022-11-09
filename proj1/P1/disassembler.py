import processins

head = {
    "000010": "J",
    "000100": "BEQ",
    "000001": "BLTZ",
    "000111": "BGTZ",
    "101011": "SW",
    "100011": "LW",
    "011100": "MUL",
}
tail = {
    "001000": "JR",
    "001101": "BREAK",
    "000000": "SLL",
    "000010": "SRL",
    "000011": "SRA",
    "100000": "ADD",
    "100010": "SUB",
    "100100": "AND",
    "100111": "NOR",
    "101010": "SLT",
}
immediate = {
    "110000": "ADD",
    "110001": "SUB",
    "100001": "MUL",
    "110010": "AND",
    "110011": "NOP",
    "110101": "SLT",
}


def instructions_process(line, address):
    """
    Processing instructions
    :param line: binary string
    :param address: address string
    :return: result after disassembly
    """
    break_flag = 0
    result = ""
    h_index = line[:6]
    t_index = line[-6:]
    if "1" not in line:
        result = "NOP"
    elif h_index in head:
        if head[h_index] in ["J"]:
            result = processins.j(line, address, head[h_index])
        elif head[h_index] in ["BEQ", "BLTZ", "BGTZ"]:
            result = processins.b(line, address, head[h_index])
        elif head[h_index] in ["SW", "LW"]:
            result = processins.ls(line, address, head[h_index])
        else:
            result = processins.op(line, address, head[h_index])
    elif t_index in tail:
        if tail[t_index] in ["JR"]:
            result = processins.j(line, address, tail[t_index])
        elif tail[t_index] in ["BREAK"]:
            result = processins.bk(line, address, tail[t_index])
            break_flag = 1
        elif tail[t_index] in ["SLL", "SRL", "SRA"]:
            result = processins.s(line, address, tail[t_index])
        else:
            result = processins.op(line, address, tail[t_index])
    else:
        result = processins.i(line, address, immediate[h_index])
    return result, break_flag


def integers_process(line, address):
    """
    Processing complement
    :param line: binary string
    :param address: address string
    :return: result after disassembly
    """
    result = processins.binary(line, address)
    return result


def process(filename):
    """
    Read the binary string by line, judge whether it is an instruction or complement,
    and process it accordingly.
    :param filename: file containing binary strings
    :return: generate disassembly file, return filename
    """
    assembly_name = "disassembly.txt"
    break_flag = 0
    address = 64
    results = []
    with open(filename, "r") as f:
        for line in f.readlines():
            if not break_flag:
                result, break_flag = instructions_process(line.strip(), str(address))
                results.append(result)
            else:
                result = integers_process(line.strip(), str(address))
                results.append(result)
            address += 4
    with open(assembly_name, "w") as f:
        f.writelines("\n".join(results))
    return assembly_name
