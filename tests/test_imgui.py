import unittest
import tempfile
import os
import pathlib
import contextlib
from typing import List

from clang import cindex
import cpptypeinfo

HERE = pathlib.Path(__file__).absolute().parent
IMGUI_H = HERE.parent / 'libs/imgui/imgui.h'


@contextlib.contextmanager
def tmp(src):
    fd, tmp_name = tempfile.mkstemp(prefix='tmpheader_', suffix='.h')
    os.close(fd)
    with open(tmp_name, 'w', encoding='utf-8') as f:
        f.write(src)
    try:
        yield pathlib.Path(tmp_name)
    finally:
        os.unlink(tmp_name)


class TypedefDecl:
    def __init__(self, name: str, src: cpptypeinfo.Declaration):
        self.name = name
        self.src = src

    def __eq__(self, value):
        return (isinstance(value, TypedefDecl) and self.name == value.name
                and self.src == value.src)

    def __repr__(self) -> str:
        return f'<typedef {self.name} = {self.src}>'

    @classmethod
    def parse(cls, c: cindex.Cursor) -> 'TypedefDecl':
        # children = [child for child in c.get_children()]
        # if children:
        #     # may function pointer
        #     # ImGuiInputTextCallback
        #     assert (len(children) == 1)
        #     params = []
        #     for p in children:
        #         if p.kind == cindex.CursorKind.PARM_DECL:
        #             params.append((p.spelling, p.type.spelling))
        #         else:
        #             raise NotImplementedError()
        #     return TypedefDecl(c.spelling, decl)
        # else:
        # tokens = [token.spelling for token in c.get_tokens()]
        decl = cpptypeinfo.parse(c.underlying_typedef_type.spelling)
        return TypedefDecl(c.spelling, decl)


