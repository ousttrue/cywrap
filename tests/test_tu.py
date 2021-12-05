import unittest
from typing import NamedTuple, Any
import pycindex
from clang import cindex


class Item(NamedTuple):
    cursor_path: Any
    file: str


class TestTU(unittest.TestCase):

    def test_empty_source(self):
        source = '''
'''
        tu = pycindex.get_tu(
            'tmp.h', unsaved=[pycindex.Unsaved('tmp.h', source)])

        items = {}

        def callback(*cursor_path: cindex.Cursor):
            cursor = cursor_path[-1]
            value = items.get(cursor.kind, 0)
            items[cursor.kind] = value + 1
            return True
        pycindex.traverse(tu, callback)

        for k, v in items.items():
            print(k, v)

    def test_function(self):
        source = '''
float func(int a, const char *b = nullptr);
'''

        tu = pycindex.get_tu(
            'tmp.h', unsaved=[pycindex.Unsaved('tmp.h', source)])

        items = []

        def callback(*cursor_path: cindex.Cursor):
            cursor = cursor_path[-1]
            match cursor.location:
                case cindex.SourceLocation() as location:
                    if location.file:
                        # print([x.kind for x in cursor_path], location.file)
                        items.append(cursor_path)
            return True
        pycindex.traverse(tu, callback)
        for item in items:
            print(', '.join([str(c.kind) for c in item]))

        self.assertEqual(5, len(items))
        self.assertEqual('func', items[0][-1].spelling)
        self.assertEqual(cindex.TypeKind.FLOAT, items[0][-1].result_type.kind)
        self.assertEqual('a', items[1][-1].spelling)
        self.assertEqual(cindex.TypeKind.INT, items[1][-1].type.kind)
        self.assertEqual('b', items[2][-1].spelling)
        self.assertTrue(items[2][-1].type.is_const_qualified)
        self.assertEqual(cindex.TypeKind.POINTER, items[2][-1].type.kind)

        pass

    def test_typedef(self):
        source = '''
typedef int INT32;
'''
        tu = pycindex.get_tu(
            'tmp.h', unsaved=[pycindex.Unsaved('tmp.h', source)])

        items = []

        def callback(*cursor_path: cindex.Cursor):
            cursor = cursor_path[-1]
            match cursor.location:
                case cindex.SourceLocation() as location:
                    if location.file:
                        # print([x.kind for x in cursor_path], location.file)
                        items.append(
                            Item([x.kind for x in cursor_path], location.file.name))
            return True
        pycindex.traverse(tu, callback)
        item = items[0]
        self.assertEqual([cindex.CursorKind.TYPEDEF_DECL], item.cursor_path)
        self.assertEqual('tmp.h', item.file)


if __name__ == '__main__':
    unittest.main()
