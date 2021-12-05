from typing import Callable
from clang import cindex


def _traverse(callback: Callable[[cindex.Cursor], bool], *cursor_path: cindex.Cursor):
    if callback(*cursor_path):
        for child in cursor_path[-1].get_children():
            _traverse(callback, *cursor_path, child)


def traverse(tu: cindex.TranslationUnit, callback: Callable[[cindex.Cursor], bool]):
    for child in tu.cursor.get_children():
        _traverse(callback, child)
