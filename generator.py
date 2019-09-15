import pathlib
import shutil
from jinja2 import Template
import cpptypeinfo
HERE = pathlib.Path(__file__).absolute().parent
CIMGUI_H = HERE / 'libs/cimgui/cimgui.h'
IMGUI_H = HERE / 'libs/imgui/imgui.h'


def generate_enum(enum: cpptypeinfo.Enum, root: pathlib.Path, namespace: str,
                  is_flags: bool, typename_filter, valuename_filter):

    type_name = typename_filter(enum.type_name)

    dst = root / f'{type_name}.cs'
    t = Template('''// python generate
namespace {{ namespace }}
{
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
            t.render(namespace=namespace,
                     attribute='[Flags]' if is_flags else '',
                     type_name=type_name,
                     values=[
                         valuename_filter(enum.type_name, v)
                         for v in enum.values
                     ]))


def generate_typedef(typedef: cpptypeinfo.Typedef, root: pathlib.Path,
                     namespace: str):

    if isinstance(
            typedef.src,
            cpptypeinfo.Struct) and typedef.type_name == typedef.src.type_name:
        # skip typedef struct same name
        return

    dst = root / f'{typedef.type_name}.cs'

    t = Template('''// python generate
namespace {{ namespace }}
{
    public struct {{ type_name }}
    {
        public {{ type }} Value;
    }
}
''')

    typedef_type = str(typedef.src)
    if isinstance(typedef.src, cpptypeinfo.Pointer):
        typedef_type = 'IntPtr'

    with open(dst, 'w') as f:
        f.write(
            t.render(namespace=namespace,
                     type_name=typedef.type_name,
                     type=typedef_type))


def generate_struct(decl: cpptypeinfo.Struct, root: pathlib.Path,
                    namespace: str):

    dst = root / f'{decl.type_name}.cs'
    t = Template('''// python generate
namespace {{ namespace }}
{
    {{ attribute }}
    public struct {{ type_name }}
    {
{%- for value in values %}
        public {{ value }};
{%- endfor %}
    }
}
''')

    def field_str(f):
        if isinstance(f.type, cpptypeinfo.Typedef):
            if isinstance(f.type.src, cpptypeinfo.Pointer):
                return f'IntPtr {f.name}'
            elif f.type.type_name.endswith('Callback'):
                return f'IntPtr {f.name}'
            else:
                return f'{f.type.type_name} {f.name}'
        elif isinstance(f.type, cpptypeinfo.Pointer):
            return f'IntPtr {f.name}'
        else:
            return f'{f.type} {f.name}'

    with open(dst, 'w') as f:
        f.write(
            t.render(namespace=namespace,
                     type_name=decl.type_name,
                     values=[field_str(f) for f in decl.fields]))


def generate(ns: cpptypeinfo.Namespace, root: pathlib.Path):
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

    namespace_name = 'SharpImGui'
    # enum
    removes = []
    for k, v in ns.user_type_map.items():
        if isinstance(v, cpptypeinfo.Enum):

            generate_enum(v, root, namespace_name,
                          v.type_name.endswith('Flags_'), typename_filter,
                          valuename_filter)
            removes.append(v.type_name[:-1])

    # except enum
    for k, v in ns.user_type_map.items():
        if isinstance(v, cpptypeinfo.Enum):
            pass
        elif isinstance(v, cpptypeinfo.Typedef):
            if v.type_name in removes:
                continue
            if v.type_name.endswith('Callback'):
                continue
            generate_typedef(v, root, namespace_name)
        elif isinstance(v, cpptypeinfo.Struct):
            generate_struct(v, root, namespace_name)
        else:
            raise Exception()


def main(dst: pathlib.Path):
    root = cpptypeinfo.push_namespace()
    with cpptypeinfo.tmp_from_source('''
#include <imgui.h>
#include <cimgui.h>
    ''') as path:
        cpptypeinfo.parse_header(path,
                                 cpp_flags=[
                                     f'-I{IMGUI_H.parent}',
                                     f'-I{CIMGUI_H.parent}',
                                 ],
                                 include_path_list=[str(IMGUI_H), str(CIMGUI_H)])
    cpptypeinfo.pop_namespace()

    if dst.exists():
        shutil.rmtree(dst)

    root.resolve('ImS8')
    root.resolve('ImS16')
    root.resolve('ImS32')
    root.resolve('ImS64')
    root.resolve('ImU8')
    root.resolve('ImU16')
    root.resolve('ImU32')
    root.resolve('ImU64')

    for ns in root.traverse():
        if not isinstance(ns, cpptypeinfo.Struct):
            generate(ns, dst)


if __name__ == '__main__':
    dst = HERE / 'cimgui_cs'
    main(dst)
