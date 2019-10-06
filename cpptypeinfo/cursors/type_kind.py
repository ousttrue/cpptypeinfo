from clang import cindex
import cpptypeinfo
from cpptypeinfo.usertype import Pointer, Array, TypeRef, Function, Param
from .decl_map import DeclMap


def get_basetype(decl_map: DeclMap, t: cindex.Type,
                 c: cindex.Cursor) -> TypeRef:
    p = cindex_type_to_cpptypeinfo(decl_map, t.get_pointee(), c)
    if p:
        return p

    children = [child for child in c.get_children()]
    for child in children:
        if child.kind == cindex.CursorKind.TYPE_REF:
            ref = child.referenced
            p = decl_map.get(ref.hash)
            if p:
                return p
            if ref.kind == cindex.CursorKind.STRUCT_DECL:
                decl = cpptypeinfo.usertype.Struct(ref.spelling)
                decl_map.add(ref.hash, decl)
                return decl
            else:
                raise Exception()

    raise Exception()


def cindex_type_to_cpptypeinfo(decl_map: DeclMap, t: cindex.Type,
                               c: cindex.Cursor) -> TypeRef:
    if t.kind == cindex.TypeKind.POINTER:
        p = get_basetype(decl_map, t, c)
        if p:
            return TypeRef(Pointer(p), t.is_const_qualified())
        raise Exception()

    elif t.kind == cindex.TypeKind.LVALUEREFERENCE:
        p = get_basetype(decl_map, t, c)
        if p:
            return TypeRef(Pointer(p), t.is_const_qualified())
        raise Exception()

    elif t.kind == cindex.TypeKind.CONSTANTARRAY:
        element = cindex_type_to_cpptypeinfo(decl_map,
                                             t.get_array_element_type(), c)
        return TypeRef(Array(element, t.get_array_size()),
                       t.is_const_qualified())

    elif t.kind == cindex.TypeKind.TYPEDEF:
        children = [child for child in c.get_children()]
        for child in children:
            if child.kind == cindex.CursorKind.TYPE_REF:
                decl = decl_map.get(child.referenced.hash)
                if decl:
                    return decl

        # ref = ref_c.referenced
        # return cindex_type_to_cpptypeinfo(ref.underlying_typedef_type, ref)
        raise Exception()

    elif t.kind == cindex.TypeKind.ELABORATED:
        children = [child for child in c.get_children()]
        for child in children:
            if child.kind in [
                    cindex.CursorKind.STRUCT_DECL,
                    cindex.CursorKind.UNION_DECL, cindex.CursorKind.ENUM_DECL
            ]:
                decl = decl_map.get(child.referenced.hash)
                if decl:
                    return decl
            elif child.kind == cindex.CursorKind.TYPE_REF:
                decl = decl_map.get(child.referenced.hash)
                if decl:
                    return decl
            raise Exception(f'unknown type: {child.kind}')
        raise Exception()

    elif t.kind == cindex.TypeKind.FUNCTIONPROTO:
        children = [child for child in c.get_children()]
        child0 = children[0]
        if child0.kind != cindex.CursorKind.TYPE_REF:
            raise Exception()
        result = decl_map.get(child0.referenced.hash)

        def to_param(child):
            decl = cindex_type_to_cpptypeinfo(decl_map, child.type, child)
            ref = TypeRef(decl, child.type.is_const_qualified())
            return Param(child.spelling, ref)

        params = [to_param(child) for child in children[1:]]
        return TypeRef(Function(result, params))

    # void
    elif t.kind == cindex.TypeKind.VOID:  # void
        return TypeRef(cpptypeinfo.Void(), t.is_const_qualified())
    # bool
    elif t.kind == cindex.TypeKind.BOOL:  # void
        assert (t.get_size() == 1)
        return TypeRef(cpptypeinfo.Bool(), t.is_const_qualified())
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
    elif t.kind == cindex.TypeKind.FLOAT:  # float
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.Float(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.DOUBLE:  # double
        assert (t.get_size() == 8)
        return TypeRef(cpptypeinfo.Double(), t.is_const_qualified())

    raise Exception(f'unknown type: {t.kind}')
    return None
