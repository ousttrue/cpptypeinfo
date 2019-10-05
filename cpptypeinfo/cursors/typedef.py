from typing import Optional
import pathlib
import cpptypeinfo
from cpptypeinfo.usertype import Typedef, Pointer
from clang import cindex


def get_type_from_kind(t: cindex.Type):
    if t.kind == cindex.TypeKind.POINTER:
        p = get_type_from_kind(t.get_pointee())
        return Pointer(p)
    elif t.kind == cindex.TypeKind.CHAR_S:  # char
        return cpptypeinfo.Int8()
    elif t.kind == cindex.TypeKind.SCHAR:  # signed char
        return cpptypeinfo.Int8()
    elif t.kind == cindex.TypeKind.SHORT:  # short
        return cpptypeinfo.Int16()
    elif t.kind == cindex.TypeKind.INT:  # int
        return cpptypeinfo.Int32()
    elif t.kind == cindex.TypeKind.LONGLONG:  # long long
        return cpptypeinfo.Int64()
    # unsigned
    elif t.kind == cindex.TypeKind.UCHAR:  # unsigned char
        return cpptypeinfo.UInt8()
    elif t.kind == cindex.TypeKind.USHORT:  # unsigned short
        return cpptypeinfo.UInt16()
    elif t.kind == cindex.TypeKind.UINT:  # unsigned int
        return cpptypeinfo.UInt32()
    elif t.kind == cindex.TypeKind.ULONGLONG:  # unsigned __int64
        return cpptypeinfo.UInt64()

    return None


def parse_typedef(parser: cpptypeinfo.TypeParser,
                  c: cindex.Cursor) -> Optional[Typedef]:
    t = get_type_from_kind(c.underlying_typedef_type)
    if not t:
        tokens = [t.spelling for t in c.get_tokens()]
        raise Exception(
            f'unknown type: {c.underlying_typedef_type.kind}: {tokens}')

    decl = parser.typedef(c.spelling, t)
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line
    return decl

    # tokens = [t.spelling for t in c.get_tokens()]
    # if not tokens:
    #     return None
    # elif tokens[-1] == ')' or c.underlying_typedef_type.spelling != 'int':
    #     parsed = parser.parse(c.underlying_typedef_type.spelling)
    # else:
    #     # int type may be wrong.
    #     # workaround
    #     end = -1
    #     for i, t in enumerate(tokens):
    #         if t == '{':
    #             end = i
    #             break
    #     parsed = parser.parse(' '.join(tokens[1:end]))
    # if not parsed:
    #     return
