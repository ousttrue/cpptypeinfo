import unittest
import pathlib
from clang import cindex
import cpptypeinfo

HERE = pathlib.Path(__file__).absolute().parent
IMGUI_H = HERE.parent / 'libs/imgui/imgui.h'


class TypedefDecl:
    def __init__(self, name: str, src: cpptypeinfo.Declaration):
        self.name = name
        self.src = src

    def __eq__(self, value):
        return (isinstance(value, TypedefDecl) and self.name == value.name
                and self.src == value.src)

    def __repr__(self) -> str:
        return f'<typedef {self.name} = {self.src}>'


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
            cpptypeinfo.Param(
                cpptypeinfo.Pointer(
                    cpptypeinfo.Struct('ImGuiInputTextCallbackData')))
        ])),
    'ImGuiSizeCallback':
    TypedefDecl(
        'ImGuiSizeCallback',
        cpptypeinfo.Function(cpptypeinfo.Void(), [
            cpptypeinfo.Param(
                cpptypeinfo.Pointer(
                    cpptypeinfo.Struct('ImGuiSizeCallbackData')))
        ])),
    'ImS8':
    TypedefDecl('ImS8', cpptypeinfo.Int8()),
    'ImU8':
    TypedefDecl('ImU8', cpptypeinfo.UInt8()),
    'ImS16':
    TypedefDecl('ImS16', cpptypeinfo.Int16()),
    'ImU16':
    TypedefDecl('ImU16', cpptypeinfo.UInt16()),
    'ImS32':
    TypedefDecl('ImS32', cpptypeinfo.Int32()),
    'ImU32':
    TypedefDecl('ImU32', cpptypeinfo.UInt32()),
    'ImS64':
    TypedefDecl('ImS64', cpptypeinfo.Int64()),
    'ImU64':
    TypedefDecl('ImU64', cpptypeinfo.UInt64()),
    'ImVec2':
    cpptypeinfo.Struct('ImVec2', False, [
        cpptypeinfo.Field(cpptypeinfo.Float(), 'x'),
        cpptypeinfo.Field(cpptypeinfo.Float(), 'y')
    ]),
    'ImVec4':
    cpptypeinfo.Struct('ImVec4', False, [
        cpptypeinfo.Field(cpptypeinfo.Float(), 'x'),
        cpptypeinfo.Field(cpptypeinfo.Float(), 'y'),
        cpptypeinfo.Field(cpptypeinfo.Float(), 'z'),
        cpptypeinfo.Field(cpptypeinfo.Float(), 'w')
    ]),
    'CreateContext':
    cpptypeinfo.Function(
        cpptypeinfo.Pointer(cpptypeinfo.Struct('ImGuiContext')), [
            cpptypeinfo.Param(
                cpptypeinfo.Pointer(cpptypeinfo.Struct('ImFontAtlas')),
                'shared_font_atlas', 'NULL')
        ]),
    'DestroyContext':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(
            cpptypeinfo.Pointer(cpptypeinfo.Struct('ImGuiContext')), 'ctx',
            'NULL')
    ]),
    'GetCurrentContext':
    cpptypeinfo.Function(
        cpptypeinfo.Pointer(cpptypeinfo.Struct('ImGuiContext')), []),
    'SetCurrentContext':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(
            cpptypeinfo.Pointer(cpptypeinfo.Struct('ImGuiContext')), 'ctx')
    ]),
    'DebugCheckVersionAndDataLayout':
    cpptypeinfo.Function(cpptypeinfo.Bool(), [
        cpptypeinfo.Param(cpptypeinfo.parse('const char*'), 'version_str'),
        cpptypeinfo.Param(cpptypeinfo.UInt64(), 'sz_io'),
        cpptypeinfo.Param(cpptypeinfo.UInt64(), 'sz_style'),
        cpptypeinfo.Param(cpptypeinfo.UInt64(), 'sz_vec2'),
        cpptypeinfo.Param(cpptypeinfo.UInt64(), 'sz_vec4'),
        cpptypeinfo.Param(cpptypeinfo.UInt64(), 'sz_drawvert'),
        cpptypeinfo.Param(cpptypeinfo.UInt64(), 'sz_drawidx'),
    ]),
    # ImGuiIO & GetIO ( )
    'GetIO':
    cpptypeinfo.Function(cpptypeinfo.parse('ImGuiIO &'), []),
    # ImGuiStyle & GetStyle ( )
    'GetStyle':
    cpptypeinfo.Function(cpptypeinfo.parse('ImGuiStyle &'), []),
    # void NewFrame ( )
    'NewFrame':
    cpptypeinfo.Function(cpptypeinfo.Void(), []),
    'EndFrame':
    cpptypeinfo.Function(cpptypeinfo.Void(), []),
    'Render':
    cpptypeinfo.Function(cpptypeinfo.Void(), []),
    # ImDrawData * GetDrawData ( )
    'GetDrawData':
    cpptypeinfo.Function(cpptypeinfo.parse('ImDrawData *'), []),
    # void ShowDemoWindow ( bool * p_open = NULL )
    'ShowDemoWindow':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('bool *'), 'p_open', 'NULL')]),
    # void ShowAboutWindow ( bool * p_open = NULL )
    'ShowAboutWindow':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('bool *'), 'p_open', 'NULL')]),
    # void ShowMetricsWindow ( bool * p_open = NULL )
    'ShowMetricsWindow':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('bool *'), 'p_open', 'NULL')]),
    # void ShowStyleEditor ( ImGuiStyle * ref = NULL )
    'ShowStyleEditor':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('ImGuiStyle *'), 'ref', 'NULL')]),
    # bool ShowStyleSelector ( const char * label )
    'ShowStyleSelector':
    cpptypeinfo.Function(
        cpptypeinfo.Bool(),
        [cpptypeinfo.Param(cpptypeinfo.parse('const char*'), 'label')]),
    # void ShowFontSelector ( const char * label )
    'ShowFontSelector':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('const char*'), 'label')]),
    # void ShowUserGuide ( )
    'ShowUserGuide':
    cpptypeinfo.Function(cpptypeinfo.Void(), []),
    # const char * GetVersion ( )
    'GetVersion':
    cpptypeinfo.Function(cpptypeinfo.parse('const char*'), []),
    # void StyleColorsDark ( ImGuiStyle * dst = NULL )
    'StyleColorsDark':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('ImGuiStyle *'), 'dst', 'NULL')]),
    # void StyleColorsClassic ( ImGuiStyle * dst = NULL )
    'StyleColorsClassic':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('ImGuiStyle *'), 'dst', 'NULL')]),
    # void StyleColorsLight ( ImGuiStyle * dst = NULL )
    'StyleColorsLight':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('ImGuiStyle *'), 'dst', 'NULL')]),
    # bool Begin ( const char * name , bool * p_open = NULL , ImGuiWindowFlags flags = 0 )
    'Begin':
    cpptypeinfo.Function(cpptypeinfo.Bool(), [
        cpptypeinfo.Param(cpptypeinfo.parse('const char *'), 'name'),
        cpptypeinfo.Param(cpptypeinfo.parse('bool *'), 'p_open', 'NULL'),
        cpptypeinfo.Param(cpptypeinfo.parse('ImGuiWindowFlags'), 'flags', '0')
    ]),
}


