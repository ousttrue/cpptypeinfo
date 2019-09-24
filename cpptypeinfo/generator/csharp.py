import pathlib
import re
from typing import Dict, NamedTuple, List
import enum
import cpptypeinfo
from jinja2 import Template

HEADLINE = f'// generated cpptypeinfo-{cpptypeinfo.VERSION}'
USING = '''using System;
using System.Runtime.InteropServices;
using System.Numerics;
'''


class CSMarshalType(NamedTuple):
    type: str
    marshal_as: str = ''


cstype_map: Dict[cpptypeinfo.Type, CSMarshalType] = {
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

# for function param
cstype_pointer_map: Dict[cpptypeinfo.Type, CSMarshalType] = {
    cpptypeinfo.Pointer(cpptypeinfo.Int8().to_const()):
    CSMarshalType('string', 'MarshalAs(UnmanagedType.LPUTF8Str)'),
    cpptypeinfo.Pointer(cpptypeinfo.Bool()):
    CSMarshalType('ref bool', 'MarshalAs(UnmanagedType.U1)'),
    cpptypeinfo.Pointer(cpptypeinfo.Float()):
    CSMarshalType('ref float'),
}


class ExportFlag(enum.Flag):
    StructField = enum.auto()
    FunctionReturn = enum.auto()
    FunctionParam = enum.auto()
    All = StructField | FunctionReturn | FunctionParam


def to_cs(decl: cpptypeinfo.Type, context: ExportFlag) -> CSMarshalType:
    if not decl:
        # bug
        print('### bug ###')
        return CSMarshalType('IntPtr')

    cs_type = cstype_map.get(decl)
    if cs_type:
        return cs_type

    if context & ExportFlag.FunctionParam:
        cs_type = cstype_pointer_map.get(decl)
        if cs_type:
            return cs_type

    if isinstance(decl, cpptypeinfo.Void):
        return CSMarshalType('void')
    elif isinstance(decl, cpptypeinfo.Array):
        return CSMarshalType('IntPtr')
    elif isinstance(decl, cpptypeinfo.Pointer):
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

    cstype = to_cs(typedef.typeref.ref, ExportFlag.StructField)
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
        cstype = to_cs(f.typeref.ref, ExportFlag.StructField)
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
                     file=decl.file.name if decl.file else '',
                     line=decl.line))


REF = re.compile(r'\bref\b')
REF_BOOL = re.compile(r'\bref bool\b')

RE_VEC2 = re.compile(r'ImVec2\((.*)\)')


def cs_value(src: str) -> str:
    if not src:
        return
    if src in ['NULL', 'ImVec2(0,0)', 'ImVec4(0,0,0,0)', 'false']:
        return 'default'  # IntPtr.Zero
    try:
        int(src)
        return src
    except:
        pass
    if src == 'true':
        return src
    if src.startswith('ImVec2('):
        # return f'new Vector2({src[7:-1]})'
        return None
    if src.startswith('ImVec4('):
        # return f'new Vector4({src[7:-1]})'
        return None
    if src[-1] == 'f':
        try:
            float(src[:-1])
            if src[0] == '.':
                src = '0' + src
            if src[-2] == '.':
                src = src[:-1] + '0f'
            return src
        except:
            pass
    else:
        try:
            float(src)
            if src[0] == '.':
                src = '0' + src
            if src[-1] == '.':
                src += '0'
            return src
        except:
            pass
    if src == 'FLT_MAX':
        return 'float.MaxValue'
    if src.startswith('sizeof(float)'):
        return '4'
    if src[0] == '"' and src[-1] == '"':
        return src
    raise Exception(src)


def generate_functions(root_ns: cpptypeinfo.Namespace,
                       context: CSContext,
                       class_name: str,
                       dll_name: str,
                       filter=None):
    def to_cs_param(p: cpptypeinfo.Param, cstype: CSMarshalType,
                    has_default: bool):
        if cstype.marshal_as:
            param_attr = f'[{cstype.marshal_as}]'
        else:
            param_attr = ''

        if has_default:
            return f'{param_attr}{cstype.type} {escape_symbol(p.name)} = {cs_value(p.value)}'
        else:
            return f'{param_attr}{cstype.type} {escape_symbol(p.name)}'

    def params_str(params: List[cpptypeinfo.Param],
                   cs_params: List[CSMarshalType], start: int):
        i = 0
        for p, cs in zip(params, cs_params):
            yield to_cs_param(p, cs, (i >= start and p.value))
            i += 1

    def function_call(v: cpptypeinfo.Function, ret_attr: str, ret_type: str,
                      cs_params: List[CSMarshalType], start: int):
        params = [p for p in params_str(v.params, cs_params, start)]
        return f'''// {v.file.name}:{v.line}
        [DllImport(DLLNAME, EntryPoint="{v.mangled_name}")]{ret_attr}
        public static extern {ret_type} {v.name}({", ".join(params)});'''

    def function_str(v: cpptypeinfo.Function):
        cs_params = [
            to_cs(p.typeref.ref, ExportFlag.FunctionParam) for p in v.params
        ]

        # return
        cstype = to_cs(v.result.ref, ExportFlag.FunctionReturn)
        if cstype.marshal_as:
            ret_attr = f'\n        [return: {cstype.marshal_as}]'
        else:
            ret_attr = ''

        # 一番後ろの ref 引数
        ref_index = -1
        for i in range(len(cs_params) - 1, -1, -1):
            if REF.search(cs_params[i].type):
                ref_index = i
                break
        not_cs_const = -1
        for i in range(len(cs_params) - 1, -1, -1):
            if not cs_value(v.params[i].value):
                not_cs_const = i
                break

        start = max(ref_index, not_cs_const) + 1

        yield function_call(v, ret_attr, cstype.type, cs_params, start)

        # ref bool のデフォルト引数
        if ref_index >= 0:
            if REF_BOOL.search(cs_params[ref_index].type):
                if (ref_index >= 0 and ref_index >= not_cs_const):
                    if v.params[ref_index].value == 'NULL':
                        # ref bool を IntPtr にして default で省略できるようにする
                        cs_params[ref_index] = CSMarshalType('IntPtr')
                        yield function_call(v, ret_attr, cstype.type,
                                            cs_params, start - 1)

    values = []
    for ns in root_ns.traverse():
        if not isinstance(ns, cpptypeinfo.Struct):
            for v in ns.functions:
                if not v.name:
                    continue
                if v.name.startswith('operator '):
                    continue
                # if not v.extern_c:
                #     continue
                if any(
                        isinstance(p.typeref.ref, cpptypeinfo.VaList)
                        for p in v.params):
                    continue
                if filter and not filter(v):
                    continue

                for value in function_str(v):
                    values.append(value)

    t = Template('''{{ headline }}
{{ using }}

namespace {{ namespace }}
{
    public static class {{ class_name }}
    {
        const string DLLNAME = "{{ dll_name }}";

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
                     values=values,
                     class_name=class_name,
                     dll_name=dll_name))
