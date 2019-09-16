import pathlib
from typing import Optional, Tuple, Dict, NamedTuple
import cpptypeinfo
from jinja2 import Template

HEADLINE = f'// generated cpptypeinfo-{cpptypeinfo.VERSION}'
USING = '''using System;
using System.Runtime.InteropServices;'''

cs_type_map: Dict[cpptypeinfo.PrimitiveType, Tuple[Optional[str], str]] = {
    cpptypeinfo.Int8(): (None, 'sbyte'),
    cpptypeinfo.Int16(): (None, 'short'),
    cpptypeinfo.Int32(): (None, 'int'),
    cpptypeinfo.Int64(): (None, 'long'),
    cpptypeinfo.UInt8(): (None, 'byte'),
    cpptypeinfo.UInt16(): (None, 'ushort'),
    cpptypeinfo.UInt32(): (None, 'uint'),
    cpptypeinfo.UInt64(): (None, 'ulong'),
    cpptypeinfo.Float(): (None, 'float'),
    cpptypeinfo.Double(): (None, 'double'),
    cpptypeinfo.Bool(): ('MarshalAs(UnmanagedType.U1)', 'bool'),
}


def to_cs(decl: cpptypeinfo.Type) -> Tuple[Optional[str], str]:
    if not decl:
        # bug
        print('### bug ###')
        return (None, 'IntPtr')

    if isinstance(decl, cpptypeinfo.PrimitiveType):
        cs_type = cs_type_map.get(decl)
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


def escape_symbol(name: str):
    if name in CS_SYMBOLS:
        return '_' + name
    return name


class CSContext(NamedTuple):
    path: pathlib.Path
    namespace: str
    headline: str = HEADLINE
    using: str = USING


def generate_enum(enum: cpptypeinfo.Enum, context: CSContext):

    # type_name = typename_filter(enum.type_name)

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
    with open(context.path, 'w') as f:
        f.write(
            t.render(headline=context.headline,
                     using=context.using,
                     namespace=context.namespace,
                     attribute='[Flags]' if enum.is_flag else '',
                     type_name=enum.type_name,
                     values=enum.values,
                     file=enum.file.name,
                     line=enum.line))


def generate_typedef(typedef: cpptypeinfo.Typedef, context: CSContext):

    if isinstance(
            typedef.typeref,
            cpptypeinfo.Struct) and typedef.type_name == typedef.src.type_name:
        # skip typedef struct same name
        return

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

    with open(context.path, 'w') as f:
        f.write(
            t.render(headline=context.headline,
                     using=context.using,
                     namespace=context.namespace,
                     type_name=typedef.type_name,
                     type=typedef_type,
                     file=typedef.file.name,
                     line=typedef.line))


def generate_struct(decl: cpptypeinfo.Struct, context: CSContext):

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

    with open(context.path, 'w') as f:
        f.write(
            t.render(headline=context.headline,
                     using=context.using,
                     namespace=context.namespace,
                     type_name=decl.type_name,
                     values=[field_str(f) for f in decl.fields],
                     file=decl.file.name,
                     line=decl.line))


def generate_functions(root_ns: cpptypeinfo.Namespace, context: CSContext):
    def to_cs_param(p: cpptypeinfo.Param):
        param_attr, param = to_cs(p.typeref.ref)
        if param_attr:
            param_attr = f'[{param_attr}]'
        else:
            param_attr = ''
        return f'{param_attr}{param} {escape_symbol(p.name)}'

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
    with open(context.path, 'w') as f:
        f.write(
            t.render(headline=context.headline,
                     using=context.using,
                     namespace=context.namespace,
                     values=values))
