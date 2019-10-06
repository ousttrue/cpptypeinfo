from typing import Dict, Optional, List, Set
import pathlib
from clang import cindex
import cpptypeinfo
from cpptypeinfo.usertype import (TypeRef, Typedef, Pointer, Array, UserType,
                                  Struct, Field, Function, Param, Enum,
                                  EnumValue)


def get_primitive_type(t: cindex.Type) -> Optional[TypeRef]:
    # void
    if t.kind == cindex.TypeKind.VOID:  # void
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

    return None


class DeclMap:
    def __init__(self, parser: cpptypeinfo.TypeParser, files):
        self.parser = parser
        self.decl_map: Dict[int, UserType] = {}
        self.used: Set[int] = set()
        self.files = files
        self.extern_c: List[bool] = [False]

    def get(self, hash: int):
        return self.decl_map.get(hash)

    def add(self, hash: int, usertype: UserType) -> None:
        self.decl_map[hash] = usertype

    def parse_namespace(self, c: cindex.Cursor):
        for i, child in enumerate(c.get_children()):
            if child.kind == cindex.CursorKind.NAMESPACE:
                # nested
                self.parser.push_namespace(child.spelling)
                self.parse_namespace(child)
                self.parser.pop_namespace()
            else:

                self.parse_cursor(child)

    def parse_cursor(self, c: cindex.Cursor):
        if c.hash in self.used:
            return
        self.used.add(c.hash)
        # if files and pathlib.Path(c.location.file.name) not in files:
        #     return

        if c.kind == cindex.CursorKind.UNEXPOSED_DECL:
            extern_c = False
            try:
                it = c.get_tokens()
                t0 = next(it)
                t1 = next(it)
                if t0.spelling == 'extern' and t1.spelling == '"C"':
                    extern_c = True
            except StopIteration:
                pass
            # tokens = [t.spelling for t in ]
            # if len(tokens) >= 2 and tokens[0] == 'extern' and tokens[1] == '"C"':
            # if 'dllexport' in tokens:
            #     a = 0
            if extern_c:
                self.extern_c.append(True)
            for child in c.get_children():
                self.parse_cursor(child)
            if extern_c:
                self.extern_c.pop()

        elif c.kind == cindex.CursorKind.UNION_DECL:
            self.parse_struct(c)

        elif c.kind == cindex.CursorKind.STRUCT_DECL:
            self.parse_struct(c)

        elif c.kind == cindex.CursorKind.CLASS_DECL:
            self.parse_struct(c)

        elif c.kind == cindex.CursorKind.TYPEDEF_DECL:
            self.parse_typedef(c)

        elif c.kind == cindex.CursorKind.FUNCTION_DECL:
            self.parse_function(c)

        elif c.kind == cindex.CursorKind.ENUM_DECL:
            self.parse_enum(c)

        elif c.kind == cindex.CursorKind.VAR_DECL:
            # static variable
            pass

        elif c.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
            # enum_type hoge = 0;
            pass

        elif c.kind == cindex.CursorKind.CXX_UNARY_EXPR:
            pass

        # elif c.kind == cindex.CursorKind.CONSTRUCTOR:
        #     pass

        elif c.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
            pass

        elif c.kind == cindex.CursorKind.CLASS_TEMPLATE:
            pass
            # parse_struct(c)

        elif c.kind == cindex.CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
            pass

        else:
            tokens = [x.spelling for x in c.get_tokens()]
            raise NotImplementedError(f'{c.kind}: {tokens}')

    def cindex_type_to_cpptypeinfo(self, t: cindex.Type,
                                   c: cindex.Cursor) -> TypeRef:
        primitive = get_primitive_type(t)
        if primitive:
            return primitive

        p = self.get_pointer_type(t, c)
        if p:
            return p

        a = self.get_array_type(t, c)
        if a:
            return a

        elif t.kind == cindex.TypeKind.TYPEDEF:
            children = [child for child in c.get_children()]
            for child in children:
                if child.kind == cindex.CursorKind.TYPE_REF:
                    ref = child.referenced
                    decl = self.get(ref.hash)
                    if decl:
                        return decl

                    raise Exception()

            # ref = ref_c.referenced
            # return cindex_type_to_cpptypeinfo(ref.underlying_typedef_type, ref)
            raise Exception()

        elif t.kind == cindex.TypeKind.ELABORATED:
            children = [child for child in c.get_children()]
            for child in children:
                if child.kind == cindex.CursorKind.STRUCT_DECL:
                    decl = self.get(child.hash)
                    if decl:
                        return decl

            raise Exception()

        # elif t.kind == cindex.TypeKind.FUNCTIONPROTO:
        #     children = [child for child in c.get_children()]
        #     child0 = children[0]
        #     if child0.kind != cindex.CursorKind.TYPE_REF:
        #         raise Exception()
        #     result = self.get(child0.referenced.hash)

        #     def to_param(child):
        #         decl = self.cindex_type_to_cpptypeinfo(child.type, child)
        #         ref = TypeRef(decl, child.type.is_const_qualified())
        #         return Param(child.spelling, ref)

        #     params = [to_param(child) for child in children[1:]]
        #     return TypeRef(Function(result, params))

        raise Exception(f'unknown type: {t.kind}')
        return None

    def get_pointer_inner_type(self, p: cindex.Type,
                               c: cindex.Cursor) -> Optional[TypeRef]:
        primitive = get_primitive_type(p)
        if primitive:
            return primitive

        pointer = self.get_pointer_type(p, c)
        if pointer:
            return pointer

        if p.kind == cindex.TypeKind.ELABORATED:
            children = [child for child in c.get_children()]
            for child in children:
                if child.kind == cindex.CursorKind.TYPE_REF:
                    decl = self.get(child.referenced.canonical.hash)
                    if decl:
                        return decl

                    raise Exception()

                elif child.kind in (cindex.CursorKind.STRUCT_DECL,
                                    cindex.CursorKind.ENUM_DECL):
                    decl = self.get(child.hash)
                    if decl:
                        return decl
                    raise Exception()

        elif p.kind == cindex.TypeKind.TYPEDEF:
            children = [child for child in c.get_children()]
            for child in children:
                if child.kind == cindex.CursorKind.TYPE_REF:
                    decl = self.get(child.referenced.hash)
                    if decl:
                        return decl
                    raise Exception()

            raise Exception()

        else:
            raise Exception()

        raise Exception()

    def get_pointer_type(self, t: cindex.Type,
                         c: cindex.Cursor) -> Optional[TypeRef]:
        if (t.kind == cindex.TypeKind.POINTER
                or t.kind == cindex.TypeKind.LVALUEREFERENCE):
            p = self.get_pointer_inner_type(t.get_pointee(), c)
            if p:
                return TypeRef(Pointer(p), t.is_const_qualified())

        return None

    def get_array_type(self, t: cindex.Type,
                       c: cindex.Cursor) -> Optional[TypeRef]:

        if t.kind == cindex.TypeKind.CONSTANTARRAY:
            p = self.get_pointer_inner_type(t.get_array_element_type(), c)
            if p:
                return TypeRef(Array(p, t.get_array_size()),
                               t.is_const_qualified())

        return None

    def parse_typedef(self, c: cindex.Cursor) -> None:
        primitive = get_primitive_type(c.underlying_typedef_type)
        if primitive:
            decl = self.parser.typedef(c.spelling, primitive)
            decl.file = pathlib.Path(c.location.file.name)
            decl.line = c.location.line
            self.add(c.hash, decl)
            return

        if c.underlying_typedef_type.kind in (cindex.TypeKind.POINTER,
                                              cindex.TypeKind.LVALUEREFERENCE):
            primitive = self.get_pointer_type(c.underlying_typedef_type, c)
            if primitive:
                decl = self.parser.typedef(c.spelling, primitive)
                decl.file = pathlib.Path(c.location.file.name)
                decl.line = c.location.line
                self.add(c.hash, decl)
                return

        if c.underlying_typedef_type.kind == cindex.TypeKind.ELABORATED:
            children = [child for child in c.get_children()]
            for child in children:
                if child.kind in [
                        cindex.CursorKind.STRUCT_DECL,
                        cindex.CursorKind.UNION_DECL,
                ]:
                    struct = self.get(child.hash)
                    if struct:
                        decl = self.parser.typedef(c.spelling, struct)
                        decl.file = pathlib.Path(c.location.file.name)
                        decl.line = c.location.line
                        self.add(c.hash, decl)
                        return

                    raise Exception()
                if child.kind == cindex.CursorKind.ENUM_DECL:
                    enum = self.get(child.hash)
                    if enum:
                        decl = self.parser.typedef(c.spelling, enum)
                        decl.file = pathlib.Path(c.location.file.name)
                        decl.line = c.location.line
                        self.add(c.hash, decl)
                        return
            #     if child.kind == cindex.CursorKind.TYPE_REF:
            #         decl = self.get(child.referenced.hash)
            #         if decl:
            #             return decl
            #         raise Exception()
            raise Exception()

        if c.underlying_typedef_type.kind == cindex.TypeKind.TYPEDEF:
            children = [child for child in c.get_children()]
            for child in children:
                if child.kind == cindex.CursorKind.TYPE_REF:
                    typedef = self.get(child.referenced.hash)
                    if typedef:
                        decl = self.parser.typedef(c.spelling, typedef)
                        decl.file = pathlib.Path(c.location.file.name)
                        decl.line = c.location.line
                        self.add(c.hash, decl)
                        return

            raise Exception()

        raise Exception()

        t = self.cindex_type_to_cpptypeinfo(c.underlying_typedef_type, c)
        if not t:
            tokens = [t.spelling for t in c.get_tokens()]
            raise Exception(
                f'unknown type: {c.underlying_typedef_type.kind}: {tokens}')

        # tokens = [t.spelling for t in c.get_tokens()]
        # if not tokens:
        #     return None
        # elif tokens[-1] == ')' or c.underlying_typedef_type.spelling != 'int':
        #     parsed = self.parser.parse(c.underlying_typedef_type.spelling)
        # else:
        #     # int type may be wrong.
        #     # workaround
        #     end = -1
        #     for i, t in enumerate(tokens):
        #         if t == '{':
        #             end = i
        #             break
        #     parsed = self.parser.parse(' '.join(tokens[1:end]))
        # if not parsed:
        #     return

    def parse_enum(self, c: cindex.Cursor) -> Enum:
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
        self.parser.get_current_namespace().register_type(name, decl)
        decl.file = pathlib.Path(c.location.file.name)
        decl.line = c.location.line
        self.add(c.hash, decl)
        return decl

    def parse_function(self, c: cindex.Cursor) -> Function:
        result = self.cindex_type_to_cpptypeinfo(c.result_type, c)

        params = []
        for child in c.get_children():
            if child.kind == cindex.CursorKind.PARM_DECL:
                param = self.cindex_type_to_cpptypeinfo(child.type, child)
                # ToDo:
                default_value = ''
                params.append(Param(param, c.spelling, default_value))

            elif child.kind == cindex.CursorKind.TYPE_REF:
                pass
            elif child.kind == cindex.CursorKind.UNEXPOSED_ATTR:
                # macro
                # tokens = [token.spelling for token in child.get_tokens()]
                pass
            # elif child.kind == cindex.CursorKind.UNEXPOSED_EXPR:
            #     pass

            elif child.kind == cindex.CursorKind.COMPOUND_STMT:
                # function body
                pass

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
        self.parser.get_current_namespace().functions.append(decl)
        decl.name = c.spelling
        decl.mangled_name = c.mangled_name
        decl.extern_c = self.extern_c[-1]
        decl.file = pathlib.Path(c.location.file.name)
        decl.line = c.location.line
        return decl

    def parse_struct(self, c: cindex.Cursor) -> Struct:
        name = c.spelling
        # print(f'{name}: {c.hash}')
        decl = Struct(name)
        self.add(c.hash, decl)
        decl.file = pathlib.Path(c.location.file.name)
        decl.line = c.location.line
        self.parser.push_namespace(decl.namespace)
        for child in c.get_children():
            if child.kind == cindex.CursorKind.FIELD_DECL:
                field = self.cindex_type_to_cpptypeinfo(child.type, child)
                if not field:
                    raise Exception()
                offset = child.get_field_offsetof() // 8
                if not decl.template_parameters and offset < 0:
                    # parseに失敗(特定のheaderが見つからないなど)
                    # clang 環境が壊れているかも
                    # VCのプレビュー版とか原因かも
                    # プレビュー版をアンインストールして LLVM を入れたり消したらなおった
                    raise Exception(f'struct {c.spelling}: offset error')
                decl.add_field(Field(field, child.spelling, offset))

            elif child.kind == cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
                pass

            else:
                self.parse_cursor(child)
        self.parser.pop_namespace()
        return decl
