from typing import NamedTuple, List, Optional
from clang import cindex


class Unsaved(NamedTuple):
    name: str
    content: str


def get_tu(entrypoint: str,
           *,
           include_dirs: List[str] = None,
           flags: List[str] = None,
           unsaved: Optional[List[Unsaved]] = None) -> cindex.TranslationUnit:
    arguments = [
        "-x",
        "c++",
        "-target",
        "x86_64-windows-msvc",
        "-fms-compatibility-version=18",
        "-fdeclspec",
        "-fms-compatibility",
        "-std=c++17",
    ]
    if include_dirs:
        arguments.extend(f'-I{i}' for i in include_dirs)
    if flags:
        arguments.extend(flags)

    # path of libclang.dll
    cindex.Config.library_path = 'C:\\Program Files\\LLVM\\bin'

    index = cindex.Index.create()

    tu = index.parse(entrypoint, arguments, unsaved,
                     cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD |
                     cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

    return tu
