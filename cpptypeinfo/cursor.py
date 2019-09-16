import pathlib
from typing import List
from clang import cindex
import cpptypeinfo


def parse_param(c: cindex.Cursor) -> cpptypeinfo.Param:
    tokens = [x.spelling for x in c.get_tokens()]
    default_value = ''
    for i, token in enumerate(tokens):
        if token == '=':
            default_value = ''.join(tokens[i + 1:])
            break

    parsed = cpptypeinfo.parse(c.type.spelling)
    return cpptypeinfo.Param(parsed, c.spelling, default_value)


def traverse(c, level=''):
    print(f'{level}{c.kind}=>{c.spelling}: {c.type.kind}=>{c.type.spelling}')
    for child in c.get_children():
        traverse(child, level + '  ')


def parse_function(c: cindex.Cursor, extern_c: bool) -> cpptypeinfo.Function:
    params = []
    result = cpptypeinfo.parse(c.result_type.spelling)
    for child in c.get_children():
        if child.kind == cindex.CursorKind.TYPE_REF:
            pass
        elif child.kind == cindex.CursorKind.UNEXPOSED_ATTR:
            # macro
            # tokens = [token.spelling for token in child.get_tokens()]
            pass
        elif child.kind == cindex.CursorKind.PARM_DECL:
            params.append(parse_param(child))
            # traverse(child)
            pass
        elif child.kind == cindex.CursorKind.COMPOUND_STMT:
            # function body
            pass
        elif child.kind == cindex.CursorKind.DLLEXPORT_ATTR:
            pass
        else:
            raise NotImplementedError(f'{child.kind}')

    decl = cpptypeinfo.Function(result, params)
    decl.name = c.spelling
    decl.extern_c = extern_c
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line
    return decl


def parse_enum(c: cindex.Cursor):
    name = c.spelling
    values = []
    for child in c.get_children():
        if child.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
            values.append(
                cpptypeinfo.EnumValue(child.spelling, child.enum_value))
        else:
            raise Exception(f'{child.kind}')
    decl = cpptypeinfo.Enum(name, values)
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line
    return decl


def parse_struct(c: cindex.Cursor):
    decl: cpptypeinfo.Struct = cpptypeinfo.parse(f'struct {c.spelling}').ref
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line
    if isinstance(decl, cpptypeinfo.Typedef):
        decl = decl.src
    cpptypeinfo.push_namespace(decl)
    for child in c.get_children():
        if child.kind == cindex.CursorKind.FIELD_DECL:
            field = cpptypeinfo.parse(child.type.spelling)
            offset = child.get_field_offsetof() // 8
            decl.add_field(cpptypeinfo.Field(field, child.spelling, offset))
        elif child.kind == cindex.CursorKind.CONSTRUCTOR:
            pass
        elif child.kind == cindex.CursorKind.DESTRUCTOR:
            pass
        elif child.kind == cindex.CursorKind.CXX_METHOD:
            pass
        elif child.kind == cindex.CursorKind.CONVERSION_FUNCTION:
            pass
        elif child.kind == cindex.CursorKind.TEMPLATE_TYPE_PARAMETER:
            decl.add_template_parameter(child.spelling)
        elif child.kind == cindex.CursorKind.VAR_DECL:
            # static variable
            pass
        elif child.kind == cindex.CursorKind.UNION_DECL:
            # ToDo
            pass
        elif child.kind == cindex.CursorKind.STRUCT_DECL:
            parse_struct(child)
        elif child.kind == cindex.CursorKind.TYPEDEF_DECL:
            typedef_decl = cpptypeinfo.parse(
                child.underlying_typedef_type.spelling)
            cpptypeinfo.Typedef(child.spelling, typedef_decl)
        else:
            raise NotImplementedError(f'{child.kind}')
    cpptypeinfo.pop_namespace()
    return decl


def parse_typedef(c: cindex.Cursor):
    tokens = [t.spelling for t in c.get_tokens()]
    if tokens[-1] == ')' or c.underlying_typedef_type.spelling != 'int':
        parsed = cpptypeinfo.parse(c.underlying_typedef_type.spelling)
    else:
        # int type may be wrong.
        # workaround
        end = -1
        for i, t in enumerate(tokens):
            if t == '{':
                end = i
                break
        parsed = cpptypeinfo.parse(' '.join(tokens[1:end]))
    decl = cpptypeinfo.Typedef(c.spelling, parsed)
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line


def parse_cursor(c: cindex.Cursor, files: List[pathlib.Path], extern_c=False):
    if pathlib.Path(c.location.file.name) not in files:
        return

    if c.kind == cindex.CursorKind.UNEXPOSED_DECL:
        # try:
        #     it = c.get_tokens()
        #     t0 = next(it)
        #     t1 = next(it)
        #     if t0.spelling == 'extern' and t1.spelling == '"C"':
        #         extern_c = True
        # except StopIteration:
        #     pass
        # tokens = [t.spelling for t in ]
        # if len(tokens) >= 2 and tokens[0] == 'extern' and tokens[1] == '"C"':
        # if 'dllexport' in tokens:
        #     a = 0
        for child in c.get_children():
            parse_cursor(child, files, extern_c)

    elif c.kind == cindex.CursorKind.UNION_DECL:
        parse_struct(c)

    elif c.kind == cindex.CursorKind.STRUCT_DECL:
        parse_struct(c)

    elif c.kind == cindex.CursorKind.TYPEDEF_DECL:
        parse_typedef(c)

    elif c.kind == cindex.CursorKind.FUNCTION_DECL:
        parse_function(c, extern_c)

    elif c.kind == cindex.CursorKind.ENUM_DECL:
        parse_enum(c)

    elif c.kind == cindex.CursorKind.VAR_DECL:
        # static variable
        pass

    elif c.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
        pass

    elif c.kind == cindex.CursorKind.CLASS_TEMPLATE:
        parse_struct(c)

    else:
        raise NotImplementedError(str(c.kind))


def parse_namespace(c: cindex.Cursor, files: List[pathlib.Path]):
    for i, child in enumerate(c.get_children()):
        if child.kind == cindex.CursorKind.NAMESPACE:
            # nested
            cpptypeinfo.push_namespace(child.spelling)
            parse_namespace(child, files)
            cpptypeinfo.pop_namespace()
        else:

            parse_cursor(child, files)
