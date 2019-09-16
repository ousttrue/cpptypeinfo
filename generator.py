import pathlib
import sys
import shutil
from typing import Tuple, Optional, Dict
from jinja2 import Template
import cpptypeinfo
HERE = pathlib.Path(__file__).absolute().parent
CIMGUI_H = HERE / 'libs/cimgui/cimgui.h'
IMGUI_H = HERE / 'libs/imgui/imgui.h'

HEADLINE = f'// generated cpptypeinfo-{cpptypeinfo.VERSION}'
NAMESPACE_NAME = 'SharpImGui'
USING = '''using System;
using System.Runtime.InteropServices;'''

cs_type_map: Dict[cpptypeinfo.PrimitiveType, Tuple[Optional[str], str]] = {
    cpptypeinfo.Int8: (None, 'sbyte'),
    cpptypeinfo.Int16: (None, 'short'),
    cpptypeinfo.Int32: (None, 'int'),
    cpptypeinfo.Int64: (None, 'long'),
    cpptypeinfo.UInt8: (None, 'byte'),
    cpptypeinfo.UInt16: (None, 'ushort'),
    cpptypeinfo.UInt32: (None, 'uint'),
    cpptypeinfo.UInt64: (None, 'ulong'),
    cpptypeinfo.Float: (None, 'float'),
    cpptypeinfo.Double: (None, 'double'),
    cpptypeinfo.Bool: ('MarshalAs(UnmanagedType.U1)', 'bool'),
}


def to_cs(decl: cpptypeinfo.Type) -> Tuple[Optional[str], str]:
    if not decl:
        # bug
        return (None, 'IntPtr')

    cs_type = cs_type_map.get(decl.__class__)
    if cs_type:
        return cs_type

    if isinstance(decl, cpptypeinfo.Void):
        return (None, 'void')
    elif isinstance(decl, cpptypeinfo.Pointer):
        return (None, 'IntPtr')
    elif isinstance(decl, cpptypeinfo.Array):
        return (None, 'IntPtr')
    elif isinstance(decl, cpptypeinfo.Function):
        return (None, 'IntPtr')
    elif isinstance(decl, cpptypeinfo.Struct):
        return (None, decl.type_name)
    elif isinstance(decl, cpptypeinfo.Typedef):
        if isinstance(decl.get_concrete_type(), cpptypeinfo.Function):
            return (None, 'IntPtr')
        else:
            return (None, decl.type_name)
    else:
        raise NotImplementedError(str(decl))


CS_SYMBOLS = ['ref', 'in', 'out']


def cs_symbol(name: str):
    if name in CS_SYMBOLS:
        return '_' + name
    return name


def generate_enum(enum: cpptypeinfo.Enum, root: pathlib.Path, is_flags: bool,
                  typename_filter, valuename_filter):

    type_name = typename_filter(enum.type_name)

    dst = root / f'{type_name}.cs'
    t = Template('''{{ headline }}
{{ using }}

namespace {{ namespace }}
{
    // {{ file }}:{{ line }}
    {{ attribute }}
    public enum {{ type_name }}
    {
{%- for value in values %}
        {{ value.name }} = {{ value.value }},
{%- endfor %}
    }
}
''')
    with open(dst, 'w') as f:
        f.write(
            t.render(headline=HEADLINE,
                     using=USING,
                     namespace=NAMESPACE_NAME,
                     attribute='[Flags]' if is_flags else '',
                     type_name=type_name,
                     values=[
                         valuename_filter(enum.type_name, v)
                         for v in enum.values
                     ],
                     file=enum.file.name,
                     line=enum.line))


def generate_typedef(typedef: cpptypeinfo.Typedef, root: pathlib.Path):

    if isinstance(
            typedef.typeref,
            cpptypeinfo.Struct) and typedef.type_name == typedef.src.type_name:
        # skip typedef struct same name
        return

    dst = root / f'{typedef.type_name}.cs'

    t = Template('''{{ headline }}
{{ using }}

namespace {{ namespace }}
{
    // {{ file}}:{{ line }}
    public struct {{ type_name }}
    {
        {{ type }};
    }
}
''')

    typedef_attr, typedef_type = to_cs(typedef.typeref.ref)
    if typedef_attr:
        typedef_attr = f'[typedef_attr]'
    else:
        typedef_attr = ''

    typedef_type = f'{typedef_attr}public {typedef_type} Value'

    with open(dst, 'w') as f:
        f.write(
            t.render(headline=HEADLINE,
                     using=USING,
                     namespace=NAMESPACE_NAME,
                     type_name=typedef.type_name,
                     type=typedef_type,
                     file=typedef.file.name,
                     line=typedef.line))


def generate_struct(decl: cpptypeinfo.Struct, root: pathlib.Path):

    dst = root / f'{decl.type_name}.cs'
    t = Template('''// {{ headline }}
{{ using }}

namespace {{ namespace }}
{
    // {{ file }}:{{ line }}
    {{ attribute }}
    public struct {{ type_name }}
    {
{%- for value in values %}
        {{ value }};
{%- endfor %}
    }
}
''')

    def field_str(f: cpptypeinfo.Field):
        field_attr, field_type = to_cs(f.typeref.ref)
        if field_attr:
            field_attr = f'[{field_attr}]'
        else:
            field_attr = ''
        return f'{field_attr}public {field_type} {f.name}'

    with open(dst, 'w') as f:
        f.write(
            t.render(headline=HEADLINE,
                     using=USING,
                     namespace=NAMESPACE_NAME,
                     type_name=decl.type_name,
                     values=[field_str(f) for f in decl.fields],
                     file=decl.file.name,
                     line=decl.line))


