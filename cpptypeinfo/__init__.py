import pathlib
from .declaration import *
from .get_tu import get_tu, get_tu_from_source
from .cursor import parse_namespace

VERSION = '0.0.1'


def parse_header(path: pathlib.Path):
    tu = get_tu(path)
    return parse_namespace(tu.cursor, [str(path)])
