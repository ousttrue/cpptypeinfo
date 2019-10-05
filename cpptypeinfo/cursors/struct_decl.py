from typing import Optional
import pathlib
from clang import cindex
import cpptypeinfo
from cpptypeinfo.usertype import Struct


def parse_struct(parser: cpptypeinfo.TypeParser,
                 c: cindex.Cursor) -> Optional[Struct]:
    name = c.spelling
    if not name:
        # anonymous
        return None
    decl = parser.parse(f'struct {name}').ref
    if not isinstance(decl, Struct):
        if isinstance(decl, Typedef):
            decl = decl.typeref.ref
    if not isinstance(decl, Struct):
        raise Exception('not struct')
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line
    # if isinstance(decl, Typedef):
    #     decl = decl.src
    parser.push_namespace(decl.namespace)
    for child in c.get_children():
        if child.kind == cindex.CursorKind.UNION_DECL:
            # ToDo
            pass
        #     if child.kind == cindex.CursorKind.FIELD_DECL:
        #         field = parser.parse(child.type.spelling)
        #         offset = child.get_field_offsetof() // 8
        #         if not decl.template_parameters and offset < 0:
        #             # parseに失敗(特定のheaderが見つからないなど)
        #             # clang 環境が壊れているかも
        #             # VCのプレビュー版とか原因かも
        #             # プレビュー版をアンインストールして LLVM を入れたり消したらなおった
        #             raise Exception(f'struct {c.spelling}: offset error')
        #         decl.add_field(Field(field, child.spelling, offset))
        #     elif child.kind == cindex.CursorKind.CONSTRUCTOR:
        #         pass
        #     elif child.kind == cindex.CursorKind.DESTRUCTOR:
        #         pass
        #     elif child.kind == cindex.CursorKind.CXX_METHOD:
        #         pass
        #     elif child.kind == cindex.CursorKind.CONVERSION_FUNCTION:
        #         pass
        #     elif child.kind == cindex.CursorKind.TEMPLATE_TYPE_PARAMETER:
        #         t = child.spelling
        #         parser.parse(f'struct {t}')
        #         decl.add_template_parameter(t)
        #     elif child.kind == cindex.CursorKind.VAR_DECL:
        #         # static variable
        #         pass
        #     elif child.kind == cindex.CursorKind.STRUCT_DECL:
        #         parse_struct(parser, child)
        #     elif child.kind == cindex.CursorKind.TYPEDEF_DECL:
        #         typedef_decl = parser.parse(child.underlying_typedef_type.spelling)
        #         parser.typedef(child.spelling, typedef_decl)
        #     elif child.kind == cindex.CursorKind.UNEXPOSED_ATTR:
        #         pass
        #     elif child.kind == cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
        #         pass
        else:
            raise NotImplementedError(f'{child.kind}')
    parser.pop_namespace()
    return decl
