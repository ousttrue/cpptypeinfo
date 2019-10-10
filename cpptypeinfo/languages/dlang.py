from typing import List, TextIO, Dict
import pathlib
import shutil
import time
import datetime
import cpptypeinfo
from cpptypeinfo.usertype import (TypeRef, Typedef, Struct, Function, Enum)

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


class DSource:
    def __init__(self, file: pathlib.Path):
        self.file = file
        self.com_interfaces: List[Struct] = []
        self.functions: List[Function] = []

    def __str__(self) -> str:
        return f'{self.file.name}: {len(self.com_interfaces)}interfaces {len(self.functions)}functions'

    def add_com_interface(self, com_interface: Struct) -> None:
        self.com_interfaces.append(com_interface)

    def add_export_function(self, function: Function) -> None:
        self.functions.append(function)

    def generate(self, dir: pathlib.Path, parent: str) -> None:
        module_name = self.file.stem
        dst = dir / (module_name + '.d')
        print(f'create {dst}')
        dst.parent.mkdir(exist_ok=True, parents=True)

        with dst.open('w') as d:
            d.write(f'// cpptypeinfo generated: {datetime.datetime.today()}\n')
            d.write(f'module {parent}.{module_name}.d;\n')

            d.write(IMPORT)

            for com in self.com_interfaces:
                dlang_struct(d, com)


def dlang_enum(d: TextIO, node: Enum) -> None:
    d.write(f'enum {node.name} {{\n')
    for v in node.values:
        name = v.name
        if name.startswith(node.name):
            # invalid: DXGI_FORMAT_420_OPAQUE
            if name[len(node.name) + 1].isnumeric():
                name = name[len(node.name) + 0:]
            else:
                name = name[len(node.name) + 1:]
        else:
            for suffix in ['_FLAG', '_MODE']:
                suffix_len = len(suffix)
                if node.name.endswith(suffix) and name.startswith(
                        node.name[:-suffix_len]):
                    if name[len(node.name) - suffix_len + 1].isnumeric():
                        name = name[len(node.name) - suffix_len:]
                    else:
                        name = name[len(node.name) - suffix_len + 1:]
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


def repl(m):
    return m[0][1:]


def to_d(param: TypeRef) -> str:
    # param_type = (param_type.replace('&', '*').replace('*const *', '**'))
    # if param_type[0] == 'I':  # is_instance
    #     param_type = re.sub(r'\*+', repl, param_type)  # reduce *
    # return param_type
    return str(param)


def dlang_function(d: TextIO, m: Function, indent='') -> None:
    ret = m.result if m.result else 'void'
    params = ', '.join(f'{to_d(p.typeref)} {p.name}' for p in m.params)
    d.write(f'{indent}{ret} {m.name}({params});\n')


def dlang_struct(d: TextIO, node: Struct) -> None:
    if node.type_name[0] == 'I':
        # com interface
        base = node.base
        if not base:
            base = 'IUnknown'
        d.write(f'interface {node.type_name}: {base} {{\n')
        if node.iid:
            h = node.iid.hex
            iid = f'0x{h[0:8]}, 0x{h[8:12]}, 0x{h[12:16]}, [0x{h[16:18]}, 0x{h[18:20]}, 0x{h[20:22]}, 0x{h[22:24]}, 0x{h[24:26]}, 0x{h[26:28]}, 0x{h[28:30]}, 0x{h[30:32]}]'
            d.write(f'    static immutable iidof = GUID({iid});\n')
        for m in node.methods:
            dlang_function(d, m, '    ')
        d.write(f'}}\n')
    else:
        d.write(f'{node}\n')


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

    source_map: Dict[pathlib.Path, DSource] = {}

    for k, v in decl_map.decl_map.items():
        if v.file in headers:
            if isinstance(v, Struct):
                if v.iid:
                    # print(f'{v.file}: {v.type_name}')
                    source = source_map.get(v.file)
                    if not source:
                        source = DSource(v.file)
                        source_map[v.file] = source
                    source.add_com_interface(v)

            # elif isinstance(v, Enum):
            #     print(f'{v.file}: {v}')

            elif isinstance(v, Function):
                # dll export
                if v.extern_c and not v.has_body:
                    # print(f'{v.file}: {v.get_exportname()}')
                    source = source_map.get(v.file)
                    if not source:
                        source = DSource(v.file)
                        source_map[v.file] = source
                    source.add_export_function(v)

    module_name = dir.name

    for k, v in source_map.items():
        # print(v)
        v.generate(dir, module_name)

    #     for include in header.includes:
    #         d.write(
    #             f'public import windowskits.{package_name}.{include.name[:-2]};\n'
    #         )
    #     d.write(HEAD)

    #     snippet = snippet_map.get(module_name)
    #     if snippet:
    #         d.write(snippet)

    #     for m in header.macro_defnitions:
    #         d.write(f'enum {m.name} = {m.value};\n')

    #     for node in header.nodes:

    #         if isinstance(node, EnumNode):
    #             dlang_enum(d, node)
    #             d.write('\n')
    #         elif isinstance(node, TypedefNode):
    #             dlang_alias(d, node)
    #             d.write('\n')
    #         elif isinstance(node, StructNode):
    #             if node.is_forward:
    #                 continue
    #             if node.name[0] == 'C':  # class
    #                 continue
    #             dlang_struct(d, node)
    #             d.write('\n')
    #         elif isinstance(node, FunctionNode):
    #             dlang_function(d, node)
    #             d.write('\n')
    #         else:
    #             #raise Exception(type(node))
    #             pass
    #         '''

    #         # constant

    #         const(d, v.const_list)

    #         '''
    #     d.write(TAIL)

    # # for include in header.includes:
    # #     self.generate_header(include, root, package_name)
