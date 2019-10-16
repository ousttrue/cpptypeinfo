from typing import List, TextIO, Dict, Set, Optional
import pathlib
import shutil
import time
import datetime
import cpptypeinfo
from cpptypeinfo.usertype import (TypeRef, UserType, Typedef, Pointer,
                                  StructType, Struct, Function, Enum)

IMPORT = '''
import core.sys.windows.windef;
import core.sys.windows.com;
'''

HEAD = '''
extern(Windows){

alias IID = GUID;
'''

TAIL = '''

}

'''

D3D11_SNIPPET = '''

'''

D2D1_SNIPPET = '''

enum D2DERR_RECREATE_TARGET = 0x8899000CL;

'''

D2D_BASETYPES = '''

struct D3DCOLORVALUE
{
    float r;
    float g;
    float b;
    float a;
}

'''

snippet_map = {
    'd3d11': D3D11_SNIPPET,
    'd2d1': D2D1_SNIPPET,
    'd2dbasetypes': D2D_BASETYPES,
}

dlang_map: Dict[cpptypeinfo.Type, str] = {
    cpptypeinfo.Void(): 'void',
    cpptypeinfo.Int8(): 'byte',
    cpptypeinfo.Int16(): 'short',
    cpptypeinfo.Int32(): 'int',
    cpptypeinfo.Int64(): 'long',
    cpptypeinfo.UInt8(): 'ubyte',
    cpptypeinfo.UInt16(): 'ushort',
    cpptypeinfo.UInt32(): 'uint',
    cpptypeinfo.UInt64(): 'ulong',
    cpptypeinfo.Float(): 'float',
    cpptypeinfo.Double(): 'double',
}


def is_const(typeref: TypeRef) -> bool:
    if typeref.is_const:
        return True
    if not isinstance(typeref.ref, Typedef):
        return False
    return is_const(typeref.ref.typeref)


def to_d(typeref: TypeRef, level=0) -> str:
    const = 'const ' if level == 0 and is_const(typeref) else ''

    if isinstance(typeref.ref, Pointer):
        if isinstance(typeref.ref.typeref.ref, Struct):
            if typeref.ref.typeref.ref.type_name == 'HWND__':
                return 'HWND'
            if typeref.ref.typeref.ref.iid:
                # interface remove *
                return f'{const}{typeref.ref.typeref.ref.type_name}'
        return f'{const}{to_d(typeref.ref.typeref, level+1)}*'
    if isinstance(typeref.ref, Struct):
        if typeref.ref.type_name in ['HDC__', 'HINSTANCE__']:
            return typeref.ref.type_name[:-2]
        elif not typeref.ref.type_name:
            if typeref.ref.struct_type == StructType.UNION:
                # anonymous union
                fields = [
                    to_d(f.typeref, level + 1) + ' ' + f.name + ';\n'
                    for f in typeref.ref.fields
                ]
                return 'union {\n' + ''.join(fields) + '}'
            elif typeref.ref.struct_type == StructType.STRUCT:
                # anonymous struct
                fields = [
                    to_d(f.typeref, level + 1) + ' ' + f.name + ';'
                    for f in typeref.ref.fields
                ]
                return '// anonymous struct {' + ''.join(fields) + '}'
            else:
                raise Exception()
        else:
            return f'{const}{typeref.ref.type_name}'
    if isinstance(typeref.ref, Enum):
        return f'{const}{typeref.ref.type_name}'
    if isinstance(typeref.ref, Function):
        return 'void*'
    text = dlang_map.get(typeref.ref)
    if text:
        return f'{const}{text}'
    return f'{typeref}'


