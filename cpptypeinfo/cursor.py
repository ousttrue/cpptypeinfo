import pathlib
from typing import List, Set, Optional
from clang import cindex
from .usertype import (Param, Field, Struct, Function, EnumValue, Enum,
                       Typedef)
from .typeparser import TypeParser
from .get_tu import get_tu, tmp_from_source
from . import cursors


def debug_print(c, files: List[pathlib.Path], level=''):
    if (files and c.location.file
            and pathlib.Path(c.location.file.name) not in files):
        return

    display = c.type.spelling
    if not display:
        if c.kind == cindex.CursorKind.UNEXPOSED_DECL:
            tokens = [x.spelling for x in c.get_tokens()]
            if tokens and tokens[0] == 'extern':
                # https://stackoverflow.com/questions/11865486/clang-ast-extern-linkagespec-issue/12526555#12526555
                display = 'extern "C"'

    if c.kind == cindex.CursorKind.TYPEDEF_DECL:
        children = [child for child in c.get_children()]
        if children:
            text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}=>{children[0].hash}'
        else:
            text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}'
        print(text)

    else:
        extra = ''
        go_children = True

        if c.type.kind == cindex.TypeKind.POINTER:
            p = c.type.get_pointee()
            a = 0

        if c.hash != c.canonical.hash:
            extra = f'[{c.canonical.hash}]'

        if c.kind == cindex.CursorKind.ENUM_DECL:
            go_children = False
        if c.kind == cindex.CursorKind.TYPE_REF:
            extra = f'({c.referenced.hash})'
        else:
            if c.kind == cindex.CursorKind.FUNCTION_DECL:
                # https://clang.llvm.org/doxygen/Index_8h_source.html
                calling_convention = cindex.conf.lib.clang_getFunctionTypeCallingConv(
                    c.type)
                calling_convention = {
                    1: '',
                    2: '(stdcall)',  # 64bit ignored
                    100: '# invalid #'
                }[calling_convention]
                extra = f'({c.result_type.kind}){calling_convention}'
        text = f'{level}({c.hash}){c.kind}=>{extra}{c.spelling}: {c.type.kind}=>{display}'
        print(text)

        if go_children:
            for child in c.get_children():
                debug_print(child, files, level + '  ')


def parse_enum(parser: TypeParser, c: cindex.Cursor) -> Enum:
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
    return decl


def parse_struct(parser: TypeParser, c: cindex.Cursor) -> Optional[Struct]:
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
        if child.kind == cindex.CursorKind.FIELD_DECL:
            field = parser.parse(child.type.spelling)
            offset = child.get_field_offsetof() // 8
            if not decl.template_parameters and offset < 0:
                # parseに失敗(特定のheaderが見つからないなど)
                # clang 環境が壊れているかも
                # VCのプレビュー版とか原因かも
                # プレビュー版をアンインストールして LLVM を入れたり消したらなおった
                raise Exception(f'struct {c.spelling}: offset error')
            decl.add_field(Field(field, child.spelling, offset))
        elif child.kind == cindex.CursorKind.CONSTRUCTOR:
            pass
        elif child.kind == cindex.CursorKind.DESTRUCTOR:
            pass
        elif child.kind == cindex.CursorKind.CXX_METHOD:
            pass
        elif child.kind == cindex.CursorKind.CONVERSION_FUNCTION:
            pass
        elif child.kind == cindex.CursorKind.TEMPLATE_TYPE_PARAMETER:
            t = child.spelling
            parser.parse(f'struct {t}')
            decl.add_template_parameter(t)
        elif child.kind == cindex.CursorKind.VAR_DECL:
            # static variable
            pass
        elif child.kind == cindex.CursorKind.UNION_DECL:
            # ToDo
            pass
        elif child.kind == cindex.CursorKind.STRUCT_DECL:
            parse_struct(parser, child)
        elif child.kind == cindex.CursorKind.TYPEDEF_DECL:
            typedef_decl = parser.parse(child.underlying_typedef_type.spelling)
            parser.typedef(child.spelling, typedef_decl)
        elif child.kind == cindex.CursorKind.UNEXPOSED_ATTR:
            pass
        elif child.kind == cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
            pass
        else:
            raise NotImplementedError(f'{child.kind}')
    parser.pop_namespace()
    return decl


def parse_cursor(parser: TypeParser,
                 c: cindex.Cursor,
                 files: List[pathlib.Path],
                 used: Set[int],
                 extern_c=False):
    if c.hash in used:
        return
    used.add(c.hash)
    if files and pathlib.Path(c.location.file.name) not in files:
        return

    if c.kind == cindex.CursorKind.UNEXPOSED_DECL:
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
        for child in c.get_children():
            parse_cursor(parser,
                         child,
                         files=files,
                         used=used,
                         extern_c=extern_c)

    # elif c.kind == cindex.CursorKind.UNION_DECL:
    #     parse_struct(parser, c)

    # elif c.kind == cindex.CursorKind.STRUCT_DECL:
    #     parse_struct(parser, c)

    # elif c.kind == cindex.CursorKind.CLASS_DECL:
    #     parse_struct(parser, c)

    elif c.kind == cindex.CursorKind.TYPEDEF_DECL:
        cursors.parse_typedef(parser, c)

    elif c.kind == cindex.CursorKind.FUNCTION_DECL:
        cursors.parse_function(parser, c, extern_c)

    # elif c.kind == cindex.CursorKind.ENUM_DECL:
    #     parse_enum(parser, c)

    # elif c.kind == cindex.CursorKind.VAR_DECL:
    #     # static variable
    #     pass

    # elif c.kind == cindex.CursorKind.CONSTRUCTOR:
    #     pass

    # elif c.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
    #     pass

    # elif c.kind == cindex.CursorKind.CLASS_TEMPLATE:
    #     parse_struct(parser, c)

    else:
        raise NotImplementedError(str(c.kind))


def parse_namespace(parser: TypeParser,
                    c: cindex.Cursor,
                    files: List[pathlib.Path],
                    used=None):
    if not used:
        used = set()

    for i, child in enumerate(c.get_children()):
        if child.kind == cindex.CursorKind.NAMESPACE:
            # nested
            parser.push_namespace(child.spelling)
            parse_namespace(parser, child, files)
            parser.pop_namespace()
        else:

            parse_cursor(parser, child, files, used)


def parse_files(parser: TypeParser,
                *paths: pathlib.Path,
                cpp_flags=None,
                debug=False):
    if cpp_flags is None:
        cpp_flags = []
    cpp_flags += [f'-I{x.parent}' for x in paths]
    with tmp_from_source(''.join([f'#include <{x.name}>\n'
                                  for x in paths])) as path:
        tu = get_tu(path, cpp_flags=cpp_flags)
        include_path_list = [x for x in paths]
        include_path_list.append(path)
        if debug:
            debug_print(tu.cursor, include_path_list)
        else:
            parse_namespace(parser, tu.cursor, include_path_list)


def parse_source(parser: TypeParser, source: str, cpp_flags=None, debug=False):
    if cpp_flags is None:
        cpp_flags = []
    with tmp_from_source(source) as path:
        tu = get_tu(path, cpp_flags=cpp_flags)
        if debug:
            debug_print(tu.cursor, [])
        parse_namespace(parser, tu.cursor, [])
