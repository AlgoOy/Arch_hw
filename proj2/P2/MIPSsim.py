import sys
import getfilename
import disassembler
import scoreboarding

if __name__ == "__main__":
    """
    Get filename using command line arguments
    Disassemble the binary code
    Simulate assembly code
    """
    input_filename, output_filename = getfilename.get_from_argv(sys.argv)
    assembly_name = disassembler.process(input_filename)
    # scoreboarding.execute(assembly_name, output_filename)

    # 测试输出模块

    scoreboarding.initialization(assembly_name)
    results = []
    for i in range(10):
        # scoreboarding.make_true()
        # scoreboarding.wb_()
        # scoreboarding.mem_()
        # scoreboarding.alu_()
        # scoreboarding.alu_b_()
        # scoreboarding.issue_()
        # scoreboarding.if_get_i_()
``
        # scoreboarding.make_true()
        scoreboarding.if_get_i_()
        if i > 0:
            scoreboarding.issue_()
        if i > 1:
            scoreboarding.alu_b_()
            scoreboarding.alu_()
            scoreboarding.mem_()
        if i > 2:
            scoreboarding.wb_()
`
        results += scoreboarding.print_cycle()
    with open(output_filename, "w") as f:
        f.writelines("\n".join(results))