def generate(ns: cpptypeinfo.Namespace, root: pathlib.Path):
    '''
    cimgui を出力する。
    enum XXXFlags_ と typedef int XXXFlags
    をまとめて enum XXXFlags にする。
    '''
    root.mkdir(parents=True, exist_ok=True)

    def typename_filter(src):
        if src.endswith('_'):
            return src[:-1]
        else:
            return src

    def valuename_filter(type_name, src):
        if src.name.startswith(type_name):
            return cpptypeinfo.EnumValue(src.name[len(type_name):], src.value)
        else:
            return src

    #
    # first enum
    #
    removes = []
    for k, v in ns.user_type_map.items():
        if isinstance(v, cpptypeinfo.Enum):

            generate_enum(v, root, v.type_name.endswith('Flags_'),
                          typename_filter, valuename_filter)
            removes.append(v.type_name[:-1])

    #
    # second, except enum
    #
    for k, v in ns.user_type_map.items():
        if isinstance(v, cpptypeinfo.Enum):
            pass
        elif isinstance(v, cpptypeinfo.Typedef):
            if v.type_name in removes:
                continue
            if v.type_name.endswith('Callback'):
                continue
            generate_typedef(v, root)
        elif isinstance(v, cpptypeinfo.Struct):
            generate_struct(v, root)
        else:
            raise Exception()


def generate_functions(root_ns: cpptypeinfo.Namespace, root: pathlib.Path):
    dst = root / 'CImGui.cs'

    def to_cs_param(p: cpptypeinfo.Param):
        param_attr, param = to_cs(p.typeref.ref)
        if param_attr:
            param_attr = f'[{param_attr}]'
        else:
            param_attr = ''
        return f'{param_attr}{param} {cs_symbol(p.name)}'

    def function_str(v: cpptypeinfo.Function):
        params = [to_cs_param(p) for p in v.params]
        ret_attr, ret = to_cs(v.result.ref)
        if ret_attr:
            ret_attr = f'\n        [return: {ret_attr}]\n'
        else:
            ret_attr = ''
        return f'''// {v.file.name}:{v.line}
        [DllImport(DLLNAME)]{ret_attr}
        public static extern {ret} {v.name}({", ".join(params)});'''

    values = []
    for ns in root_ns.traverse():
        if not isinstance(ns, cpptypeinfo.Struct):
            for v in ns.functions:
                if not v.name:
                    continue
                if v.file.name == 'imgui.h':
                    continue
                if v.name.startswith('operator '):
                    continue
                if any(
                        isinstance(p.typeref.ref, cpptypeinfo.VaList)
                        for p in v.params):
                    continue
                values.append(function_str(v))

    t = Template('''{{ headline }}
{{ using }}

namespace {{ namespace }}
{
    public static class CImGui
    {
        const string DLLNAME = "cimgui.dll";

{%- for value in values %}

        {{ value }}
{%- endfor %}
    }
}
''')
    with open(dst, 'w') as f:
        f.write(
            t.render(headline=HEADLINE,
                     using=USING,
                     namespace=NAMESPACE_NAME,
                     values=values))


def main(imgui_h: pathlib.Path, cimgui_h: pathlib.Path, root: pathlib.Path):
    root_ns = cpptypeinfo.push_namespace()
    with cpptypeinfo.tmp_from_source('''
#include <imgui.h>
#include <cimgui.h>
    ''') as path:
        cpptypeinfo.parse_header(
            path,
            cpp_flags=[
                f'-I{imgui_h.parent}',
                f'-I{cimgui_h.parent}',
            ],
            include_path_list=[str(imgui_h), str(cimgui_h)])
    cpptypeinfo.pop_namespace()

    if root.exists():
        shutil.rmtree(root)

    root_ns.resolve_typedef('ImS8')
    root_ns.resolve_typedef('ImS16')
    root_ns.resolve_typedef('ImS32')
    root_ns.resolve_typedef('ImS64')
    root_ns.resolve_typedef('ImU8')
    root_ns.resolve_typedef('ImU16')
    root_ns.resolve_typedef('ImU32')
    root_ns.resolve_typedef('ImU64')

    for ns in root_ns.traverse():
        if not isinstance(ns, cpptypeinfo.Struct):
            generate(ns, root)

    #
    # functions
    #
    generate_functions(root_ns, root)


if __name__ == '__main__':
    if (len(sys.argv) > 3):
        imgui_h = pathlib.Path(sys.argv[1])
        cimgui_h = pathlib.Path(sys.argv[2])
        dst = pathlib.Path(sys.argv[3])
        main(imgui_h, cimgui_h, dst)
    else:
        dst = HERE / 'cimgui_cs'
        main(IMGUI_H, CIMGUI_H, dst)