class DSource:
    def __init__(self, file: pathlib.Path):
        self.file = file
        self.com_interfaces: List[Struct] = []
        self.functions: List[Function] = []
        self.enums: List[Enum] = []
        self.structs: List[Struct] = []
        self.imports: List[pathlib.Path] = []
        self.used: Set[int] = set()
        self.macros: List[cpptypeinfo.MacroDefinition] = []

    def __str__(self) -> str:
        return f'{self.file.name}: {len(self.com_interfaces)}interfaces {len(self.functions)}functions'

    def add_com_interface(self, com_interface: Struct) -> None:
        if com_interface in self.com_interfaces:
            return
        self.com_interfaces.append(com_interface)

    def add_export_function(self, function: Function) -> None:
        if function in self.functions:
            return
        self.functions.append(function)

    def add_enum(self, enum: Enum) -> None:
        if enum in self.enums:
            return
        self.enums.append(enum)
        self.add_import(enum.file)

    def add_struct(self, struct: Struct) -> None:
        if struct in self.structs:
            return
        self.structs.append(struct)
        self.add_import(struct.file)

    def add_import(self, file: pathlib.Path) -> None:
        if not file:
            return
        if file == self.file:
            return
        if file in self.imports:
            return
        self.imports.append(file)

    def generate(self, dir: pathlib.Path, parent: str) -> None:
        module_name = self.file.stem
        dst = dir / (module_name + '.d')
        print(f'create {dst}')
        dst.parent.mkdir(exist_ok=True, parents=True)

        with dst.open('w') as d:
            d.write(f'// cpptypeinfo generated\n')
            d.write(f'module {parent}.{module_name};\n')

            d.write(IMPORT)
            for i in self.imports:
                d.write(f'import {parent}.{i.stem};\n')
            d.write('\n')

            for macro in self.macros:
                d.write(f'const {macro.name} = {macro.value};\n')
            d.write('\n')

            for enum in self.enums:
                dlang_enum(d, enum)
                d.write('\n')

            for struct in self.structs:
                if dlang_struct(d, struct):
                    d.write('\n')

            for com in self.com_interfaces:
                if dlang_com_interface(d, com):
                    d.write('\n')

            for function in self.functions:
                dlang_function(d, function)


def dlang_enum(d: TextIO, node: Enum) -> None:
    d.write(f'enum {node.type_name} {{\n')
    for v in node.values:
        name = v.name
        if name.startswith(node.type_name):
            # invalid: DXGI_FORMAT_420_OPAQUE
            if name[len(node.type_name) + 1].isnumeric():
                name = name[len(node.type_name) + 0:]
            else:
                name = name[len(node.type_name) + 1:]
        else:
            for suffix in ['_FLAG', '_MODE']:
                suffix_len = len(suffix)
                if node.type_name.endswith(suffix) and name.startswith(
                        node.type_name[:-suffix_len]):
                    if name[len(node.type_name) - suffix_len + 1].isnumeric():
                        name = name[len(node.type_name) - suffix_len:]
                    else:
                        name = name[len(node.type_name) - suffix_len + 1:]
                    break

        value = v.value
        if isinstance(value, int):
            value = f'{value:#010x}'

        d.write(f'    {name} = {value},\n')
    d.write(f'}}\n')


def dlang_alias(d: TextIO, node: Typedef) -> None:
    if node.name.startswith('PFN_'):
        # function pointer workaround
        d.write(f'alias {node.name} = void *;\n')
    else:
        typedef_type = node.typedef_type
        if typedef_type.startswith('struct '):
            typedef_type = typedef_type[7:]
        d.write(f'alias {node.name} = {typedef_type};\n')


def dlang_function(d: TextIO, m: Function, indent='') -> None:
    ret = m.result if m.result else 'void'
    params = ', '.join(f'{to_d(p.typeref)} {p.name}' for p in m.params)
    extern_c = 'extern(C) ' if m.extern_c else ''
    d.write(f'{indent}{extern_c}{to_d(ret)} {m.name}({params});\n')


def escape_symbol(name: str) -> str:
    if name in ['module']:
        return '_' + name
    return name


def dlang_struct(d: TextIO, node: Struct) -> bool:
    if not node.type_name:
        return False
    # if not node.fields:
    #     # may forward decl
    #     return False

    d.write(f'{node.struct_type.value} {node.type_name}{{\n')
    for f in node.fields:
        d.write(f'    {to_d(f.typeref, 1)} {escape_symbol(f.name)};\n')
    d.write(f'}}\n')
    return True


def dlang_com_interface(d: TextIO, node: Struct) -> bool:
    if not node.base:
        return False

    d.write(f'// {node.file.name}: {node.line}\n')
    d.write(f'interface {node.type_name}: {to_d(node.base)} {{\n')
    if node.iid:
        h = node.iid.hex
        iid = f'0x{h[0:8]}, 0x{h[8:12]}, 0x{h[12:16]}, [0x{h[16:18]}, 0x{h[18:20]}, 0x{h[20:22]}, 0x{h[22:24]}, 0x{h[24:26]}, 0x{h[26:28]}, 0x{h[28:30]}, 0x{h[30:32]}]'
        d.write(f'    static immutable iidof = GUID({iid});\n')
    for m in node.methods:
        dlang_function(d, m, '    ')
    d.write(f'}}\n')
    return True


