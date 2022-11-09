import sys
import getfilename
import disassembler
import simulator

if __name__ == "__main__":
    """
    Get filename using command line arguments
    Disassemble the binary code
    Simulate assembly code
    """
    filename = getfilename.get_from_argv(sys.argv)
    assembly_name = disassembler.process(filename)
    simulator.execute(assembly_name)
