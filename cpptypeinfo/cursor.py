import pathlib
from typing import List
from clang import cindex
from .typeparser import TypeParser
from .get_tu import get_tu, tmp_from_source
from .decl_map import DeclMap


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
        # children = [child for child in c.get_children()]
        # if c.underlying_typedef_type.kind == cindex.TypeKind.POINTER:
        #     p = c.underlying_typedef_type.get_pointee()
        #     text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}=>{p.spelling}'
        # if children:
        #     if c.underlying_typedef_type.kind == cindex.TypeKind.POINTER:
        #         p = c.underlying_typedef_type.get_pointee()
        #         child = children[0]
        #         ref = child.referenced
        #         text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}=>{children[0].hash}'
        #     else:
        #         text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}=>{children[0].hash}'
        # else:
        #     text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}'
        # print(text)
        children = [child for child in c.get_children()]
        if c.underlying_typedef_type.kind == cindex.TypeKind.POINTER:
            child = children[0]
            ref = child.referenced
            text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind} => {ref.hash}'
        else:
            text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}'
        print(text)

    else:
        extra = ''
        go_children = True

        if c.type.kind == cindex.TypeKind.POINTER:
            p = c.type.get_pointee()
            a = 0
            extra = f'=>({p.spelling})'

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


def parse_files(parser: TypeParser,
                *paths: pathlib.Path,
                includes=None,
                cpp_flags=None,
                debug=False) -> DeclMap:
    if cpp_flags is None:
        cpp_flags = []
    cpp_flags += [f'-I{x.parent}' for x in paths]
    if includes:
        cpp_flags += [f'-I{x}' for x in includes]
    with tmp_from_source(''.join([f'#include <{x.name}>\n'
                                  for x in paths])) as path:
        tu = get_tu(path, cpp_flags=cpp_flags)
        include_path_list = [x for x in paths]
        include_path_list.append(path)
        decl_map = DeclMap(parser, include_path_list)
        if debug:
            debug_print(tu.cursor, include_path_list)
        else:
            decl_map.parse_cursor(tu.cursor)
        return decl_map


def parse_source(parser: TypeParser, source: str, cpp_flags=None,
                 debug=False) -> DeclMap:
    decl_map = DeclMap(parser, [])

    if cpp_flags is None:
        cpp_flags = []
    with tmp_from_source(source) as path:
        tu = get_tu(path, cpp_flags=cpp_flags)
        if debug:
            debug_print(tu.cursor, [])
        decl_map.parse_cursor(tu.cursor)

    return decl_map
