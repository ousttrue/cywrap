from os import path
import setuptools
import pathlib

HERE = pathlib.Path(__file__).parent
SRC_CLANG = HERE / 'src/clang'
SRC_CLANG_BASE_URL = 'https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-13.0.0/clang/bindings/python/clang/'
if not SRC_CLANG.exists():
    SRC_CLANG.mkdir(parents=True)

    def http_get(url_base: str, dst_dir: pathlib.Path, name: str):
        import urllib.request
        req = urllib.request.Request(url_base + name)
        with urllib.request.urlopen(req) as res:
            (dst_dir / name).write_bytes(res.read())

    http_get(SRC_CLANG_BASE_URL, SRC_CLANG, '__init__.py')
    http_get(SRC_CLANG_BASE_URL, SRC_CLANG, 'cindex.py')
    http_get(SRC_CLANG_BASE_URL, SRC_CLANG, 'enumerations.py')

setuptools.setup()
