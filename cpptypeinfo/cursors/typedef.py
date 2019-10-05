from typing import Optional
import pathlib
from clang import cindex
import cpptypeinfo
from cpptypeinfo.usertype import Typedef
from .type_kind import cindex_type_to_cpptypeinfo


def parse_typedef(parser: cpptypeinfo.TypeParser,
                  c: cindex.Cursor) -> Optional[Typedef]:
    t = cindex_type_to_cpptypeinfo(c.underlying_typedef_type)
    if not t:
        tokens = [t.spelling for t in c.get_tokens()]
        raise Exception(
            f'unknown type: {c.underlying_typedef_type.kind}: {tokens}')

    decl = parser.typedef(c.spelling, t)
    decl.file = pathlib.Path(c.location.file.name)
    decl.line = c.location.line
    return decl

    # tokens = [t.spelling for t in c.get_tokens()]
    # if not tokens:
    #     return None
    # elif tokens[-1] == ')' or c.underlying_typedef_type.spelling != 'int':
    #     parsed = parser.parse(c.underlying_typedef_type.spelling)
    # else:
    #     # int type may be wrong.
    #     # workaround
    #     end = -1
    #     for i, t in enumerate(tokens):
    #         if t == '{':
    #             end = i
    #             break
    #     parsed = parser.parse(' '.join(tokens[1:end]))
    # if not parsed:
    #     return
