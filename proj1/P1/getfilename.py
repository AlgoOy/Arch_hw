import sys


def get_from_argv(argv):
    """
    get filename from command line arguments
    usage: python main.py [filename]
    :param argv:a list with all command line arguments
    :return:filename
    """
    if len(argv) != 2:
        print("usage: python main.py [filename]")
        sys.exit()
    return argv[1]
