import pathlib
from typing import List
from .declaration import *
from .get_tu import get_tu, get_tu_from_source, tmp_from_source
from .cursor import parse_namespace

VERSION = '0.1.0'


def parse_headers(*paths: pathlib.Path, cpp_flags=None):
    root_ns = push_namespace()
    if not cpp_flags:
        cpp_flags = []
    cpp_flags += [f'-I{x.parent}' for x in paths]
    with tmp_from_source(''.join([f'#include <{x.name}>\n'
                                  for x in paths])) as path:
        tu = get_tu(path, cpp_flags=cpp_flags)
        include_path_list = [x for x in paths]
        include_path_list.append(path)
        parse_namespace(tu.cursor, include_path_list)

    pop_namespace()
    return root_ns
