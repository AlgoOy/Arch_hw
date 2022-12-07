import sys
import getfilename
import disassembler
import simulator
import scoreboarding

if __name__ == "__main__":
    """
    Get filename using command line arguments
    Disassemble the binary code
    Simulate assembly code
    """
    input_filename, output_filename = getfilename.get_from_argv(sys.argv)
    assembly_name = disassembler.process(input_filename)
    # simulator.execute(assembly_name, output_filename)

    # 测试输出模块
    simulator.initialization(assembly_name)
    results = scoreboarding.print_cycle()
    with open(output_filename, "w") as f:
        f.writelines("\n".join(results))
