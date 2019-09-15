import pathlib
from .declaration import *
from .get_tu import get_tu, get_tu_from_source, tmp_from_source
from .cursor import parse_namespace

VERSION = '0.0.1'


def parse_header(path: pathlib.Path, cpp_flags=None, include_path_list=None):
    tu = get_tu(path, cpp_flags=cpp_flags, include_path_list=include_path_list)
    include_path_list = include_path_list if include_path_list else []
    include_path_list.append(str(path))
    parse_namespace(tu.cursor, include_path_list)
