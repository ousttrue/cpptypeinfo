import pathlib
from clang import cindex
from cpptypeinfo.usertype import Enum, EnumValue
from cpptypeinfo import TypeParser
from .decl_map import DeclMap


def parse_enum(decl_map: DeclMap, parser: TypeParser,
               c: cindex.Cursor) -> Enum:
    name = c.type.spelling
    if not name:
        raise Exception(f'no name')
    values = []
    for child in c.get_children():
        if child.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
            values.append(EnumValue(child.spelling, child.enum_value))
        else:
            raise Exception(f'{child.kind}')
    decl = Enum(name, values)
    parser.get_current_namespace().register_type(name, decl)
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line
    decl_map.add(c.hash, decl)
    return decl