EXPECTS = {
    'ImDrawChannel':
    cpptypeinfo.Struct('ImDrawChannel'),
    'ImDrawCmd':
    cpptypeinfo.Struct('ImDrawCmd'),
    'ImDrawData':
    cpptypeinfo.Struct('ImDrawData'),
    'ImDrawList':
    cpptypeinfo.Struct('ImDrawList'),
    'ImDrawListSharedData':
    cpptypeinfo.Struct('ImDrawListSharedData'),
    'ImDrawListSplitter':
    cpptypeinfo.Struct('ImDrawListSplitter'),
    'ImDrawVert':
    cpptypeinfo.Struct('ImDrawVert'),
    'ImFont':
    cpptypeinfo.Struct('ImFont'),
    'ImFontAtlas':
    cpptypeinfo.Struct('ImFontAtlas'),
    'ImFontConfig':
    cpptypeinfo.Struct('ImFontConfig'),
    'ImFontGlyph':
    cpptypeinfo.Struct('ImFontGlyph'),
    'ImFontGlyphRangesBuilder':
    cpptypeinfo.Struct('ImFontGlyphRangesBuilder'),
    'ImColor':
    cpptypeinfo.Struct('ImColor'),
    'ImGuiContext':
    cpptypeinfo.Struct('ImGuiContext'),
    'ImGuiIO':
    cpptypeinfo.Struct('ImGuiIO'),
    'ImGuiInputTextCallbackData':
    cpptypeinfo.Struct('ImGuiInputTextCallbackData'),
    'ImGuiListClipper':
    cpptypeinfo.Struct('ImGuiListClipper'),
    'ImGuiOnceUponAFrame':
    cpptypeinfo.Struct('ImGuiOnceUponAFrame'),
    'ImGuiPayload':
    cpptypeinfo.Struct('ImGuiPayload'),
    'ImGuiSizeCallbackData':
    cpptypeinfo.Struct('ImGuiSizeCallbackData'),
    'ImGuiStorage':
    cpptypeinfo.Struct('ImGuiStorage'),
    'ImGuiStyle':
    cpptypeinfo.Struct('ImGuiStyle'),
    'ImGuiTextBuffer':
    cpptypeinfo.Struct('ImGuiTextBuffer'),
    'ImGuiTextFilter':
    cpptypeinfo.Struct('ImGuiTextFilter'),
    'ImTextureID':
    TypedefDecl('ImTextureID', cpptypeinfo.Pointer(cpptypeinfo.Void())),
    'ImGuiID':
    TypedefDecl('ImGuiID', cpptypeinfo.UInt32()),
    'ImWchar':
    TypedefDecl('ImWchar', cpptypeinfo.UInt16()),
    'ImGuiCol':
    TypedefDecl('ImGuiCol', cpptypeinfo.Int32()),
    'ImGuiCond':
    TypedefDecl('ImGuiCond', cpptypeinfo.Int32()),
    'ImGuiDataType':
    TypedefDecl('ImGuiDataType', cpptypeinfo.Int32()),
    'ImGuiDir':
    TypedefDecl('ImGuiDir', cpptypeinfo.Int32()),
    'ImGuiKey':
    TypedefDecl('ImGuiKey', cpptypeinfo.Int32()),
    'ImGuiNavInput':
    TypedefDecl('ImGuiNavInput', cpptypeinfo.Int32()),
    'ImGuiMouseCursor':
    TypedefDecl('ImGuiMouseCursor', cpptypeinfo.Int32()),
    'ImGuiStyleVar':
    TypedefDecl('ImGuiStyleVar', cpptypeinfo.Int32()),
    'ImDrawCornerFlags':
    TypedefDecl('ImDrawCornerFlags', cpptypeinfo.Int32()),
    'ImDrawListFlags':
    TypedefDecl('ImDrawListFlags', cpptypeinfo.Int32()),
    'ImFontAtlasFlags':
    TypedefDecl('ImFontAtlasFlags', cpptypeinfo.Int32()),
    'ImGuiBackendFlags':
    TypedefDecl('ImGuiBackendFlags', cpptypeinfo.Int32()),
    'ImGuiColorEditFlags':
    TypedefDecl('ImGuiColorEditFlags', cpptypeinfo.Int32()),
    'ImGuiConfigFlags':
    TypedefDecl('ImGuiConfigFlags', cpptypeinfo.Int32()),
    'ImGuiComboFlags':
    TypedefDecl('ImGuiComboFlags', cpptypeinfo.Int32()),
    'ImGuiDragDropFlags':
    TypedefDecl('ImGuiDragDropFlags', cpptypeinfo.Int32()),
    'ImGuiFocusedFlags':
    TypedefDecl('ImGuiFocusedFlags', cpptypeinfo.Int32()),
    'ImGuiHoveredFlags':
    TypedefDecl('ImGuiHoveredFlags', cpptypeinfo.Int32()),
    'ImGuiInputTextFlags':
    TypedefDecl('ImGuiInputTextFlags', cpptypeinfo.Int32()),
    'ImGuiSelectableFlags':
    TypedefDecl('ImGuiSelectableFlags', cpptypeinfo.Int32()),
    'ImGuiTabBarFlags':
    TypedefDecl('ImGuiTabBarFlags', cpptypeinfo.Int32()),
    'ImGuiTabItemFlags':
    TypedefDecl('ImGuiTabItemFlags', cpptypeinfo.Int32()),
    'ImGuiTreeNodeFlags':
    TypedefDecl('ImGuiTreeNodeFlags', cpptypeinfo.Int32()),
    'ImGuiWindowFlags':
    TypedefDecl('ImGuiWindowFlags', cpptypeinfo.Int32()),
    'ImGuiInputTextCallback':
    TypedefDecl(
        'ImGuiInputTextCallback',
        cpptypeinfo.Function(cpptypeinfo.Int32(), [
            cpptypeinfo.Pointer(
                cpptypeinfo.Struct('ImGuiInputTextCallbackData'))
        ]))
}


def parse(c: cindex.Cursor):
    if c.kind == cindex.CursorKind.UNEXPOSED_DECL:
        tokens = [t.spelling for t in c.get_tokens()]
    elif c.kind == cindex.CursorKind.STRUCT_DECL:
        fields = []
        for child in c.get_children():
            fields.append(child)
        if fields:
            raise NotImplementedError()
        return cpptypeinfo.parse(f'struct {c.spelling}')

    elif c.kind == cindex.CursorKind.TYPEDEF_DECL:
        return TypedefDecl.parse(c)
    else:
        print(c.kind)


class ImGuiTest(unittest.TestCase):
    def test_int(self) -> None:
        tu = cpptypeinfo.get_tu(IMGUI_H)
        self.assertIsInstance(tu, cindex.TranslationUnit)

        # TRANSLATION_UNIT
        c: cindex.Cursor = tu.cursor
        self.assertIsInstance(c, cindex.Cursor)
        self.assertEqual(cindex.CursorKind.TRANSLATION_UNIT, c.kind)
        self.assertIsNone(c.location.file)

        count = 0
        for i, c in enumerate(c.get_children()):
            if c.location.file.name != str(IMGUI_H):
                continue
            count += 1
            with self.subTest(i=i, spelling=c.spelling):
                self.assertEqual(EXPECTS.get(c.spelling), parse(c))
            if count > len(EXPECTS):
                break


if __name__ == '__main__':
    unittest.main()
