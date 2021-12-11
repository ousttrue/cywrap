from typing import List, Tuple
import logging
import argparse
import pathlib
import io
import re
import pycindex
from pycindex import cindex


logger = logging.getLogger(__name__)


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


def remove_prefix(values: List[str]):
    def get_prefix(l, r):
        i = 0
        for i in range(len(l)):
            if l[i] != r[i]:
                break
        return l[:i]

    prefix = get_prefix(values[0], values[1])
    for value in values[2:]:
        if not value.startswith(prefix):
            prefix = get_prefix(value, prefix)

    logger.debug(f'prefix: {prefix}')

    return [value[len(prefix):] for value in values]


def upper_snake(s: str):
    return '_'.join(
        re.sub(r"(\s|_|-)+", " ",
               re.sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                      lambda mo: ' ' + mo.group(0).upper(), s)).split())


def generate(w: io.IOBase, tu, functions: List[Tuple[cindex.Cursor, ...]]):
    used = set()
    for f in functions:
        c = f[-1]
        if c.spelling:
            if c.spelling in used:
                continue

            children = []
            for child in c.get_children():
                match child.kind:
                    case cindex.CursorKind.ENUM_CONSTANT_DECL:
                        children.append(child.spelling)

            if len(children) > 1:
                print(c.spelling)
                used.add(c.spelling)

                children = remove_prefix(children)
                children = [upper_snake(child) for child in children]

                name = c.spelling[2:]  # remove prefix CX
                w.write(f'class {name}(BaseEnumeration):\n')
                for child in children:
                    w.write(f'    {child}: ClassVar[{name}]\n')
                w.write('\n')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

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
        w.write('''from typing import ClassVar

class BaseEnumeration(object):
    pass

''')
        generate(w, parser.tu, parser.enums)
