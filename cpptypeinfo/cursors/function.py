import pathlib
from clang import cindex
import cpptypeinfo
from cpptypeinfo.usertype import Param, Function
from .type_kind import cindex_type_to_cpptypeinfo


def parse_param(parser: cpptypeinfo.TypeParser, c: cindex.Cursor) -> Param:
    # tokens = [x.spelling for x in c.get_tokens()]
    # default_value = ''
    # for i, token in enumerate(tokens):
    #     if token == '=':
    #         default_value = ''.join(tokens[i + 1:])
    #         break

    parsed = cindex_type_to_cpptypeinfo(c.type)
    # ToDo:
    default_value = ''
    return Param(parsed, c.spelling, default_value)


def parse_function(parser: cpptypeinfo.TypeParser, c: cindex.Cursor,
                   extern_c: bool) -> Function:
    result = cindex_type_to_cpptypeinfo(c.result_type)

    params = []
    for child in c.get_children():
        if child.kind == cindex.CursorKind.PARM_DECL:
            params.append(parse_param(parser, child))
            pass

        # if child.kind == cindex.CursorKind.TYPE_REF:
        #     pass
        # elif child.kind == cindex.CursorKind.UNEXPOSED_ATTR:
        #     # macro
        #     # tokens = [token.spelling for token in child.get_tokens()]
        #     pass
        # elif child.kind == cindex.CursorKind.UNEXPOSED_EXPR:
        #     pass

        # elif child.kind == cindex.CursorKind.COMPOUND_STMT:
        #     # function body
        #     pass
        # elif child.kind == cindex.CursorKind.DLLEXPORT_ATTR:
        #     # __declspec(dllexport)
        #     pass
        # elif child.kind == cindex.CursorKind.DLLIMPORT_ATTR:
        #     # __declspec(dllimport)
        #     pass
        # elif child.kind == cindex.CursorKind.NAMESPACE_REF:
        #     pass
        # elif child.kind == cindex.CursorKind.TEMPLATE_REF:
        #     pass

        else:
            raise NotImplementedError(f'{child.kind}')

    decl = Function(result, params)
    parser.get_current_namespace().functions.append(decl)
    decl.name = c.spelling
    decl.mangled_name = c.mangled_name
    decl.extern_c = extern_c
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line
    return decl