def parse_param(c: cindex.Cursor) -> cpptypeinfo.Param:
    tokens = [x.spelling for x in c.get_tokens()]
    decl = cpptypeinfo.parse(c.type.spelling)
    name = c.spelling
    default_value = ''
    for child in c.get_children():
        if child.kind == cindex.CursorKind.TYPE_REF:
            pass
        elif child.kind == cindex.CursorKind.UNEXPOSED_EXPR:
            # default param assignment
            children = [x for x in child.get_children()]
            assert (len(children) == 1)
            # decl = cpptypeinfo.parse(child.type.spelling)
            childchild = children[0]
            assert (childchild.kind == cindex.CursorKind.INTEGER_LITERAL)
            default_value = tokens[-1]
        else:
            raise NotImplementedError(f'{child.kind}')
    return cpptypeinfo.Param(decl, name, default_value)


def traverse(c, level=''):
    print(f'{level}{c.kind}=>{c.spelling}: {c.type.kind}=>{c.type.spelling}')
    for child in c.get_children():
        traverse(child, level + '  ')


def parse_function(c: cindex.Cursor) -> cpptypeinfo.Function:
    params = []
    result = cpptypeinfo.parse(c.result_type.spelling)
    for child in c.get_children():
        if child.kind == cindex.CursorKind.TYPE_REF:
            pass
        elif child.kind == cindex.CursorKind.PARM_DECL:
            params.append(parse_param(child))
            # traverse(child)
            pass
        else:
            raise NotImplementedError()

    return cpptypeinfo.Function(result, params)


def parse(c: cindex.Cursor):
    if c.kind == cindex.CursorKind.UNEXPOSED_DECL:
        tokens = [t.spelling for t in c.get_tokens()]
    elif c.kind == cindex.CursorKind.STRUCT_DECL:
        decl = cpptypeinfo.parse(f'struct {c.spelling}')
        for child in c.get_children():
            if child.kind == cindex.CursorKind.FIELD_DECL:
                field = cpptypeinfo.parse(child.type.spelling)
                decl.add_field(cpptypeinfo.Field(field, child.spelling))
            elif child.kind == cindex.CursorKind.CONSTRUCTOR:
                pass
            elif child.kind == cindex.CursorKind.CXX_METHOD:
                pass
            else:
                raise NotImplementedError()
        return decl

    elif c.kind == cindex.CursorKind.TYPEDEF_DECL:
        # return TypedefDecl.parse(c)
        decl = cpptypeinfo.parse(c.underlying_typedef_type.spelling)
        return TypedefDecl(c.spelling, decl)

    elif c.kind == cindex.CursorKind.FUNCTION_DECL:
        return parse_function(c)

    else:
        raise NotImplementedError(str(c.kind))


class ImGuiTest(unittest.TestCase):
    def test_int(self) -> None:
        tu = cpptypeinfo.get_tu(IMGUI_H)
        self.assertIsInstance(tu, cindex.TranslationUnit)

        # TRANSLATION_UNIT
        c: cindex.Cursor = tu.cursor
        self.assertIsInstance(c, cindex.Cursor)
        self.assertEqual(cindex.CursorKind.TRANSLATION_UNIT, c.kind)
        self.assertIsNone(c.location.file)

        class Counter:
            def __init__(self):
                self.count = 0

        counter = Counter()

        def parse_namespace(c: cindex.Cursor):
            for i, child in enumerate(c.get_children()):
                if child.location.file.name != str(IMGUI_H):
                    continue
                with self.subTest(i=counter.count,
                                  kind=child.kind,
                                  spelling=child.spelling):
                    if child.kind == cindex.CursorKind.NAMESPACE:
                        # nested
                        cpptypeinfo.push_namespace(child.spelling)
                        parse_namespace(child)
                        cpptypeinfo.pop_namespace()
                    else:
                        counter.count += 1
                        expected = EXPECTS.get(child.spelling)
                        if expected:
                            self.assertEqual(expected, parse(child))
                        else:
                            raise Exception('not found :' + ' '.join(
                                t.spelling for t in child.get_tokens()))
                if counter.count > len(EXPECTS):
                    break
                    # pass

        parse_namespace(c)


if __name__ == '__main__':
    unittest.main()