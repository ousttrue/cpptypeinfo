import cpptypeinfo
from typing import List
from clang import cindex


def parse_param(c: cindex.Cursor) -> cpptypeinfo.Param:
    tokens = [x.spelling for x in c.get_tokens()]
    default_value = ''
    for i, token in enumerate(tokens):
        if token == '=':
            default_value = ''.join(tokens[i + 1:])
            break

    decl = cpptypeinfo.parse(c.type.spelling)
    name = c.spelling
    # for child in c.get_children():
    #     if child.kind == cindex.CursorKind.TYPE_REF:
    #         pass
    #     elif child.kind == cindex.CursorKind.UNEXPOSED_EXPR:
    #         # default param assignment
    #         children = [x for x in child.get_children()]
    #         assert (len(children) == 1)
    #         # decl = cpptypeinfo.parse(child.type.spelling)
    #         # childchild = children[0]
    #         # assert (childchild.kind == cindex.CursorKind.INTEGER_LITERAL)
    #         # default_value = get_value()
    #     elif child.kind == cindex.CursorKind.INTEGER_LITERAL:
    #         pass
    #         # default_value = get_value()
    #     elif child.kind == cindex.CursorKind.FLOATING_LITERAL:
    #         pass
    #         # default_value = get_value()
    #     elif child.kind == cindex.CursorKind.CXX_BOOL_LITERAL_EXPR:
    #         pass
    #         # default_value = get_value()
    #     elif child.kind == cindex.CursorKind.UNARY_OPERATOR:
    #         # negative value
    #         pass
    #     else:
    #         raise NotImplementedError(f'{child.kind}')
    return cpptypeinfo.Param(decl, name, default_value)


def traverse(c, level=''):
    print(f'{level}{c.kind}=>{c.spelling}: {c.type.kind}=>{c.type.spelling}')
    for child in c.get_children():
        traverse(child, level + '  ')


def parse_function(c: cindex.Cursor) -> cpptypeinfo.Function:
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
        else:
            raise NotImplementedError(f'{child.kind}')

    return cpptypeinfo.Function(result, params)


def parse_enum(c: cindex.Cursor):
    name = c.spelling
    values = []
    for child in c.get_children():
        if child.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
            values.append(
                cpptypeinfo.EnumValue(child.spelling, child.enum_value))
        else:
            raise Exception(f'{child.kind}')
    return cpptypeinfo.Enum(name, values)


def parse_struct(c: cindex.Cursor):
    decl: cpptypeinfo.Struct = cpptypeinfo.parse(f'struct {c.spelling}')
    cpptypeinfo.push_namespace(decl)
    for child in c.get_children():
        if child.kind == cindex.CursorKind.FIELD_DECL:
            field = cpptypeinfo.parse(child.type.spelling)
            decl.add_field(cpptypeinfo.Field(field, child.spelling))
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


def parse_cursor(c: cindex.Cursor):
    if c.kind == cindex.CursorKind.UNEXPOSED_DECL:
        # tokens = [t.spelling for t in c.get_tokens()]
        pass
    elif c.kind == cindex.CursorKind.UNION_DECL:
        return parse_struct(c)
    elif c.kind == cindex.CursorKind.STRUCT_DECL:
        return parse_struct(c)

    elif c.kind == cindex.CursorKind.TYPEDEF_DECL:
        decl = cpptypeinfo.parse(c.underlying_typedef_type.spelling)
        return cpptypeinfo.Typedef(c.spelling, decl)

    elif c.kind == cindex.CursorKind.FUNCTION_DECL:
        f = parse_function(c)
        cpptypeinfo.STACK[-1].functions[c.spelling] = f
        return f

    elif c.kind == cindex.CursorKind.ENUM_DECL:
        return parse_enum(c)

    elif c.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
        return None

    elif c.kind == cindex.CursorKind.CLASS_TEMPLATE:
        return parse_struct(c)

    else:
        raise NotImplementedError(str(c.kind))


def parse_namespace(c: cindex.Cursor, files: List[str]):
    for i, child in enumerate(c.get_children()):
        if child.location.file.name not in files:
            continue

        if child.kind == cindex.CursorKind.NAMESPACE:
            # nested
            cpptypeinfo.push_namespace(child.spelling)
            parse_namespace(child, files)
            cpptypeinfo.pop_namespace()
        else:

            parse_cursor(child)
