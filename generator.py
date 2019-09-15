import pathlib
from jinja2 import Template
import cpptypeinfo
HERE = pathlib.Path(__file__).absolute().parent
CIMGUI_H = HERE / 'libs/cimgui/cimgui.h'


def generate_enum(enum: cpptypeinfo.Enum, root: pathlib.Path, namespace: str,
                  is_flags: bool):
    dst = root / f'{enum.type_name}.cs'
    t = Template('''// python generate
namespace {{ namespace }}
{
    {{ attribute }}
    public enum {{ type_name }}
    {
{%- for value in values %}
        {{ value.name }} = {{ value.value }}
{%- endfor %}
    }
}
''')
    with open(dst, 'w') as f:
        f.write(
            t.render(namespace=namespace,
                     attribute='[Flags]' if is_flags else '',
                     type_name=enum.type_name,
                     values=enum.values))


def generate(ns: cpptypeinfo.Namespace, root: pathlib.Path):
    root.mkdir(parents=True, exist_ok=True)

    for k, v in ns.user_type_map.items():
        if isinstance(v, cpptypeinfo.Enum):
            generate_enum(v, root, 'SharpImGui', v.type_name.endswith('Flags_'))


def main(dst: pathlib.Path):
    root = cpptypeinfo.push_namespace()
    cpptypeinfo.parse_header(CIMGUI_H,
                             cpp_flags=['-DCIMGUI_DEFINE_ENUMS_AND_STRUCTS'])
    cpptypeinfo.pop_namespace()

    for level, ns in root.traverse():
        if not isinstance(ns, cpptypeinfo.Struct):
            generate(ns, dst)


if __name__ == '__main__':
    dst = HERE / 'cimgui_cs'
    main(dst)
