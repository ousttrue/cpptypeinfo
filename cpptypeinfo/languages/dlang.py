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


def has_anonymous(usertype: UserType, used) -> bool:
    used.append(usertype)

    if not isinstance(usertype, Struct):
        return False
    if not usertype.type_name:
        return True
    for f in usertype.fields:
        if f.typeref.ref not in used:
            if has_anonymous(f.typeref.ref, used):
                return True
    return False


def is_const(typeref: TypeRef) -> bool:
    if typeref.is_const:
        return True
    if not isinstance(typeref.ref, Typedef):
        return False
    return is_const(typeref.ref.typeref)


def to_d(typeref: TypeRef, level=0) -> str:
    const = 'const ' if level == 0 and is_const(typeref) else ''

    if isinstance(typeref.ref, Pointer):
        return f'{const}{to_d(typeref.ref.typeref, level+1)}*'
    if isinstance(typeref.ref, Struct):
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

    def __str__(self) -> str:
        return f'{self.file.name}: {len(self.com_interfaces)}interfaces {len(self.functions)}functions'

    def add_com_interface(self, com_interface: Struct) -> None:
        self.com_interfaces.append(com_interface)

    def add_export_function(self, function: Function) -> None:
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
            d.write(f'// cpptypeinfo generated: {datetime.datetime.today()}\n')
            d.write(f'module {parent}.{module_name};\n')

            d.write(IMPORT)
            for i in self.imports:
                d.write(f'import {parent}.{i.stem};\n')
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
    d.write(f'{indent}{to_d(ret)} {m.name}({params});\n')


def dlang_struct(d: TextIO, node: Struct) -> bool:
    if not node.type_name:
        return False
    if not node.fields:
        # may forward decl
        return False
    if has_anonymous(node, []):
        return False

    d.write(f'{node.struct_type.value} {node.type_name}{{\n')
    for f in node.fields:
        d.write(f'    {to_d(f.typeref, 1)} {f.name};\n')
    d.write(f'}}\n')
    return True


def dlang_com_interface(d: TextIO, node: Struct) -> bool:
    if not node.base:
        return False
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

    for k, v in decl_map.decl_map.items():
        if v.file in headers:
            if isinstance(v, Struct):
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
                    for f in v.fields:
                        path = register_enum_struct(f.typeref.ref)
                        if path:
                            source.add_import(path)

            elif isinstance(v, Function):
                # dll export
                if v.extern_c and not v.has_body:
                    # print(f'{v.file}: {v.get_exportname()}')
                    source = get_or_create_source_map(v.file)
                    source.add_export_function(v)

    module_name = dir.name

    for k, v in source_map.items():
        # print(v)
        v.generate(dir, module_name)
