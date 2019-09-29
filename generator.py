import pathlib
import sys
import shutil
from typing import NamedTuple
from jinja2 import Template
import cpptypeinfo
from cpptypeinfo.usertype import (Namespace, Pointer, Struct, Typedef)
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
    elif isinstance(f.typeref.ref, Pointer):
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


def generate_imguiio(root_ns: Namespace, context: csharp.CSContext):
    def find_struct() -> Struct:
        for ns in root_ns.traverse():
            for k, v in ns.user_type_map.items():
                if k == 'ImGuiIO' and isinstance(v, Struct):
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


def process_enum(parser: cpptypeinfo.TypeParser) -> None:
    '''
    enum XXXFlags_ と typedef int XXXFlags
    をまとめて enum XXXFlags にする。
    '''
    for ns in parser.root_namespace.traverse():
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

            print(f'process: {k} {v.type_name}')
            old = ns.user_type_map.get(v.type_name)
            if old:
                # remove typdef
                parser.resolve(old, v)
            ns.user_type_map[v.type_name] = v


def main(root: pathlib.Path, *paths: pathlib.Path):
    print(f'{[x.name for x in paths]} => {root}')

    parser = cpptypeinfo.TypeParser()

    # predefine
    parser.struct('PodImVec2', [])
    # win32API
    parser.typedef('LRESULT', Pointer(cpptypeinfo.Void()))
    parser.typedef('HWND', Pointer(cpptypeinfo.Void()))
    parser.typedef('UINT', cpptypeinfo.UInt32())
    parser.typedef('WPARAM', Pointer(cpptypeinfo.Void()))
    parser.typedef('LPARAM', Pointer(cpptypeinfo.Void()))

    # std
    parser.push_namespace('std')
    parser.parse('struct array')
    parser.pop_namespace()
    # DirectX
    parser.push_namespace('DirectX')
    parser.parse('struct XMFLOAT4X4')
    parser.pop_namespace()
    #

    root_ns = cpptypeinfo.parse_headers(
        parser,
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

    process_enum(parser)
    parser.resolve_typedef_by_name('ImS8')
    parser.resolve_typedef_by_name('ImS16')
    parser.resolve_typedef_by_name('ImS32')
    parser.resolve_typedef_by_name('ImS64')
    parser.resolve_typedef_by_name('ImU8')
    parser.resolve_typedef_by_name('ImU16')
    parser.resolve_typedef_by_name('ImU32')
    parser.resolve_typedef_by_name('ImU64')
    parser.resolve_typedef_by_name('UINT')
    parser.resolve_typedef_struct_tag()
    parser.resolve_typedef_void_p()

    # vector2
    vector2 = parser.struct('PodImVec2')
    csharp.cstype_map[vector2] = csharp.CSMarshalType('Vector2')
    csharp.cstype_pointer_map[vector2] = csharp.CSMarshalType('ref Vector2')
    # vector2
    vector2 = parser.struct('ImVec2')
    csharp.cstype_map[vector2] = csharp.CSMarshalType('Vector2')
    csharp.cstype_pointer_map[vector2] = csharp.CSMarshalType('ref Vector2')
    # vector3
    vector3 = parser.struct('ImVec3')
    csharp.cstype_map[vector3] = csharp.CSMarshalType('Vector3')
    csharp.cstype_pointer_map[vector3] = csharp.CSMarshalType('ref Vector3')
    # vector4
    vector4 = parser.struct('ImVec4')
    csharp.cstype_map[vector4] = csharp.CSMarshalType('Vector4')
    csharp.cstype_pointer_map[vector4] = csharp.CSMarshalType('ref Vector4')
    # Im3d
    # vector2
    vector2 = parser.struct('Vec2')
    csharp.cstype_map[vector2] = csharp.CSMarshalType('Vector2')
    csharp.cstype_pointer_map[vector2] = csharp.CSMarshalType('ref Vector2')
    # CameraState
    camera_state = parser.struct('CameraState')
    csharp.cstype_pointer_map[camera_state] = csharp.CSMarshalType(
        'ref CameraState')
    # MouseState
    mouse_state = parser.struct('MouseState')
    csharp.cstype_pointer_map[mouse_state] = csharp.CSMarshalType(
        'ref MouseState')
    # Mat4
    mat4 = parser.struct('Mat4')
    csharp.cstype_map[mat4] = csharp.CSMarshalType('Matrix4x4')
    csharp.cstype_pointer_map[mat4] = csharp.CSMarshalType('ref Matrix4x4')
    # array
    array16 = parser.struct('array').instantiate(cpptypeinfo.Float, 16)
    csharp.cstype_map[array16] = csharp.CSMarshalType('Matrix4x4')
    # Mat4
    float44 = parser.struct('XMFLOAT4X4')
    csharp.cstype_map[float44] = csharp.CSMarshalType('Matrix4x4')

    #
    # process each namespace from root
    #
    root.mkdir(parents=True, exist_ok=True)
    for ns in parser.root_namespace.traverse():
        if ns.struct:
            continue

        for k, v in ns.user_type_map.items():
            if isinstance(v, cpptypeinfo.Enum):
                csharp.generate_enum(
                    k, v, csharp.CSContext(root / f'{k}.cs', NAMESPACE_NAME))
            elif isinstance(v, Typedef):
                if k.endswith('Callback'):
                    continue
                csharp.generate_typedef(
                    k, v, csharp.CSContext(root / f'{k}.cs', NAMESPACE_NAME))
            elif isinstance(v, Struct):
                if v.fields:
                    csharp.generate_struct(
                        k, v, csharp.CSContext(root / f'{k}.cs',
                                               NAMESPACE_NAME))
                else:
                    print(k)
            else:
                raise Exception()

    def is_im3d(f):
        if f.name.lower().startswith('im3d'):
            return True
        if f.file.name == 'im3d.h':
            return True
        return False

    csharp.generate_functions(
        parser.root_namespace,
        csharp.CSContext(root / 'ImGui.cs', NAMESPACE_NAME), 'ImGui',
        'imgui.dll', lambda f: not is_im3d(f))
    csharp.generate_functions(
        parser.root_namespace,
        csharp.CSContext(root / 'Im3d.cs', NAMESPACE_NAME), 'Im3d',
        'imgui.dll', is_im3d)

    generate_imguiio(parser.root_namespace,
                     csharp.CSContext(root / 'ImGuiIO.cs', NAMESPACE_NAME))


if __name__ == '__main__':
    if (len(sys.argv) > 3):
        dst = pathlib.Path(sys.argv[1])
        main(dst, *[pathlib.Path(x) for x in sys.argv[2:]])
    else:
        dst = HERE / 'cimgui_cs'
        main(dst, IMGUI_H, CIMGUI_H)
