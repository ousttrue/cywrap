# Parse and get TranslationUnit

path が parse のエントリポイントとなる。
arguments の与え方で vc の `cl.exe` ようにふるまわせることができる。

```python
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
```

unsaved file はメモリ上のファイルに仮の名前を与えてパースする仕組み。
エディタで未保存のファイルを対象にする他に、
複数のヘッダーを一度にパースしたい場合に
まとめて include する一時ファイルをメモリ上で済ます用途がある。

```c
// unsaved content
#include "a.h"
#include "b.h"
#include "c.h"
```
