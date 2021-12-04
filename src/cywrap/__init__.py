import clang
import sys
import pathlib


def run():
    # parse header. get TU
    header = pathlib.Path(sys.argv[1])
    print(header, header.exists())
