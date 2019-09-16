import pathlib
from typing import List
from .declaration import *
from .get_tu import get_tu, get_tu_from_source, tmp_from_source
from .cursor import parse_namespace

VERSION = '0.1.0'


def parse_header(path: pathlib.Path, cpp_flags=None, include_path_list=None):
    tu = get_tu(path, cpp_flags=cpp_flags, include_path_list=include_path_list)
    include_path_list = include_path_list if include_path_list else []
    include_path_list.append(str(path))
    parse_namespace(tu.cursor, include_path_list)


def parse_headers(*paths: List[pathlib.Path],
                  cpp_flags=None,
                  include_path_list=None):
    root_ns = push_namespace()
    with tmp_from_source(''.join([f'#include <{x.name}>\n'
                                  for x in paths])) as path:
        parse_header(path,
                     cpp_flags=[f'-I{x.parent}' for x in paths],
                     include_path_list=[str(x) for x in paths])
    pop_namespace()
    return root_ns
