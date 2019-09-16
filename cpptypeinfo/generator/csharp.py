import pathlib
from typing import Dict, NamedTuple
import cpptypeinfo
from jinja2 import Template

HEADLINE = f'// generated cpptypeinfo-{cpptypeinfo.VERSION}'
USING = '''using System;
using System.Runtime.InteropServices;'''


class CSMarshalType(NamedTuple):
    type: str
    marshal_as: str = ''


cstype_map: Dict[cpptypeinfo.PrimitiveType, CSMarshalType] = {
    cpptypeinfo.Int8(): CSMarshalType('sbyte'),
    cpptypeinfo.Int16(): CSMarshalType('short'),
    cpptypeinfo.Int32(): CSMarshalType('int'),
    cpptypeinfo.Int64(): CSMarshalType('long'),
    cpptypeinfo.UInt8(): CSMarshalType('byte'),
    cpptypeinfo.UInt16(): CSMarshalType('ushort'),
    cpptypeinfo.UInt32(): CSMarshalType('uint'),
    cpptypeinfo.UInt64(): CSMarshalType('ulong'),
    cpptypeinfo.Float(): CSMarshalType('float'),
    cpptypeinfo.Double(): CSMarshalType('double'),
    cpptypeinfo.Bool(): CSMarshalType('bool', 'MarshalAs(UnmanagedType.U1)'),
}


def to_cs(decl: cpptypeinfo.Type) -> CSMarshalType:
    '''
    ToDo: context: struct field, function return, function param
    '''
    if not decl:
        # bug
        print('### bug ###')
        return CSMarshalType('IntPtr')

    if isinstance(decl, cpptypeinfo.PrimitiveType):
        cs_type = cstype_map.get(decl)
        if cs_type:
            return cs_type

    if isinstance(decl, cpptypeinfo.Void):
        return CSMarshalType('void')
    elif isinstance(decl, cpptypeinfo.Array):
        return CSMarshalType('IntPtr')
    elif isinstance(decl, cpptypeinfo.Pointer):
        if isinstance(decl.typeref.ref, cpptypeinfo.Bool):
            return CSMarshalType('ref bool', 'MarshalAs(UnmanagedType.U1)')
        else:
            return CSMarshalType('IntPtr')
    elif isinstance(decl, cpptypeinfo.Function):
        return CSMarshalType('IntPtr')
    elif isinstance(decl, cpptypeinfo.Enum):
        return CSMarshalType(decl.type_name)
    elif isinstance(decl, cpptypeinfo.Struct):
        return CSMarshalType(decl.type_name)
    elif isinstance(decl, cpptypeinfo.Typedef):
        if isinstance(decl.get_concrete_type(), cpptypeinfo.Function):
            return CSMarshalType('IntPtr')
        else:
            return CSMarshalType(decl.type_name)
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

    cstype = to_cs(typedef.typeref.ref)
    if cstype.marshal_as:
        typedef_attr = f'[{cstype.marshal_as}]'
    else:
        typedef_attr = ''

    typedef_type = f'{typedef_attr}public {cstype.type} Value'

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
        cstype = to_cs(f.typeref.ref)
        if cstype.marshal_as:
            field_attr = f'[{cstype.marshal_as}]'
        else:
            field_attr = ''
        return f'''// offsetof: {f.offset}
        {field_attr}public {cstype.type} {f.name}'''

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
        cstype = to_cs(p.typeref.ref)
        if cstype.marshal_as:
            param_attr = f'[{cstype.marshal_as}]'
        else:
            param_attr = ''
        return f'{param_attr}{cstype.type} {escape_symbol(p.name)}'

    def function_str(v: cpptypeinfo.Function):
        params = [to_cs_param(p) for p in v.params]
        cstype = to_cs(v.result.ref)
        if cstype.marshal_as:
            ret_attr = f'\n        [return: {cstype.marshal_as}]\n'
        else:
            ret_attr = ''
        return f'''// {v.file.name}:{v.line}
        [DllImport(DLLNAME)]{ret_attr}
        public static extern {cstype.type} {v.name}({", ".join(params)});'''

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
