import pathlib
import sys
import shutil
# from typing import Tuple, Optional, Dict, List
from jinja2 import Template
import cpptypeinfo
from cpptypeinfo.generator import csharp
HERE = pathlib.Path(__file__).absolute().parent
CIMGUI_H = HERE / 'libs/cimgui/cimgui.h'
IMGUI_H = HERE / 'libs/imgui/imgui.h'

NAMESPACE_NAME = 'SharpImGui'


def generate_imguiio(root_ns: cpptypeinfo.Namespace,
                     context: csharp.CSContext):
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
    with open(context.path, 'w') as w:
        w.write(
            t.render(headline=context.headline,
                     using=context.using,
                     namespace=context.namespace,
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
                csharp.generate_enum(
                    v,
                    csharp.CSContext(root / f'{v.type_name}.cs',
                                     NAMESPACE_NAME))
            elif isinstance(v, cpptypeinfo.Typedef):
                if v.type_name.endswith('Callback'):
                    continue
                csharp.generate_typedef(
                    v,
                    csharp.CSContext(root / f'{v.type_name}.cs',
                                     NAMESPACE_NAME))
            elif isinstance(v, cpptypeinfo.Struct):
                csharp.generate_struct(
                    v,
                    csharp.CSContext(root / f'{v.type_name}.cs',
                                     NAMESPACE_NAME))
            else:
                raise Exception()

    csharp.generate_functions(
        root_ns, csharp.CSContext(root / 'CImGui.cs', NAMESPACE_NAME))

    generate_imguiio(root_ns,
                     csharp.CSContext(root / 'ImGuiIO.cs', NAMESPACE_NAME))


if __name__ == '__main__':
    if (len(sys.argv) > 3):
        dst = pathlib.Path(sys.argv[1])
        main(dst, *[pathlib.Path(x) for x in sys.argv[2:]])
    else:
        dst = HERE / 'cimgui_cs'
        main(dst, IMGUI_H, CIMGUI_H)
