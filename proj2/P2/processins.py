# cut string
def line_split(line):
    return [line[:6], line[6:11], line[11:16], line[16:21], line[21:26], line[26:32]]


# processing public parts
def common(ins_split, address, ins):
    return " ".join(ins_split) + "\t" + address + "\t" + ins


# convert to register
def to_register(binary_code):
    return " R" + str(int(binary_code, 2))


# convert to immediate
def to_integer(binary_code):
    return " #" + str(int(binary_code + "00", 2))


def j(line, address, ins):
    ins_split = line_split(line)
    if ins == "J":
        return common(ins_split, address, ins) + to_integer(line[6:])
    else:
        return common(ins_split, address, ins) + to_register(ins_split[1])


def b(line, address, ins):
    ins_split = line_split(line)
    if ins == "BEQ":
        return (
            common(ins_split, address, ins)
            + to_register(ins_split[1])
            + ","
            + to_register(ins_split[2])
            + ","
            + to_integer(line[16:])
        )
    else:
        return (
            common(ins_split, address, ins)
            + to_register(ins_split[1])
            + ","
            + to_integer(line[16:])
        )


def ls(line, address, ins):
    ins_split = line_split(line)
    return (
        common(ins_split, address, ins)
        + to_register(ins_split[2])
        + ", "
        + str(int(line[16:], 2))
        + "("
        + to_register(ins_split[1]).strip()
        + ")"
    )


def op(line, address, ins):
    ins_split = line_split(line)
    return (
        common(ins_split, address, ins)
        + to_register(ins_split[3])
        + ","
        + to_register(ins_split[1])
        + ","
        + to_register(ins_split[2])
    )


def bk(line, address, ins):
    ins_split = line_split(line)
    return common(ins_split, address, ins)


def s(line, address, ins):
    ins_split = line_split(line)
    return (
        common(ins_split, address, ins)
        + to_register(ins_split[3])
        + ","
        + to_register(ins_split[2])
        + ", #"
        + str(int(ins_split[4], 2))
    )


def i(line, address, ins):
    ins_split = line_split(line)
    return (
        common(ins_split, address, ins)
        + to_register(ins_split[2])
        + ","
        + to_register(ins_split[1])
        + ", #"
        + str(int(line[16:], 2))
    )


# binary to decimal
def cb2dec(str_b):
    if str_b.startswith("0"):
        return str(int(str_b, 2))
    else:
        return "-" + str(~(int(str_b[1:], 2) - 0x01) & int("1" * (len(str_b) - 1), 2))


def binary(line, address):
    return line + "\t" + address + "\t" + cb2dec(line)
