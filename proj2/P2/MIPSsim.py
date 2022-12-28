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
    scoreboarding.execute(assembly_name, output_filename)

    # 测试输出模块

    # scoreboarding.initialization(assembly_name)
    # results = []
    # for i in range(10):
    #
    #     scoreboarding.if_get_i_()
    #     scoreboarding.issue_()
    #     scoreboarding.alu_b_()
    #     scoreboarding.alu_()
    #     scoreboarding.mem_()
    #     scoreboarding.wb_()
    #     scoreboarding.if_finish()
    #     scoreboarding.issue_finish()
    #     scoreboarding.deal_finish()
    #     results += scoreboarding.print_cycle()
    #
    # with open(output_filename, "w") as f:
    #     f.writelines("\n".join(results))
