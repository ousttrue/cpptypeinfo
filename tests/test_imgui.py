import unittest
import pathlib
import cpptypeinfo

HERE = pathlib.Path(__file__).absolute().parent
IMGUI_H = HERE.parent / 'libs/imgui/imgui.h'

root = cpptypeinfo.push_namespace('')
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
    cpptypeinfo.Typedef('ImTextureID',
                        cpptypeinfo.Pointer(cpptypeinfo.Void())),
    'ImGuiID':
    cpptypeinfo.Typedef('ImGuiID', cpptypeinfo.UInt32()),
    'ImWchar':
    cpptypeinfo.Typedef('ImWchar', cpptypeinfo.UInt16()),
    'ImGuiCol':
    cpptypeinfo.Typedef('ImGuiCol', cpptypeinfo.Int32()),
    'ImGuiCond':
    cpptypeinfo.Typedef('ImGuiCond', cpptypeinfo.Int32()),
    'ImGuiDataType':
    cpptypeinfo.Typedef('ImGuiDataType', cpptypeinfo.Int32()),
    'ImGuiDir':
    cpptypeinfo.Typedef('ImGuiDir', cpptypeinfo.Int32()),
    'ImGuiKey':
    cpptypeinfo.Typedef('ImGuiKey', cpptypeinfo.Int32()),
    'ImGuiNavInput':
    cpptypeinfo.Typedef('ImGuiNavInput', cpptypeinfo.Int32()),
    'ImGuiMouseCursor':
    cpptypeinfo.Typedef('ImGuiMouseCursor', cpptypeinfo.Int32()),
    'ImGuiStyleVar':
    cpptypeinfo.Typedef('ImGuiStyleVar', cpptypeinfo.Int32()),
    'ImDrawCornerFlags':
    cpptypeinfo.Typedef('ImDrawCornerFlags', cpptypeinfo.Int32()),
    'ImDrawListFlags':
    cpptypeinfo.Typedef('ImDrawListFlags', cpptypeinfo.Int32()),
    'ImFontAtlasFlags':
    cpptypeinfo.Typedef('ImFontAtlasFlags', cpptypeinfo.Int32()),
    'ImGuiBackendFlags':
    cpptypeinfo.Typedef('ImGuiBackendFlags', cpptypeinfo.Int32()),
    'ImGuiColorEditFlags':
    cpptypeinfo.Typedef('ImGuiColorEditFlags', cpptypeinfo.Int32()),
    'ImGuiConfigFlags':
    cpptypeinfo.Typedef('ImGuiConfigFlags', cpptypeinfo.Int32()),
    'ImGuiComboFlags':
    cpptypeinfo.Typedef('ImGuiComboFlags', cpptypeinfo.Int32()),
    'ImGuiDragDropFlags':
    cpptypeinfo.Typedef('ImGuiDragDropFlags', cpptypeinfo.Int32()),
    'ImGuiFocusedFlags':
    cpptypeinfo.Typedef('ImGuiFocusedFlags', cpptypeinfo.Int32()),
    'ImGuiHoveredFlags':
    cpptypeinfo.Typedef('ImGuiHoveredFlags', cpptypeinfo.Int32()),
    'ImGuiInputTextFlags':
    cpptypeinfo.Typedef('ImGuiInputTextFlags', cpptypeinfo.Int32()),
    'ImGuiSelectableFlags':
    cpptypeinfo.Typedef('ImGuiSelectableFlags', cpptypeinfo.Int32()),
    'ImGuiTabBarFlags':
    cpptypeinfo.Typedef('ImGuiTabBarFlags', cpptypeinfo.Int32()),
    'ImGuiTabItemFlags':
    cpptypeinfo.Typedef('ImGuiTabItemFlags', cpptypeinfo.Int32()),
    'ImGuiTreeNodeFlags':
    cpptypeinfo.Typedef('ImGuiTreeNodeFlags', cpptypeinfo.Int32()),
    'ImGuiWindowFlags':
    cpptypeinfo.Typedef('ImGuiWindowFlags', cpptypeinfo.Int32()),
    'ImGuiInputTextCallback':
    cpptypeinfo.Typedef(
        'ImGuiInputTextCallback',
        cpptypeinfo.Function(cpptypeinfo.Int32(), [
            cpptypeinfo.Param(
                cpptypeinfo.Pointer(
                    cpptypeinfo.Struct('ImGuiInputTextCallbackData')))
        ])),
    'ImGuiSizeCallback':
    cpptypeinfo.Typedef(
        'ImGuiSizeCallback',
        cpptypeinfo.Function(cpptypeinfo.Void(), [
            cpptypeinfo.Param(
                cpptypeinfo.Pointer(
                    cpptypeinfo.Struct('ImGuiSizeCallbackData')))
        ])),
    'ImS8':
    cpptypeinfo.Typedef('ImS8', cpptypeinfo.Int8()),
    'ImU8':
    cpptypeinfo.Typedef('ImU8', cpptypeinfo.UInt8()),
    'ImS16':
    cpptypeinfo.Typedef('ImS16', cpptypeinfo.Int16()),
    'ImU16':
    cpptypeinfo.Typedef('ImU16', cpptypeinfo.UInt16()),
    'ImS32':
    cpptypeinfo.Typedef('ImS32', cpptypeinfo.Int32()),
    'ImU32':
    cpptypeinfo.Typedef('ImU32', cpptypeinfo.UInt32()),
    'ImS64':
    cpptypeinfo.Typedef('ImS64', cpptypeinfo.Int64()),
    'ImU64':
    cpptypeinfo.Typedef('ImU64', cpptypeinfo.UInt64()),
    'ImVec2':
    cpptypeinfo.Struct('ImVec2', [
        cpptypeinfo.Field(cpptypeinfo.Float(), 'x'),
        cpptypeinfo.Field(cpptypeinfo.Float(), 'y')
    ]),
    'ImVec4':
    cpptypeinfo.Struct('ImVec4', [
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
    'End':
    cpptypeinfo.Function(cpptypeinfo.Void(), []),
    # bool BeginChild ( const char * str_id , const ImVec2 & size = ImVec2 ( 0 , 0 ) , bool border = false , ImGuiWindowFlags flags = 0 )
    # bool BeginChild(ImGuiID id, const ImVec2& size = ImVec2(0,0), bool border = false, ImGuiWindowFlags flags = 0);
    # function overloading
    'BeginChild': [
        cpptypeinfo.Function(cpptypeinfo.Bool(), [
            cpptypeinfo.Param(cpptypeinfo.parse('const char *'), 'str_id'),
            cpptypeinfo.Param(cpptypeinfo.Param('const ImVec2 &'), 'size',
                              'ImVec2(0,0)'),
            cpptypeinfo.Param(cpptypeinfo.Param('bool'), 'border', 'false'),
            cpptypeinfo.Param(cpptypeinfo.parse('ImGuiWindowFlags'), 'flags',
                              '0')
        ])
    ],
    '__dummy__0':
    None,
    'EndChild':
    cpptypeinfo.Function(cpptypeinfo.Void(), []),
    # bool IsWindowAppearing ( )
    'IsWindowAppearing':
    cpptypeinfo.Function(cpptypeinfo.Bool(), []),
    # bool IsWindowCollapsed ( )
    'IsWindowCollapsed':
    cpptypeinfo.Function(cpptypeinfo.Bool(), []),
    # bool IsWindowFocused ( ImGuiFocusedFlags flags = 0 )
    'IsWindowFocused':
    cpptypeinfo.Function(cpptypeinfo.Bool(), [
        cpptypeinfo.Param(cpptypeinfo.parse('ImGuiFocusedFlags'), 'flags', '0')
    ]),
    # bool IsWindowHovered ( ImGuiHoveredFlags flags = 0 )
    'IsWindowHovered':
    cpptypeinfo.Function(cpptypeinfo.Bool(), [
        cpptypeinfo.Param(cpptypeinfo.parse('ImGuiHoveredFlags'), 'flags', '0')
    ]),
    # ImDrawList * GetWindowDrawList ( )
    'GetWindowDrawList':
    cpptypeinfo.Function(cpptypeinfo.parse('ImDrawList*'), []),
    # ImVec2 GetWindowPos ( )
    'GetWindowPos':
    cpptypeinfo.Function(cpptypeinfo.parse('ImVec2'), []),
    # ImVec2 GetWindowSize ( )
    'GetWindowSize':
    cpptypeinfo.Function(cpptypeinfo.parse('ImVec2'), []),
    # float GetWindowWidth ( )
    'GetWindowWidth':
    cpptypeinfo.Function(cpptypeinfo.Float(), []),
    'GetWindowHeight':
    cpptypeinfo.Function(cpptypeinfo.Float(), []),
    # void SetNextWindowPos ( const ImVec2 & pos , ImGuiCond cond = 0 , const ImVec2 & pivot = ImVec2 ( 0 , 0 ) )
    'SetNextWindowPos':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(cpptypeinfo.parse('const ImVec2&'), 'pos'),
        cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCond'), 'cond', '0'),
        cpptypeinfo.Param(cpptypeinfo.parse('const ImVec2 &'), 'pivot',
                          'ImVec2(0,0)'),
    ]),
    # void SetNextWindowSize ( const ImVec2 & size , ImGuiCond cond = 0 )
    'SetNextWindowSize':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(cpptypeinfo.parse('const ImVec2 &'), 'size'),
        cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCond'), 'cond', '0')
    ]),
    # void SetNextWindowSizeConstraints ( const ImVec2 & size_min , const ImVec2 & size_max , ImGuiSizeCallback custom_callback = NULL , void * custom_callback_data = NULL )
    'SetNextWindowSizeConstraints':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(cpptypeinfo.parse('const ImVec2 &'), 'size_min'),
        cpptypeinfo.Param(cpptypeinfo.parse('const ImVec2 &'), 'size_max'),
        cpptypeinfo.Param(cpptypeinfo.parse('ImGuiSizeCallback'),
                          'custom_callback', 'NULL'),
        cpptypeinfo.Param(cpptypeinfo.parse('void *'), 'custom_callback_data',
                          'NULL')
    ]),
    # void SetNextWindowContentSize ( const ImVec2 & size )
    'SetNextWindowContentSize':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(cpptypeinfo.parse('const ImVec2 &'), 'size'),
    ]),
    # void SetNextWindowCollapsed ( bool collapsed , ImGuiCond cond = 0 )
    'SetNextWindowCollapsed':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(cpptypeinfo.Bool(), 'collapsed'),
        cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCond'), 'cond', '0'),
    ]),
    # void SetNextWindowFocus ( )
    'SetNextWindowFocus':
    cpptypeinfo.Function(cpptypeinfo.Void(), []),
    # void SetNextWindowBgAlpha ( float alpha )
    'SetNextWindowBgAlpha':
    cpptypeinfo.Function(cpptypeinfo.Void(),
                         [cpptypeinfo.Param(cpptypeinfo.Float(), 'alpha')]),
    # void SetWindowPos ( const ImVec2 & pos , ImGuiCond cond = 0 )
    # void SetWindowPos(const char* name, const ImVec2& pos, ImGuiCond cond = 0);
    # function overloading
    'SetWindowPos': [
        cpptypeinfo.Function(cpptypeinfo.Void(), [
            cpptypeinfo.Param(cpptypeinfo.parse('const ImVec2 &'), 'pos'),
            cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCond'), 'cond', '0'),
        ])
    ],
    '__dummy__1':
    None,
    # void SetWindowSize ( const ImVec2 & size , ImGuiCond cond = 0 )
    # void          SetWindowSize(const char* name, const ImVec2& size, ImGuiCond cond = 0);
    # function overloading
    'SetWindowSize': [
        cpptypeinfo.Function(cpptypeinfo.Void(), [
            cpptypeinfo.Param(cpptypeinfo.parse('const ImVec2 &'), 'size'),
            cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCond'), 'cond', '0'),
        ])
    ],
    '__dummy__2':
    None,
    # void SetWindowCollapsed ( bool collapsed , ImGuiCond cond = 0 )
    #  IMGUI_API void          SetWindowCollapsed(const char* name, bool collapsed, ImGuiCond cond = 0);   // set named window collapsed state
    'SetWindowCollapsed': [
        cpptypeinfo.Function(cpptypeinfo.Void(), [
            cpptypeinfo.Param(cpptypeinfo.Bool(), 'collapsed'),
            cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCond'), 'cond', '0'),
        ])
    ],
    '__dummy__3':
    None,
    # void SetWindowFocus ( )
    # IMGUI_API void          SetWindowFocus(const char* name);
    'SetWindowFocus': [cpptypeinfo.Function(cpptypeinfo.Void(), [])],
    '__dummy__4':
    None,
    # void SetWindowFontScale ( float scale )
    'SetWindowFontScale':
    cpptypeinfo.Function(cpptypeinfo.Void(),
                         [cpptypeinfo.Param(cpptypeinfo.Float(), 'scale')]),
    # ImVec2 GetContentRegionMax ( )
    'GetContentRegionMax':
    cpptypeinfo.Function(cpptypeinfo.parse('ImVec2'), []),
    # ImVec2 GetContentRegionAvail ( )
    'GetContentRegionAvail':
    cpptypeinfo.Function(cpptypeinfo.parse('ImVec2'), []),
    # ImVec2 GetWindowContentRegionMin ( )
    'GetWindowContentRegionMin':
    cpptypeinfo.Function(cpptypeinfo.parse('ImVec2'), []),
    # ImVec2 GetWindowContentRegionMax ( )
    'GetWindowContentRegionMax':
    cpptypeinfo.Function(cpptypeinfo.parse('ImVec2'), []),
    # float GetWindowContentRegionWidth ( )
    'GetWindowContentRegionWidth':
    cpptypeinfo.Function(cpptypeinfo.Float(), []),
    # float GetScrollX ( )
    'GetScrollX':
    cpptypeinfo.Function(cpptypeinfo.Float(), []),
    'GetScrollY':
    cpptypeinfo.Function(cpptypeinfo.Float(), []),
    'GetScrollMaxX':
    cpptypeinfo.Function(cpptypeinfo.Float(), []),
    'GetScrollMaxY':
    cpptypeinfo.Function(cpptypeinfo.Float(), []),
    # void SetScrollX ( float scroll_x )
    'SetScrollX':
    cpptypeinfo.Function(cpptypeinfo.Void(),
                         [cpptypeinfo.Param(cpptypeinfo.Float(), 'scroll_x')]),
    'SetScrollY':
    cpptypeinfo.Function(cpptypeinfo.Void(),
                         [cpptypeinfo.Param(cpptypeinfo.Float(), 'scroll_y')]),
    # void SetScrollHereX ( float center_x_ratio = 0.5f )
    'SetScrollHereX':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.Float(), 'center_x_ratio', '0.5f')]),
    'SetScrollHereY':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.Float(), 'center_y_ratio', '0.5f')]),
    # void SetScrollFromPosX ( float local_x , float center_x_ratio = 0.5f )
    'SetScrollFromPosX':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(cpptypeinfo.Float(), 'local_x'),
        cpptypeinfo.Param(cpptypeinfo.Float(), 'center_x_ratio', '0.5f')
    ]),
    'SetScrollFromPosY':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(cpptypeinfo.Float(), 'local_y'),
        cpptypeinfo.Param(cpptypeinfo.Float(), 'center_y_ratio', '0.5f')
    ]),
    # void PushFont ( ImFont * font )
    'PushFont':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.parse('ImFont*'), 'font')]),
    # void PopFont ( )
    'PopFont':
    cpptypeinfo.Function(cpptypeinfo.Void(), []),
    # void PushStyleColor ( ImGuiCol idx , ImU32 col )
    # void PushStyleColor ( ImGuiCol idx , ImU32 col )
    'PushStyleColor': [
        cpptypeinfo.Function(cpptypeinfo.Void(), [
            cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCol'), 'idx'),
            cpptypeinfo.Param(cpptypeinfo.parse('ImU32'), 'col')
        ])
    ],
    '__dummy__5':
    None,
    # void PopStyleColor ( int count = 1 )
    'PopStyleColor':
    cpptypeinfo.Function(
        cpptypeinfo.Void(),
        [cpptypeinfo.Param(cpptypeinfo.Int32(), 'count', '1')]),
    # void PushStyleVar ( ImGuiStyleVar idx , float val )
    # void PushStyleVar(ImGuiStyleVar idx, const ImVec2& val);
    'PushStyleVar': [
        cpptypeinfo.Function(cpptypeinfo.Void(), [
            cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCol'), 'idx'),
            cpptypeinfo.Param(cpptypeinfo.Float(), 'val')
        ])
    ],
    '__dummy__6':
    None,
    # :void PopStyleVar ( int count = 1 )
    'PopStyleVar':
    cpptypeinfo.Function(cpptypeinfo.Void(), [
        cpptypeinfo.Param(cpptypeinfo.Int32(), 'count', '1'),
    ]),
    # const ImVec4 & GetStyleColorVec4 ( ImGuiCol idx )
    'GetStyleColorVec4':
    cpptypeinfo.Function(
        cpptypeinfo.parse('const ImVec4 &'),
        [cpptypeinfo.Param(cpptypeinfo.parse('ImGuiCol'), 'idx')]),
    # ImFont * GetFont ( )
    'GetFont':
    cpptypeinfo.Function(cpptypeinfo.parse('ImFont*'), []),
    'GetFontSize': [],
    'GetFontTexUvWhitePixel': [],
    # 3 overloading
    'GetColorU32': [],
    '__dummy__7':
    None,
    '__dummy__8':
    None,
    'PushItemWidth': [],
    'PopItemWidth': [],
    'SetNextItemWidth': [],
    'CalcItemWidth': [],
    'PushTextWrapPos': [],
    'PopTextWrapPos': [],
    'PushAllowKeyboardFocus': [],
    'PopAllowKeyboardFocus': [],
    'PushButtonRepeat': [],
    'PopButtonRepeat': [],
    'Separator': [],
    'SameLine': [],
    'NewLine': [],
    'Spacing': [],
    'Dummy': [],
    'Indent': [],
    'Unindent': [],
    'BeginGroup': [],
    'EndGroup': [],
    'GetCursorPos': [],
    'GetCursorPosX': [],
    'GetCursorPosY': [],
    'SetCursorPos': [],
    'SetCursorPosX': [],
    'SetCursorPosY': [],
    'GetCursorStartPos': [],
    'GetCursorScreenPos': [],
    'SetCursorScreenPos': [],
    'AlignTextToFramePadding': [],
    'GetTextLineHeight': [],
    'GetTextLineHeightWithSpacing': [],
    'GetFrameHeight': [],
    'GetFrameHeightWithSpacing': [],
    'PushID': [],
    '__dummy__9': [],
    '__dummy__10': [],
    '__dummy__11': [],
    'PopID': [],
    'GetID': [],
    '__dummy__12': [],
    '__dummy__13': [],
    'TextUnformatted': [],
    'Text': [],
    'TextV': [],
    'TextColored': [],
    'TextColoredV': [],
    'TextDisabled': [],
    'TextDisabledV': [],
    'TextWrapped': [],
    'TextWrappedV': [],
    'LabelText': [],
    'LabelTextV': [],
    'BulletText': [],
    'BulletTextV': [],
    'Button': [],
    'SmallButton': [],
    'InvisibleButton': [],
    'ArrowButton': [],
    'Image': [],
    'ImageButton': [],
    'Checkbox': [],
    'CheckboxFlags': [],
    'RadioButton': [],
    '__dummy__14':
    None,
    'ProgressBar': [],
    'Bullet': [],
    'BeginCombo': [],
    'EndCombo': [],
    'Combo': [],
    '__dummy__15': [],
    '__dummy__16': [],
    'DragFloat': [],
    'DragFloat2': [],
    'DragFloat3': [],
    'DragFloat4': [],
    'DragFloatRange2': [],
    'DragInt': [],
    'DragInt2': [],
    'DragInt3': [],
    'DragInt4': [],
    'DragIntRange2': [],
    'DragScalar': [],
    'DragScalarN': [],
    'SliderFloat': [],
    'SliderFloat2': [],
    'SliderFloat3': [],
    'SliderFloat4': [],
    'SliderAngle': [],
    'SliderInt': [],
    'SliderInt2': [],
    'SliderInt3': [],
    'SliderInt4': [],
    'SliderScalar': [],
    'SliderScalarN': [],
    'VSliderFloat': [],
    'VSliderInt': [],
    'VSliderScalar': [],
    'InputText': [],
    'InputTextMultiline': [],
    'InputTextWithHint': [],
    'InputFloat': [],
    'InputFloat2': [],
    'InputFloat3': [],
    'InputFloat4': [],
    'InputInt': [],
    'InputInt2': [],
    'InputInt3': [],
    'InputInt4': [],
    'InputDouble': [],
    'InputScalar': [],
    'InputScalarN': [],
    'ColorEdit3': [],
    'ColorEdit4': [],
    'ColorPicker3': [],
    'ColorPicker4': [],
    'ColorButton': [],
    'SetColorEditOptions': [],
    'TreeNode': [],
    '__dummy__17': [],
    '__dummy__18': [],
    'TreeNodeV': [],
    '__dummy__19': [],
    'TreeNodeEx': [],
    '__dummy__20': [],
    '__dummy__21': [],
    'TreeNodeExV': [],
    '__dummy__22': [],
    'TreePush': [],
    '__dummy__23': [],
    'TreePop': [],
    'GetTreeNodeToLabelSpacing': [],
    'CollapsingHeader': [],
    '__dummy__24': [],
    'SetNextItemOpen': [],
    'Selectable': [],
    '__dummy__25': [],
    'ListBox': [],
    '__dummy__26': [],
    'ListBoxHeader': [],
    '__dummy__27': [],
    'ListBoxFooter': [],
    'PlotLines': [],
    '__dummy__28': [],
    'PlotHistogram': [],
    '__dummy__29': [],
    'Value': [],
    '__dummy__30': [],
    '__dummy__31': [],
    '__dummy__32': [],
    'BeginMainMenuBar': [],
    'EndMainMenuBar': [],
    'BeginMenuBar': [],
    'EndMenuBar': [],
    'BeginMenu': [],
    'EndMenu': [],
    'MenuItem': [],
    '__dummy__33': [],
    'BeginTooltip': [],
    'EndTooltip': [],
    'SetTooltip': [],
    'SetTooltipV': [],
    'OpenPopup': [],
    'BeginPopup': [],
    'BeginPopupContextItem': [],
    'BeginPopupContextWindow': [],
    'BeginPopupContextVoid': [],
    'BeginPopupModal': [],
    'EndPopup': [],
    'OpenPopupOnItemClick': [],
    'IsPopupOpen': [],
    'CloseCurrentPopup': [],
    'Columns': [],
    'NextColumn': [],
    'GetColumnIndex': [],
    'GetColumnWidth': [],
    'SetColumnWidth': [],
    'GetColumnOffset': [],
    'SetColumnOffset': [],
    'GetColumnsCount': [],
    'BeginTabBar': [],
    'EndTabBar': [],
    'BeginTabItem': [],
    'EndTabItem': [],
    'SetTabItemClosed': [],
    'LogToTTY': [],
    'LogToFile': [],
    'LogToClipboard': [],
    'LogFinish': [],
    'LogButtons': [],
    'LogText': [],
    'BeginDragDropSource': [],
    'SetDragDropPayload': [],
    'EndDragDropSource': [],
    'BeginDragDropTarget': [],
    'AcceptDragDropPayload': [],
    'EndDragDropTarget': [],
    'GetDragDropPayload': [],
    'PushClipRect': [],
    'PopClipRect': [],
    'SetItemDefaultFocus': [],
    'SetKeyboardFocusHere': [],
    'IsItemHovered': [],
    'IsItemActive': [],
    'IsItemFocused': [],
    'IsItemClicked': [],
    'IsItemVisible': [],
    'IsItemEdited': [],
    'IsItemActivated': [],
    'IsItemDeactivated': [],
    'IsItemDeactivatedAfterEdit': [],
    'IsAnyItemHovered': [],
    'IsAnyItemActive': [],
    'IsAnyItemFocused': [],
    'GetItemRectMin': [],
    'GetItemRectMax': [],
    'GetItemRectSize': [],
    'SetItemAllowOverlap': [],
    'IsRectVisible': [],
    '__dummy__34': [],
    'GetTime': [],
    'GetFrameCount': [],
    'GetBackgroundDrawList': [],
    'GetForegroundDrawList': [],
    'GetDrawListSharedData': [],
    'GetStyleColorName': [],
    'SetStateStorage': [],
    'GetStateStorage': [],
    'CalcTextSize': [],
    'CalcListClipping': [],
    'BeginChildFrame': [],
    'EndChildFrame': [],
    'ColorConvertU32ToFloat4': [],
    'ColorConvertFloat4ToU32': [],
    'ColorConvertRGBtoHSV': [],
    'ColorConvertHSVtoRGB': [],
    'GetKeyIndex': [],
    'IsKeyDown': [],
    'IsKeyPressed': [],
    'IsKeyReleased': [],
    'GetKeyPressedAmount': [],
    'IsMouseDown': [],
    'IsAnyMouseDown': [],
    'IsMouseClicked': [],
    'IsMouseDoubleClicked': [],
    'IsMouseReleased': [],
    'IsMouseDragging': [],
    'IsMouseHoveringRect': [],
    'IsMousePosValid': [],
    'GetMousePos': [],
    'GetMousePosOnOpeningCurrentPopup': [],
    'GetMouseDragDelta': [],
    'ResetMouseDragDelta': [],
    'GetMouseCursor': [],
    'SetMouseCursor': [],
    'CaptureKeyboardFromApp': [],
    'CaptureMouseFromApp': [],
    'GetClipboardText': [],
    'SetClipboardText': [],
    'LoadIniSettingsFromDisk': [],
    'LoadIniSettingsFromMemory': [],
    'SaveIniSettingsToDisk': [],
    'SaveIniSettingsToMemory': [],
    'SetAllocatorFunctions': [],
    'MemAlloc': [],
    'MemFree': [],
    # enum
    'ImGuiWindowFlags_': [],
    'ImGuiInputTextFlags_': [],
    'ImGuiTreeNodeFlags_': [],
    'ImGuiSelectableFlags_': [],
    'ImGuiComboFlags_': [],
    'ImGuiTabBarFlags_': [],
    'ImGuiFocusedFlags_': [],
    'ImGuiDragDropFlags_': [],
    'ImGuiDataType_': [],
    'ImGuiDir_': [],
    'ImGuiKey_': [],
    'ImGuiNavInput_': [],
    'ImGuiConfigFlags_': [],
    'ImGuiBackendFlags_': [],
    'ImGuiCol_': [],
    'ImGuiStyleVar_': [],
    'ImGuiColorEditFlags_': [],
    'ImGuiMouseCursor_': [],
    'ImGuiCond_': [],
    'ImGuiHoveredFlags_': [],
    'ImGuiTabItemFlags_': [],
    # allocator
    'ImNewDummy':
    cpptypeinfo.Struct('ImNewDummy'),
    'operator new': [],
    'operator delete': [],
    'IM_DELETE': [],
    #
    'ImVector':
    cpptypeinfo.parse('struct ImVector'),
    #
    'TreeAdvanceToLabelPos': [],
    'SetNextTreeNodeOpen': [],
    'GetContentRegionAvailWidth': [],
    'GetOverlayDrawList': [],
    'SetScrollHere': [],
    'IsItemDeactivatedAfterChange': [],
    'IsAnyWindowFocused': [],
    'IsAnyWindowHovered': [],
    'CalcItemRectClosestPoint': [],
    'ShowTestWindow': [],
    'IsRootWindowFocused': [],
    'IsRootWindowOrAnyChildFocused': [],
    'SetNextWindowContentWidth': [],
    'GetItemsLineHeightWithSpacing': [],
    'IsRootWindowOrAnyChildHovered': [],
    'AlignFirstTextHeightToWidgets': [],
    'SetNextWindowPosCenter': [],
    #
    'ImGuiTextEditCallback': [],
    'ImGuiTextEditCallbackData': [],
    'ImDrawCallback': [],
    'ImDrawIdx':
    cpptypeinfo.Typedef('ImDrawIdx', cpptypeinfo.UInt16()),
    'ImDrawCornerFlags_': [],
    'ImDrawListFlags_': [],
    'ImFontAtlasCustomRect': [],
    'ImFontAtlasFlags_': [],
}
cpptypeinfo.pop_namespace()


class ImGuiTest(unittest.TestCase):
    def test_imgui_h(self) -> None:
        cpptypeinfo.push_namespace(root)
        cpptypeinfo.parse_headers(IMGUI_H,
                                 cpp_flags=[
                                     '-DIMGUI_DISABLE_OBSOLETE_FUNCTIONS',
                                 ])
        cpptypeinfo.pop_namespace()

        for ns in root.traverse():
            if isinstance(ns, cpptypeinfo.Struct):
                continue

            for k, v in ns.user_type_map.items():
                with self.subTest(name=k):
                    # print(f'{ns}{v}')
                    expected = EXPECTS.get(k)
                    if expected is None:
                        raise Exception('not found :' + k)
                    else:
                        if isinstance(expected, list):
                            pass
                        else:
                            self.assertEqual(expected, v)

            for v in ns.functions:
                if v.name:
                    with self.subTest(name=v.name):
                        # print(f'{ns}{v}')
                        expected = EXPECTS.get(v.name)
                        if expected is None:
                            raise Exception('not found :' + v.name)
                        else:
                            if isinstance(expected, list):
                                pass
                            else:
                                self.assertEqual(expected, v)


if __name__ == '__main__':
    unittest.main()
