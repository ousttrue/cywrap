from clang import cindex
from .get_tu import get_tu, Unsaved
from .traverse import traverse


def run():
    # parse header. get TU
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('entrypoint')
    args = parser.parse_args()
    tu = get_tu(args.entrypoint)

    # traverse
    functions = []

    def filter_imgui(*cursor_path: cindex.Cursor):
        cursor = cursor_path[-1]
        location: cindex.SourceLocation = cursor.location
        if not location:
            return
        if not location.file:
            return

        if location.file.name == args.entrypoint:
            if cursor.kind == cindex.CursorKind.FUNCTION_DECL:
                functions.append(cursor_path)

        return True
    traverse(tu, filter_imgui)

    # generate
    for i, cursor_path in enumerate(functions):
        kinds = ', '.join(str(cursor.kind) for cursor in cursor_path)
        print(f'{i}: {kinds}: {cursor_path[-1].spelling}')
