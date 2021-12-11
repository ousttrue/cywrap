from clang import cindex
import logging
from .get_tu import get_tu, Unsaved
from .traverse import traverse
logger = logging.getLogger(__name__)


def run():
    logging.basicConfig(level=logging.DEBUG)

    # parse header. get TU
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('entrypoint')
    args = parser.parse_args()
    tu = get_tu(args.entrypoint)

    # traverse
    enums = []
    functions = []
    typedef_struct_list = []

    def filter_imgui(*cursor_path: cindex.Cursor):
        cursor = cursor_path[-1]
        location: cindex.SourceLocation = cursor.location
        if not location:
            return
        if not location.file:
            return

        if location.file.name == args.entrypoint:
            match cursor.kind:
                case cindex.CursorKind.NAMESPACE:
                    # enter namespace
                    # logger.info(f'namespace: {cursor.spelling}')
                    return True
                case (
                    cindex.CursorKind.MACRO_DEFINITION
                    | cindex.CursorKind.MACRO_INSTANTIATION
                    | cindex.CursorKind.INCLUSION_DIRECTIVE
                    | cindex.CursorKind.FUNCTION_TEMPLATE
                    | cindex.CursorKind.CLASS_TEMPLATE
                ):
                    pass
                case cindex.CursorKind.FUNCTION_DECL:
                    if(cursor.spelling.startswith('operator ')):
                        pass
                    else:
                        functions.append(cursor_path)
                case cindex.CursorKind.ENUM_DECL:
                    enums.append(cursor_path)
                case cindex.CursorKind.TYPEDEF_DECL | cindex.CursorKind.STRUCT_DECL:
                    typedef_struct_list.append(cursor_path)
                case _:
                    logger.debug(cursor.kind)
        else:
            pass
            # return True
    traverse(tu, filter_imgui)

    logger.info(
        f'enum: {len(enums)}, typedef/struct: {len(typedef_struct_list)}, function: {len(functions)}')

    # generate
    def get_type(cursor: cindex.Cursor):
        name = cursor.spelling
        return (name, cursor.type.spelling)

    for i, cursor_path in enumerate(enums):
        cursor = cursor_path[-1]
        logger.info(f'enum {cursor.spelling}')

    for i, cursor_path in enumerate(typedef_struct_list):
        cursor = cursor_path[-1]
        match cursor.kind:
            case cindex.CursorKind.TYPEDEF_DECL:
                logger.info(f'typedef {cursor.spelling}')
            case cindex.CursorKind.STRUCT_DECL:
                logger.info(f'struct {cursor.spelling}')

    for i, cursor_path in enumerate(functions):
        cursor = cursor_path[-1]

        result_type = cursor.result_type
        params = [get_type(child) for child in cursor.get_children(
        ) if child.kind == cindex.CursorKind.PARM_DECL]

        logger.debug(
            f'{result_type.spelling} {cursor.spelling}({", ".join(f"{param_type} {param_name}" for param_name, param_type in params)});')

        break
