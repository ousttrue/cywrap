from clang import cindex
from typing import List, Optional, NamedTuple
import sys
import pathlib
from clang import cindex


class Unsaved(NamedTuple):
    name: str
    content: str


def get_tu(path: str, cflags: List[str], *, unsaved: Optional[List[Unsaved]] = None) -> cindex.TranslationUnit:
    arguments = [
        "-x",
        "c++",
        "-target",
        "x86_64-windows-msvc",
        "-fms-compatibility-version=18",
        "-fdeclspec",
        "-fms-compatibility",
    ] + cflags

    # path of libclang.dll
    cindex.Config.library_path = 'C:\\Program Files\\LLVM\\bin'

    index = cindex.Index.create()
    tu = index.parse(path, arguments, unsaved,
                     cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD |
                     cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

    return tu


def run():
    # parse header. get TU
    header = pathlib.Path(sys.argv[1])
    print(header, header.exists())

    tu = get_tu(str(header), [])
    print(tu)
