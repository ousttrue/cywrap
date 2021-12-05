from typing import NamedTuple, List, Optional
from clang import cindex


class Unsaved(NamedTuple):
    name: str
    content: str


def get_tu(entrypoint: str,
           *,
           includes: List[str] = None,
           unsaved: Optional[List[Unsaved]] = None) -> cindex.TranslationUnit:
    arguments = [
        "-x",
        "c++",
        "-target",
        "x86_64-windows-msvc",
        "-fms-compatibility-version=18",
        "-fdeclspec",
        "-fms-compatibility",
    ]
    if includes:
        arguments.extend(f'-I{i}' for i in includes)

    # path of libclang.dll
    cindex.Config.library_path = 'C:\\Program Files\\LLVM\\bin'

    index = cindex.Index.create()

    tu = index.parse(entrypoint, arguments, unsaved,
                     cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD |
                     cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

    return tu
