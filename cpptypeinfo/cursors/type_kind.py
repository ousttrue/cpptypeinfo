from clang import cindex
import cpptypeinfo
from cpptypeinfo.usertype import Pointer, TypeRef


def cindex_type_to_cpptypeinfo(t: cindex.Type, c: cindex.Cursor) -> TypeRef:
    if t.kind == cindex.TypeKind.POINTER:
        p = cindex_type_to_cpptypeinfo(t.get_pointee(), c)
        if not p:
            raise Exception(f'unknown type: {t}')
        return TypeRef(Pointer(p), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.TYPEDEF:
        children = [child for child in c.get_children()]
        if len(children) != 1:
            raise Exception(f'unknown children: {children}')
        ref_c = children[0]
        if ref_c.kind != cindex.CursorKind.TYPE_REF:
            raise Exception('not TYPE_REF')
        ref = ref_c.referenced
        return cindex_type_to_cpptypeinfo(ref.underlying_typedef_type, ref)

    # void
    elif t.kind == cindex.TypeKind.VOID:  # void
        return TypeRef(cpptypeinfo.Void(), t.is_const_qualified())
    # int
    elif t.kind == cindex.TypeKind.CHAR_S:  # char
        assert (t.get_size() == 1)
        return TypeRef(cpptypeinfo.Int8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.SCHAR:  # signed char
        assert (t.get_size() == 1)
        return TypeRef(cpptypeinfo.Int8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.SHORT:  # short
        assert (t.get_size() == 2)
        return TypeRef(cpptypeinfo.Int16(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.INT:  # int
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.Int32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.LONG:  # long
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.Int32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.LONGLONG:  # long long
        assert (t.get_size() == 8)
        return TypeRef(cpptypeinfo.Int64(), t.is_const_qualified())
    # unsigned
    elif t.kind == cindex.TypeKind.UCHAR:  # unsigned char
        assert (t.get_size() == 1)
        return TypeRef(cpptypeinfo.UInt8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.WCHAR:  # wchar_t
        assert (t.get_size() == 2)
        return TypeRef(cpptypeinfo.UInt16(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.USHORT:  # unsigned short
        assert (t.get_size() == 2)
        return TypeRef(cpptypeinfo.UInt16(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.UINT:  # unsigned int
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.UInt32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.ULONG:  # unsigned long
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.UInt32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.ULONGLONG:  # unsigned __int64
        assert (t.get_size() == 8)
        return TypeRef(cpptypeinfo.UInt64(), t.is_const_qualified())
    # float
    elif t.kind == cindex.TypeKind.DOUBLE:  # double
        assert (t.get_size() == 8)
        return TypeRef(cpptypeinfo.Double(), t.is_const_qualified())

    # raise Exception(f'unknown type: {t.kind}')
    return None
