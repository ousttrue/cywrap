from typing import List, Tuple
import argparse
import pathlib
import io
import pycindex
from pycindex import cindex


class Parser:
    def __init__(self, entrypoint: str):
        self.entrypoint = entrypoint
        self.tu = pycindex.get_tu(self.entrypoint)
        self.functions = []
        self.enums = []

    def filter(self, *cursor_path: cindex.Cursor):
        cursor = cursor_path[-1]
        location: cindex.SourceLocation = cursor.location
        if not location:
            return False
        if not location.file:
            return False

        if location.file.name == self.entrypoint:
            match cursor.kind:
                case cindex.CursorKind.FUNCTION_DECL:
                    self.functions.append(cursor_path)
                case cindex.CursorKind.ENUM_DECL:
                    self.enums.append(cursor_path)

        return True

    def traverse(self):
        pycindex.traverse(self.tu, self.filter)


def generate(w: io.IOBase, tu, functions: List[Tuple[cindex.Cursor, ...]]):
    used = set()
    for f in functions:
        c = f[-1]
        if c.spelling:
            if c.spelling in used:
                continue
            used.add(c.spelling)
            print(c.spelling)
            w.write(f'class {c.spelling}:\n')
            w.write(f'    pass\n')
            w.write(f'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('dst')
    args = parser.parse_args()

    src = pathlib.Path(args.src).absolute()
    parser = Parser(str(src))
    parser.traverse()

    dst = pathlib.Path(args.dst).absolute()
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open('w') as w:
        generate(w, parser.tu, parser.enums)
