import sys


def get_from_argv(argv):
    """
    get filename from command line arguments
    usage: python MIPSsim.py [filename]
    :param argv:a list with all command line arguments
    :return:filename
    """
    if len(argv) == 2:
        return argv[1], "simulation.txt"
    if len(argv) != 3:
        print("usage: python MIPSsim.py {inputfilename} [outputfilename]")
        print("\t{inputfilename} is required; [outputfilename] is optional.\n")
        print(
            "When the output file name is not specified, the final output file name defaults to 'simulation.txt'."
        )
        sys.exit()
    return argv[1], argv[2]
