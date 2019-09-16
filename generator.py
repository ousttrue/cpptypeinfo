import pathlib
import sys
import shutil
from typing import Tuple, Optional, Dict, List
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
    elif isinstance(decl, cpptypeinfo.Enum):
        return (None, decl.type_name)
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


def generate_enum(enum: cpptypeinfo.Enum, root: pathlib.Path):

    # type_name = typename_filter(enum.type_name)

    dst = root / f'{enum.type_name}.cs'
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
                     attribute='[Flags]' if enum.is_flag else '',
                     type_name=enum.type_name,
                     values=enum.values,
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
        return f'''// offsetof: {f.offset}
        {field_attr}public {field_type} {f.name}'''

    with open(dst, 'w') as f:
        f.write(
            t.render(headline=HEADLINE,
                     using=USING,
                     namespace=NAMESPACE_NAME,
                     type_name=decl.type_name,
                     values=[field_str(f) for f in decl.fields],
                     file=decl.file.name,
                     line=decl.line))


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
                if v.name.startswith('ImVector_'):
                    continue
                if v.file.name == 'imgui.h':
                    continue
                if v.name.startswith('operator '):
                    continue
                # if not v.extern_c:
                #     continue
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


def generate_imguiio(root_ns: cpptypeinfo.Namespace, root: pathlib.Path):
    def find_struct() -> cpptypeinfo.Struct:
        for ns in root_ns.traverse():
            for k, v in ns.user_type_map.items():
                if k == 'ImGuiIO' and isinstance(v, cpptypeinfo.Struct):
                    return v
        raise Exception()

    imguiio = find_struct()
    values = []
    for f in imguiio.fields:
        if f.typeref.ref == cpptypeinfo.Int32:
            value = f'''public int {f.name}
        {{
            get => (int)Marshal.ReadInt32(IntPtr.Add(m_p, {f.offset}));
            set => Marshal.WriteInt32(IntPtr.Add(m_p, {f.offset}), (int)value);
        }}'''
            values.append(value)
        elif isinstance(f.typeref.ref, cpptypeinfo.Enum):
            type_name = f.typeref.ref.type_name
            value = f'''public {type_name} {f.name}
        {{
            get => ({type_name})Marshal.ReadInt32(IntPtr.Add(m_p, {f.offset}));
            set => Marshal.WriteInt32(IntPtr.Add(m_p, {f.offset}), (int)value);
        }}'''
            values.append(value)

    t = Template('''{{ headline }}
{{ using }}

namespace {{ namespace }}
{
    public struct ImGuiIO
    {
        public static implicit operator ImGuiIO(IntPtr p)
        {
            return new ImGuiIO(p);
        }

        readonly IntPtr m_p;

        public ImGuiIO(IntPtr ptr)
        {
            m_p = ptr;
        }

{%- for value in values %}
        {{ value }}
{%- endfor %}
    }
}
''')
    with open(root / 'ImGuiIO.cs', 'w') as f:
        f.write(
            t.render(headline=HEADLINE,
                     using=USING,
                     namespace=NAMESPACE_NAME,
                     values=values))


def process_enum(root_ns: cpptypeinfo.Namespace):
    '''
    enum XXXFlags_ と typedef int XXXFlags
    をまとめて enum XXXFlags にする。
    '''
    for ns in root_ns.traverse():
        while True:
            found = None
            for k, v in ns.user_type_map.items():
                if not k:
                    continue
                if isinstance(v, cpptypeinfo.Enum) and k.endswith('_'):
                    found = v
                    break
            if not found:
                return

            if k.endswith('Flags_'):
                v.is_flag = True

            # 値をrename
            def valuename_filter(type_name: str, src: cpptypeinfo.EnumValue):
                if src.name.startswith(type_name):
                    return cpptypeinfo.EnumValue(src.name[len(type_name):],
                                                 src.value)
                else:
                    return src

            v.values = [valuename_filter(v.type_name, x) for x in v.values]

            # renameして再登録
            ns.user_type_map.pop(v.type_name)
            v.type_name = v.type_name[:-1]

            old = ns.user_type_map.get(v.type_name)
            if old:
                # remove typdef
                root_ns.resolve(old, v)
            ns.user_type_map[v.type_name] = v


def main(root: pathlib.Path, *paths: pathlib.Path):
    print(f'{[x.name for x in paths]} => {root}')

    root_ns = cpptypeinfo.parse_headers(*paths)

    #
    # preprocess
    #
    if root.exists():
        shutil.rmtree(root)

    root_ns.resolve_typedef_by_name('ImS8')
    root_ns.resolve_typedef_by_name('ImS16')
    root_ns.resolve_typedef_by_name('ImS32')
    root_ns.resolve_typedef_by_name('ImS64')
    root_ns.resolve_typedef_by_name('ImU8')
    root_ns.resolve_typedef_by_name('ImU16')
    root_ns.resolve_typedef_by_name('ImU32')
    root_ns.resolve_typedef_by_name('ImU64')
    root_ns.resolve_typedef_struct_tag()
    process_enum(root_ns)



    #
    # process each namespace from root
    #
    root.mkdir(parents=True, exist_ok=True)
    for ns in root_ns.traverse():

        for k, v in ns.user_type_map.items():
            if isinstance(v, cpptypeinfo.Enum):
                generate_enum(v, root)
            elif isinstance(v, cpptypeinfo.Typedef):
                if v.type_name.endswith('Callback'):
                    continue
                generate_typedef(v, root)
            elif isinstance(v, cpptypeinfo.Struct):
                generate_struct(v, root)
            else:
                raise Exception()

    generate_functions(root_ns, root)

    generate_imguiio(root_ns, root)


if __name__ == '__main__':
    if (len(sys.argv) > 3):
        dst = pathlib.Path(sys.argv[1])
        main(dst, *[pathlib.Path(x) for x in sys.argv[2:]])
    else:
        dst = HERE / 'cimgui_cs'
        main(dst, IMGUI_H, CIMGUI_H)
