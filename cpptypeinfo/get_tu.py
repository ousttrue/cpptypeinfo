import pathlib
from typing import List, Optional
import tempfile
import os
import contextlib
from clang import cindex

DEFAULT_CLANG_DLL = pathlib.Path("C:/Program Files/LLVM/bin/libclang.dll")
SET_DLL = False


def get_tu(path: pathlib.Path,
           include_path_list: List[pathlib.Path] = None,
           cpp_flags: List[str] = None,
           use_macro: bool = False,
           dll: Optional[pathlib.Path] = None) -> cindex.TranslationUnit:
    '''
    parse cpp source
    '''
    global SET_DLL

    if not path.exists():
        raise FileNotFoundError(str(path))

    if not dll and DEFAULT_CLANG_DLL.exists():
        dll = DEFAULT_CLANG_DLL
    if not SET_DLL and dll:
        cindex.Config.set_library_file(str(dll))
        SET_DLL = True

    index = cindex.Index.create()

    kw = {}
    if use_macro:
        kw['options'] = cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    cpp_args = ['-x', 'c++', '-DUNICODE=1', '-DNOMINMAX=1']
    if include_path_list is not None:
        for i in include_path_list:
            value = f'-I{str(i)}'
            if value not in cpp_args:
                cpp_args.append(value)
    if cpp_flags:
        for f in cpp_flags:
            cpp_args.append(f)

    return index.parse(str(path), cpp_args, **kw)


@contextlib.contextmanager
def tmp(src):
    fd, tmp_name = tempfile.mkstemp(prefix='tmpheader_', suffix='.h')
    os.close(fd)
    with open(tmp_name, 'w', encoding='utf-8') as f:
        f.write(src)
    try:
        yield pathlib.Path(tmp_name)
    finally:
        os.unlink(tmp_name)


def get_tu_from_source(src: str):
    with tmp(src) as path:
        return get_tu(path)
