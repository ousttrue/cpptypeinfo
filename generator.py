import pathlib
import sys
import shutil
from typing import NamedTuple
from jinja2 import Template
import cpptypeinfo
from cpptypeinfo.generator import csharp
HERE = pathlib.Path(__file__).absolute().parent
CIMGUI_H = HERE / 'libs/cimgui/cimgui.h'
IMGUI_H = HERE / 'libs/imgui/imgui.h'

NAMESPACE_NAME = 'SharpImGui'


class PropInfo(NamedTuple):
    name: str
    offset: int
    cstype: str
    to_cstype: str
    readfunc: str
    from_cstype: str
    writefunc: str

    def to_cs(self):
        return f'''// offsetof: {self.offset}
        public {self.cstype} {self.name}
        {{
            get => {self.to_cstype}(Marshal.{self.readfunc}(IntPtr.Add(m_p, {self.offset})));
            set => Marshal.{self.writefunc}(IntPtr.Add(m_p, {self.offset}), {self.from_cstype});
        }}'''


def create_property(f) -> PropInfo:
    if isinstance(f.typeref.ref, cpptypeinfo.Int32):
        return PropInfo(
            f.name,
            f.offset,
            'int',
            to_cstype='',
            readfunc='ReadInt32',  #
            from_cstype='value',
            writefunc='WriteInt32')
    elif isinstance(f.typeref.ref, cpptypeinfo.Enum):
        return PropInfo(
            f.name,
            f.offset,
            f.typeref.ref.type_name,
            to_cstype=f'({f.typeref.ref.type_name})',
            readfunc='ReadInt32',  #
            from_cstype='(int)value',
            writefunc='WriteInt32')
    elif isinstance(f.typeref.ref, cpptypeinfo.Float):
        return PropInfo(
            f.name,
            f.offset,
            'float',
            to_cstype='BitConverter.Int32BitsToSingle',
            readfunc='ReadInt32',  #
            from_cstype='BitConverter.SingleToInt32Bits(value)',
            writefunc='WriteInt32')
    elif isinstance(f.typeref.ref, cpptypeinfo.Pointer):
        return PropInfo(
            f.name,
            f.offset,
            'IntPtr',
            to_cstype='new IntPtr',
            readfunc='ReadInt64',  #
            from_cstype='value.ToInt64()',
            writefunc='WriteInt64')
    else:
        # print(f.typeref.ref)
        pass


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
        value = create_property(f)
        if value:
            values.append(value.to_cs())

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

    root_ns = cpptypeinfo.parse_headers(
        *paths,
        cpp_flags=[
            '-target',
            'x86_64-windows-msvc'
            '-DIMGUI_DISABLE_OBSOLETE_FUNCTIONS=1',
            '-DIMGUI_USER_CONFIG=<imconfig_dll.h>',
        ])

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
    root_ns.resolve_typedef_void_p()
    process_enum(root_ns)

    cpptypeinfo.push_namespace(root_ns)
    # vector2
    vector2 = cpptypeinfo.Struct('PodImVec2')
    csharp.cstype_map[vector2] = csharp.CSMarshalType('Vector2')
    csharp.cstype_pointer_map[cpptypeinfo.Pointer(
        vector2)] = csharp.CSMarshalType('ref Vector2')
    csharp.cstype_pointer_map[cpptypeinfo.Pointer(
        vector2.to_const())] = csharp.CSMarshalType('ref Vector2')
    csharp.cstype_pointer_map[cpptypeinfo.Array(
        cpptypeinfo.Float(), 2)] = csharp.CSMarshalType('ref Vector2')
    # vector2
    vector2 = cpptypeinfo.Struct('ImVec2')
    csharp.cstype_map[vector2] = csharp.CSMarshalType('Vector2')
    csharp.cstype_pointer_map[cpptypeinfo.Pointer(
        vector2)] = csharp.CSMarshalType('ref Vector2')
    csharp.cstype_pointer_map[cpptypeinfo.Pointer(
        vector2.to_const())] = csharp.CSMarshalType('ref Vector2')
    csharp.cstype_pointer_map[cpptypeinfo.Array(
        cpptypeinfo.Float(), 2)] = csharp.CSMarshalType('ref Vector2')
    # vector3
    vector3 = cpptypeinfo.Struct('ImVec3')
    csharp.cstype_map[vector3] = csharp.CSMarshalType('Vector3')
    csharp.cstype_pointer_map[cpptypeinfo.Pointer(
        vector3)] = csharp.CSMarshalType('ref Vector3')
    csharp.cstype_pointer_map[cpptypeinfo.Pointer(
        vector3.to_const())] = csharp.CSMarshalType('ref Vector3')
    csharp.cstype_pointer_map[cpptypeinfo.Array(
        cpptypeinfo.Float(), 3)] = csharp.CSMarshalType('ref Vector3')
    # vector4
    vector4 = cpptypeinfo.Struct('ImVec4')
    csharp.cstype_map[vector4] = csharp.CSMarshalType('Vector4')
    csharp.cstype_pointer_map[cpptypeinfo.Pointer(
        vector4)] = csharp.CSMarshalType('ref Vector4')
    csharp.cstype_pointer_map[cpptypeinfo.Pointer(
        vector4.to_const())] = csharp.CSMarshalType('ref Vector4')
    csharp.cstype_pointer_map[cpptypeinfo.Array(
        cpptypeinfo.Float(), 4)] = csharp.CSMarshalType('ref Vector4')

    cpptypeinfo.pop_namespace()

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

    # if v.name.startswith('ImVector_'):
    #     continue
    # if v.file.name == 'imgui.h':
    #     continue
    csharp.generate_functions(
        root_ns, csharp.CSContext(root / 'ImGui.cs', NAMESPACE_NAME), 'ImGui',
        'imgui.dll')

    generate_imguiio(root_ns,
                     csharp.CSContext(root / 'ImGuiIO.cs', NAMESPACE_NAME))


if __name__ == '__main__':
    if (len(sys.argv) > 3):
        dst = pathlib.Path(sys.argv[1])
        main(dst, *[pathlib.Path(x) for x in sys.argv[2:]])
    else:
        dst = HERE / 'cimgui_cs'
        main(dst, IMGUI_H, CIMGUI_H)
