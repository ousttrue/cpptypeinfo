from clang import cindex
import cpptypeinfo
from cpptypeinfo.usertype import Pointer, TypeRef


def cindex_type_to_cpptypeinfo(t: cindex.Type) -> TypeRef:
    if t.kind == cindex.TypeKind.POINTER:
        p = cindex_type_to_cpptypeinfo(t.get_pointee())
        if not p:
            raise Exception(f'unknown type: {t}')
        return TypeRef(Pointer(p), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.VOID:  # void
        return TypeRef(cpptypeinfo.Void(), t.is_const_qualified())
    # int
    elif t.kind == cindex.TypeKind.CHAR_S:  # char
        return TypeRef(cpptypeinfo.Int8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.SCHAR:  # signed char
        return TypeRef(cpptypeinfo.Int8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.SHORT:  # short
        return TypeRef(cpptypeinfo.Int16(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.INT:  # int
        return TypeRef(cpptypeinfo.Int32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.LONGLONG:  # long long
        return TypeRef(cpptypeinfo.Int64(), t.is_const_qualified())
    # unsigned
    elif t.kind == cindex.TypeKind.UCHAR:  # unsigned char
        return TypeRef(cpptypeinfo.UInt8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.USHORT:  # unsigned short
        return TypeRef(cpptypeinfo.UInt16(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.UINT:  # unsigned int
        return TypeRef(cpptypeinfo.UInt32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.ULONG:  # unsigned long
        return TypeRef(cpptypeinfo.UInt32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.ULONGLONG:  # unsigned __int64
        return TypeRef(cpptypeinfo.UInt64(), t.is_const_qualified())

    raise Exception(f'unknown type: {t}')
    return None
