from typing import Optional, NamedTuple, Callable, List
import sys
import pathlib
from clang import cindex


class Unsaved(NamedTuple):
    name: str
    content: str


def get_tu(path: str, *cflags: str, unsaved: Optional[List[Unsaved]] = None) -> cindex.TranslationUnit:
    arguments = (
        "-x",
        "c++",
        "-target",
        "x86_64-windows-msvc",
        "-fms-compatibility-version=18",
        "-fdeclspec",
        "-fms-compatibility",
    ) + cflags

    # path of libclang.dll
    cindex.Config.library_path = 'C:\\Program Files\\LLVM\\bin'

    index = cindex.Index.create()
    tu = index.parse(path, arguments, unsaved,
                     cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD |
                     cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

    return tu


def traverse(callback: Callable[[cindex.Cursor], bool], *cursor_path: cindex.Cursor):
    if callback(*cursor_path):
        for child in cursor_path[-1].get_children():
            traverse(callback, *cursor_path, child)


def run():
    # parse header. get TU
    header = pathlib.Path(sys.argv[1])
    print(header, header.exists())

    tu = get_tu(str(header))
    print(tu)

    def print_cursor(*cursor_path: cindex.Cursor):
        indent = '  ' * len(cursor_path)
        cursor = cursor_path[-1]
        print(f'{indent}{cursor.kind}')
        return True
    traverse(print_cursor, tu.cursor)
