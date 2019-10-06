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
        # if c.underlying_typedef_type.kind == cindex.TypeKind.POINTER:
        #     p = c.underlying_typedef_type.get_pointee()
        #     text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}=>{p.spelling}'
        if children:
            if c.underlying_typedef_type.kind == cindex.TypeKind.POINTER:
                p = c.underlying_typedef_type.get_pointee()
                child = children[0]
                ref = child.referenced
                text = f'{level}({c.hash}){c.kind}=>{c.spelling}: {c.underlying_typedef_type.kind}=>{children[0].hash}'
            else:
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
                cpp_flags=None,
                debug=False) -> cursors.DeclMap:
    decl_map = cursors.DeclMap()
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
            decl_map.parse_namespace(parser, tu.cursor, include_path_list)
    return decl_map


def parse_source(parser: TypeParser, source: str, cpp_flags=None,
                 debug=False) -> cursors.DeclMap:
    decl_map = cursors.DeclMap()

    if cpp_flags is None:
        cpp_flags = []
    with tmp_from_source(source) as path:
        tu = get_tu(path, cpp_flags=cpp_flags)
        if debug:
            debug_print(tu.cursor, [])
        decl_map.parse_namespace(parser, tu.cursor, [])

    return decl_map