def generate(parser: cpptypeinfo.TypeParser, decl_map: cpptypeinfo.DeclMap,
             headers: List[pathlib.Path], dir: pathlib.Path,
             module_list: List[str]) -> None:
    '''
    write to 

    dir/module_name0/module_name1/.../module_name.d

    すべての com interface と __declspec(dllimport) な関数とそれの参照する型を出力する
    '''

    # clear folder
    if dir.exists():
        print(f'clear {dir}')
        shutil.rmtree(dir)
        time.sleep(0.1)

    # preprocess
    decl_map.resolve_typedef()

    source_map: Dict[pathlib.Path, DSource] = {}

    def get_or_create_source_map(file: pathlib.Path) -> DSource:
        source = source_map.get(file)
        if not source:
            source = DSource(file)
            source_map[file] = source
        return source

    def register_enum_struct(ref: UserType) -> Optional[pathlib.Path]:
        # enum
        if isinstance(ref, Enum):
            source = get_or_create_source_map(ref.file)
            source.add_enum(ref)
            return ref.file
        elif isinstance(ref, Pointer) and isinstance(ref.typeref.ref, Enum):
            source = get_or_create_source_map(ref.typeref.ref.file)
            source.add_enum(ref.typeref.ref)
            return ref.typeref.ref.file
        # struct
        elif isinstance(ref, Struct):
            source = get_or_create_source_map(ref.file)
            source.add_struct(ref)
            return ref.file
        elif isinstance(ref, Pointer) and isinstance(ref.typeref.ref, Struct):
            source = get_or_create_source_map(ref.typeref.ref.file)
            source.add_struct(ref.typeref.ref)
            return ref.typeref.ref.file

    def register_struct(v: Struct, used):
        if v in used:
            return
        used.append(v)

        source = get_or_create_source_map(v.file)
        if v.iid:
            # print(f'{v.file}: {v.type_name}')
            source.add_com_interface(v)

            for m in v.methods:
                for p in m.params:
                    path = register_enum_struct(p.typeref.ref)
                    if path:
                        source.add_import(path)
                path = register_enum_struct(m.result.ref)
                if path:
                    source.add_import(path)

        else:
            source.add_struct(v)
            for f in v.fields:
                path = register_enum_struct(f.typeref.ref)
                if path:
                    source.add_import(path)

                if isinstance(f.typeref.ref, Struct):
                    register_struct(f.typeref.ref, used)
                elif isinstance(f.typeref.ref, Pointer) and isinstance(
                        f.typeref.ref.typeref.ref, Struct):
                    register_struct(f.typeref.ref.typeref.ref, used)

    for k, v in decl_map.decl_map.items():
        if v.file in headers:
            if isinstance(v, Struct):
                register_struct(v, [])

            elif isinstance(v, Enum):
                register_enum_struct(v)

            elif isinstance(v, Function):
                # dll export
                # if v.dll_export:
                if True:
                    # print(f'{v.file}: {v.get_exportname()}')
                    source = get_or_create_source_map(v.file)
                    source.add_export_function(v)
                    # params
                    for p in v.params:
                        path = register_enum_struct(p.typeref.ref)
                        if path:
                            source.add_import(path)
                    # return
                    path = register_enum_struct(v.result.ref)
                    if path:
                        source.add_import(path)

    for m in decl_map.macro_definitions:
        if m.name == 'D3D11_SDK_VERSION':
            source = get_or_create_source_map(m.file)
            source.macros.append(m)
        elif m.file.name == 'dxgi.h':
            source = get_or_create_source_map(m.file)
            source.macros.append(m)
        else:
            pass

    module_name = dir.name

    # write each DLangSource
    for k, v in source_map.items():
        v.generate(dir, module_name)

    # package.d
    dst = dir / 'package.d'
    print(f'create {dst}')
    dst.parent.mkdir(exist_ok=True, parents=True)
    with dst.open('w') as d:
        d.write(f'module {module_name};\n')
        for k, v in source_map.items():
            d.write(f'public import {module_name}.{k.stem};\n')
