import unittest
import pathlib
import cpptypeinfo
from cpptypeinfo.usertype import (Field, Struct, Pointer, Param, Function)

HERE = pathlib.Path(__file__).absolute().parent
IMGUI_H = HERE.parent / 'libs/imgui/imgui.h'

parser = cpptypeinfo.TypeParser()
EXPECTS = {
    'ImDrawChannel':
    parser.parse('struct ImDrawChannel'),
    'ImDrawCmd':
    parser.parse('struct ImDrawCmd'),
    'ImDrawData':
    parser.parse('struct ImDrawData'),
    'ImDrawList':
    parser.parse('struct ImDrawList'),
    'ImDrawListSharedData':
    parser.parse('struct ImDrawListSharedData'),
    'ImDrawListSplitter':
    parser.parse('struct ImDrawListSplitter'),
    'ImDrawVert':
    parser.parse('struct ImDrawVert'),
    'ImFont':
    parser.parse('struct ImFont'),
    'ImFontAtlas':
    parser.parse('struct ImFontAtlas'),
    'ImFontConfig':
    parser.parse('struct ImFontConfig'),
    'ImFontGlyph':
    parser.parse('struct ImFontGlyph'),
    'ImFontGlyphRangesBuilder':
    parser.parse('struct ImFontGlyphRangesBuilder'),
    'ImColor':
    parser.parse('struct ImColor'),
    'ImGuiContext':
    parser.parse('struct ImGuiContext'),
    'ImGuiIO':
    parser.parse('struct ImGuiIO'),
    'ImGuiInputTextCallbackData':
    parser.parse('struct ImGuiInputTextCallbackData'),
    'ImGuiListClipper':
    parser.parse('struct ImGuiListClipper'),
    'ImGuiOnceUponAFrame':
    parser.parse('struct ImGuiOnceUponAFrame'),
    'ImGuiPayload':
    parser.parse('struct ImGuiPayload'),
    'ImGuiSizeCallbackData':
    parser.parse('struct ImGuiSizeCallbackData'),
    'ImGuiStorage':
    parser.parse('struct ImGuiStorage'),
    'ImGuiStyle':
    parser.parse('struct ImGuiStyle'),
    'ImGuiTextBuffer':
    parser.parse('struct ImGuiTextBuffer'),
    'ImGuiTextFilter':
    parser.parse('struct ImGuiTextFilter'),
    'ImTextureID':
    parser.typedef('ImTextureID', Pointer(cpptypeinfo.Void())),
    'ImGuiID':
    parser.typedef('ImGuiID', cpptypeinfo.UInt32()),
    'ImWchar':
    parser.typedef('ImWchar', cpptypeinfo.UInt16()),
    'ImGuiCol':
    parser.typedef('ImGuiCol', cpptypeinfo.Int32()),
    'ImGuiCond':
    parser.typedef('ImGuiCond', cpptypeinfo.Int32()),
    'ImGuiDataType':
    parser.typedef('ImGuiDataType', cpptypeinfo.Int32()),
    'ImGuiDir':
    parser.typedef('ImGuiDir', cpptypeinfo.Int32()),
    'ImGuiKey':
    parser.typedef('ImGuiKey', cpptypeinfo.Int32()),
    'ImGuiNavInput':
    parser.typedef('ImGuiNavInput', cpptypeinfo.Int32()),
    'ImGuiMouseCursor':
    parser.typedef('ImGuiMouseCursor', cpptypeinfo.Int32()),
    'ImGuiStyleVar':
    parser.typedef('ImGuiStyleVar', cpptypeinfo.Int32()),
    'ImDrawCornerFlags':
    parser.typedef('ImDrawCornerFlags', cpptypeinfo.Int32()),
    'ImDrawListFlags':
    parser.typedef('ImDrawListFlags', cpptypeinfo.Int32()),
    'ImFontAtlasFlags':
    parser.typedef('ImFontAtlasFlags', cpptypeinfo.Int32()),
    'ImGuiBackendFlags':
    parser.typedef('ImGuiBackendFlags', cpptypeinfo.Int32()),
    'ImGuiColorEditFlags':
    parser.typedef('ImGuiColorEditFlags', cpptypeinfo.Int32()),
    'ImGuiConfigFlags':
    parser.typedef('ImGuiConfigFlags', cpptypeinfo.Int32()),
    'ImGuiComboFlags':
    parser.typedef('ImGuiComboFlags', cpptypeinfo.Int32()),
    'ImGuiDragDropFlags':
    parser.typedef('ImGuiDragDropFlags', cpptypeinfo.Int32()),
    'ImGuiFocusedFlags':
    parser.typedef('ImGuiFocusedFlags', cpptypeinfo.Int32()),
    'ImGuiHoveredFlags':
    parser.typedef('ImGuiHoveredFlags', cpptypeinfo.Int32()),
    'ImGuiInputTextFlags':
    parser.typedef('ImGuiInputTextFlags', cpptypeinfo.Int32()),
    'ImGuiSelectableFlags':
    parser.typedef('ImGuiSelectableFlags', cpptypeinfo.Int32()),
    'ImGuiTabBarFlags':
    parser.typedef('ImGuiTabBarFlags', cpptypeinfo.Int32()),
    'ImGuiTabItemFlags':
    parser.typedef('ImGuiTabItemFlags', cpptypeinfo.Int32()),
    'ImGuiTreeNodeFlags':
    parser.typedef('ImGuiTreeNodeFlags', cpptypeinfo.Int32()),
    'ImGuiWindowFlags':
    parser.typedef('ImGuiWindowFlags', cpptypeinfo.Int32()),
    'ImGuiInputTextCallback':
    parser.typedef(
        'ImGuiInputTextCallback',
        Function(cpptypeinfo.Int32(), [
            Param(Pointer(parser.parse('struct ImGuiInputTextCallbackData')))
        ])),
    'ImGuiSizeCallback':
    parser.typedef(
        'ImGuiSizeCallback',
        Function(
            cpptypeinfo.Void(),
            [Param(Pointer(parser.parse('struct ImGuiSizeCallbackData')))])),
    'ImS8':
    parser.typedef('ImS8', cpptypeinfo.Int8()),
    'ImU8':
    parser.typedef('ImU8', cpptypeinfo.UInt8()),
    'ImS16':
    parser.typedef('ImS16', cpptypeinfo.Int16()),
    'ImU16':
    parser.typedef('ImU16', cpptypeinfo.UInt16()),
    'ImS32':
    parser.typedef('ImS32', cpptypeinfo.Int32()),
    'ImU32':
    parser.typedef('ImU32', cpptypeinfo.UInt32()),
    'ImS64':
    parser.typedef('ImS64', cpptypeinfo.Int64()),
    'ImU64':
    parser.typedef('ImU64', cpptypeinfo.UInt64()),
    'ImVec2':
    parser.struct(
        'ImVec2',
        [Field(cpptypeinfo.Float(), 'x'),
         Field(cpptypeinfo.Float(), 'y')]),
    'ImVec4':
    parser.struct('ImVec4', [
        Field(cpptypeinfo.Float(), 'x'),
        Field(cpptypeinfo.Float(), 'y'),
        Field(cpptypeinfo.Float(), 'z'),
        Field(cpptypeinfo.Float(), 'w')
    ]),
    'CreateContext':
    Function(Pointer(parser.parse('struct ImGuiContext')), [
        Param(Pointer(parser.parse('struct ImFontAtlas')), 'shared_font_atlas',
              'NULL')
    ]),
    'DestroyContext':
    Function(
        cpptypeinfo.Void(),
        [Param(Pointer(parser.parse('struct ImGuiContext')), 'ctx', 'NULL')]),
    'GetCurrentContext':
    Function(Pointer(parser.parse('struct ImGuiContext')), []),
    'SetCurrentContext':
    Function(cpptypeinfo.Void(),
             [Param(Pointer(parser.parse('struct ImGuiContext')), 'ctx')]),
    'DebugCheckVersionAndDataLayout':
    Function(cpptypeinfo.Bool(), [
        Param(('const char*'), 'version_str'),
        Param(cpptypeinfo.UInt64(), 'sz_io'),
        Param(cpptypeinfo.UInt64(), 'sz_style'),
        Param(cpptypeinfo.UInt64(), 'sz_vec2'),
        Param(cpptypeinfo.UInt64(), 'sz_vec4'),
        Param(cpptypeinfo.UInt64(), 'sz_drawvert'),
        Param(cpptypeinfo.UInt64(), 'sz_drawidx'),
    ]),
    # ImGuiIO & GetIO ( )
    'GetIO':
    Function(parser.parse('ImGuiIO &'), []),
    # ImGuiStyle & GetStyle ( )
    'GetStyle':
    Function(parser.parse('ImGuiStyle &'), []),
    # void NewFrame ( )
    'NewFrame':
    Function(cpptypeinfo.Void(), []),
    'EndFrame':
    Function(cpptypeinfo.Void(), []),
    'Render':
    Function(cpptypeinfo.Void(), []),
    # ImDrawData * GetDrawData ( )
    'GetDrawData':
    Function(parser.parse('ImDrawData *'), []),
    # void ShowDemoWindow ( bool * p_open = NULL )
    'ShowDemoWindow':
    Function(cpptypeinfo.Void(),
             [Param(parser.parse('bool *'), 'p_open', 'NULL')]),
    # void ShowAboutWindow ( bool * p_open = NULL )
    'ShowAboutWindow':
    Function(cpptypeinfo.Void(),
             [Param(parser.parse('bool *'), 'p_open', 'NULL')]),
    # void ShowMetricsWindow ( bool * p_open = NULL )
    'ShowMetricsWindow':
    Function(cpptypeinfo.Void(),
             [Param(parser.parse('bool *'), 'p_open', 'NULL')]),
    # void ShowStyleEditor ( ImGuiStyle * ref = NULL )
    'ShowStyleEditor':
    Function(cpptypeinfo.Void(),
             [Param(parser.parse('ImGuiStyle *'), 'ref', 'NULL')]),
    # bool ShowStyleSelector ( const char * label )
    'ShowStyleSelector':
    Function(cpptypeinfo.Bool(),
             [Param(parser.parse('const char*'), 'label')]),
    # void ShowFontSelector ( const char * label )
    'ShowFontSelector':
    Function(cpptypeinfo.Void(),
             [Param(parser.parse('const char*'), 'label')]),
    # void ShowUserGuide ( )
    'ShowUserGuide':
    Function(cpptypeinfo.Void(), []),
    # const char * GetVersion ( )
    'GetVersion':
    Function(parser.parse('const char*'), []),
    # void StyleColorsDark ( ImGuiStyle * dst = NULL )
    'StyleColorsDark':
    Function(cpptypeinfo.Void(),
             [Param(parser.parse('ImGuiStyle *'), 'dst', 'NULL')]),
    # void StyleColorsClassic ( ImGuiStyle * dst = NULL )
    'StyleColorsClassic':
    Function(cpptypeinfo.Void(),
             [Param(parser.parse('ImGuiStyle *'), 'dst', 'NULL')]),
    # void StyleColorsLight ( ImGuiStyle * dst = NULL )
    'StyleColorsLight':
    Function(cpptypeinfo.Void(),
             [Param(parser.parse('ImGuiStyle *'), 'dst', 'NULL')]),
    # bool Begin ( const char * name , bool * p_open = NULL , ImGuiWindowFlags flags = 0 )
    'Begin':
    Function(cpptypeinfo.Bool(), [
        Param(parser.parse('const char *'), 'name'),
        Param(parser.parse('bool *'), 'p_open', 'NULL'),
        Param(parser.parse('ImGuiWindowFlags'), 'flags', '0')
    ]),
    'End':
    Function(cpptypeinfo.Void(), []),
    # bool BeginChild ( const char * str_id , const ImVec2 & size = ImVec2 ( 0 , 0 ) , bool border = false , ImGuiWindowFlags flags = 0 )
    # bool BeginChild(ImGuiID id, const ImVec2& size = ImVec2(0,0), bool border = false, ImGuiWindowFlags flags = 0);
    # function overloading
    'BeginChild': [
        Function(cpptypeinfo.Bool(), [
            Param(parser.parse('const char *'), 'str_id'),
            Param(Param('const ImVec2 &'), 'size', 'ImVec2(0,0)'),
            Param(Param('bool'), 'border', 'false'),
            Param(parser.parse('ImGuiWindowFlags'), 'flags', '0')
        ])
    ],
    '__dummy__0':
    None,
    'EndChild':
    Function(cpptypeinfo.Void(), []),
    # bool IsWindowAppearing ( )
    'IsWindowAppearing':
    Function(cpptypeinfo.Bool(), []),
    # bool IsWindowCollapsed ( )
    'IsWindowCollapsed':
    Function(cpptypeinfo.Bool(), []),
    # bool IsWindowFocused ( ImGuiFocusedFlags flags = 0 )
    'IsWindowFocused':
    Function(cpptypeinfo.Bool(),
             [Param(parser.parse('ImGuiFocusedFlags'), 'flags', '0')]),
    # bool IsWindowHovered ( ImGuiHoveredFlags flags = 0 )
    'IsWindowHovered':
    Function(cpptypeinfo.Bool(),
             [Param(parser.parse('ImGuiHoveredFlags'), 'flags', '0')]),
    # ImDrawList * GetWindowDrawList ( )
    'GetWindowDrawList':
    Function(parser.parse('ImDrawList*'), []),
    # ImVec2 GetWindowPos ( )
    'GetWindowPos':
    Function(parser.parse('ImVec2'), []),
    # ImVec2 GetWindowSize ( )
    'GetWindowSize':
    Function(parser.parse('ImVec2'), []),
    # float GetWindowWidth ( )
    'GetWindowWidth':
    Function(cpptypeinfo.Float(), []),
    'GetWindowHeight':
    Function(cpptypeinfo.Float(), []),
    # void SetNextWindowPos ( const ImVec2 & pos , ImGuiCond cond = 0 , const ImVec2 & pivot = ImVec2 ( 0 , 0 ) )
    'SetNextWindowPos':
    Function(cpptypeinfo.Void(), [
        Param(parser.parse('const ImVec2&'), 'pos'),
        Param(parser.parse('ImGuiCond'), 'cond', '0'),
        Param(parser.parse('const ImVec2 &'), 'pivot', 'ImVec2(0,0)'),
    ]),
    # void SetNextWindowSize ( const ImVec2 & size , ImGuiCond cond = 0 )
    'SetNextWindowSize':
    Function(cpptypeinfo.Void(), [
        Param(parser.parse('const ImVec2 &'), 'size'),
        Param(parser.parse('ImGuiCond'), 'cond', '0')
    ]),
    # void SetNextWindowSizeConstraints ( const ImVec2 & size_min , const ImVec2 & size_max , ImGuiSizeCallback custom_callback = NULL , void * custom_callback_data = NULL )
    'SetNextWindowSizeConstraints':
    Function(cpptypeinfo.Void(), [
        Param(parser.parse('const ImVec2 &'), 'size_min'),
        Param(parser.parse('const ImVec2 &'), 'size_max'),
        Param(parser.parse('ImGuiSizeCallback'), 'custom_callback', 'NULL'),
        Param(parser.parse('void *'), 'custom_callback_data', 'NULL')
    ]),
    # void SetNextWindowContentSize ( const ImVec2 & size )
    'SetNextWindowContentSize':
    Function(cpptypeinfo.Void(), [
        Param(parser.parse('const ImVec2 &'), 'size'),
    ]),
    # void SetNextWindowCollapsed ( bool collapsed , ImGuiCond cond = 0 )
    'SetNextWindowCollapsed':
    Function(cpptypeinfo.Void(), [
        Param(cpptypeinfo.Bool(), 'collapsed'),
        Param(parser.parse('ImGuiCond'), 'cond', '0'),
    ]),
    # void SetNextWindowFocus ( )
    'SetNextWindowFocus':
    Function(cpptypeinfo.Void(), []),
    # void SetNextWindowBgAlpha ( float alpha )
    'SetNextWindowBgAlpha':
    Function(cpptypeinfo.Void(), [Param(cpptypeinfo.Float(), 'alpha')]),
    # void SetWindowPos ( const ImVec2 & pos , ImGuiCond cond = 0 )
    # void SetWindowPos(const char* name, const ImVec2& pos, ImGuiCond cond = 0);
    # function overloading
    'SetWindowPos': [
        Function(cpptypeinfo.Void(), [
            Param(parser.parse('const ImVec2 &'), 'pos'),
            Param(parser.parse('ImGuiCond'), 'cond', '0'),
        ])
    ],
    '__dummy__1':
    None,
    # void SetWindowSize ( const ImVec2 & size , ImGuiCond cond = 0 )
    # void          SetWindowSize(const char* name, const ImVec2& size, ImGuiCond cond = 0);
    # function overloading
    'SetWindowSize': [
        Function(cpptypeinfo.Void(), [
            Param(parser.parse('const ImVec2 &'), 'size'),
            Param(parser.parse('ImGuiCond'), 'cond', '0'),
        ])
    ],
    '__dummy__2':
    None,
    # void SetWindowCollapsed ( bool collapsed , ImGuiCond cond = 0 )
    #  IMGUI_API void          SetWindowCollapsed(const char* name, bool collapsed, ImGuiCond cond = 0);   // set named window collapsed state
    'SetWindowCollapsed': [
        Function(cpptypeinfo.Void(), [
            Param(cpptypeinfo.Bool(), 'collapsed'),
            Param(parser.parse('ImGuiCond'), 'cond', '0'),
        ])
    ],
    '__dummy__3':
    None,
    # void SetWindowFocus ( )
    # IMGUI_API void          SetWindowFocus(const char* name);
    'SetWindowFocus': [Function(cpptypeinfo.Void(), [])],
    '__dummy__4':
    None,
    # void SetWindowFontScale ( float scale )
    'SetWindowFontScale':
    Function(cpptypeinfo.Void(), [Param(cpptypeinfo.Float(), 'scale')]),
    # ImVec2 GetContentRegionMax ( )
    'GetContentRegionMax':
    Function(parser.parse('ImVec2'), []),
    # ImVec2 GetContentRegionAvail ( )
    'GetContentRegionAvail':
    Function(parser.parse('ImVec2'), []),
    # ImVec2 GetWindowContentRegionMin ( )
    'GetWindowContentRegionMin':
    Function(parser.parse('ImVec2'), []),
    # ImVec2 GetWindowContentRegionMax ( )
    'GetWindowContentRegionMax':
    Function(parser.parse('ImVec2'), []),
    # float GetWindowContentRegionWidth ( )
    'GetWindowContentRegionWidth':
    Function(cpptypeinfo.Float(), []),
    # float GetScrollX ( )
    'GetScrollX':
    Function(cpptypeinfo.Float(), []),
    'GetScrollY':
    Function(cpptypeinfo.Float(), []),
    'GetScrollMaxX':
    Function(cpptypeinfo.Float(), []),
    'GetScrollMaxY':
    Function(cpptypeinfo.Float(), []),
    # void SetScrollX ( float scroll_x )
    'SetScrollX':
    Function(cpptypeinfo.Void(), [Param(cpptypeinfo.Float(), 'scroll_x')]),
    'SetScrollY':
    Function(cpptypeinfo.Void(), [Param(cpptypeinfo.Float(), 'scroll_y')]),
    # void SetScrollHereX ( float center_x_ratio = 0.5f )
    'SetScrollHereX':
    Function(cpptypeinfo.Void(),
             [Param(cpptypeinfo.Float(), 'center_x_ratio', '0.5f')]),
    'SetScrollHereY':
    Function(cpptypeinfo.Void(),
             [Param(cpptypeinfo.Float(), 'center_y_ratio', '0.5f')]),
    # void SetScrollFromPosX ( float local_x , float center_x_ratio = 0.5f )
    'SetScrollFromPosX':
    Function(cpptypeinfo.Void(), [
        Param(cpptypeinfo.Float(), 'local_x'),
        Param(cpptypeinfo.Float(), 'center_x_ratio', '0.5f')
    ]),
    'SetScrollFromPosY':
    Function(cpptypeinfo.Void(), [
        Param(cpptypeinfo.Float(), 'local_y'),
        Param(cpptypeinfo.Float(), 'center_y_ratio', '0.5f')
    ]),
    # void PushFont ( ImFont * font )
    'PushFont':
    Function(cpptypeinfo.Void(), [Param(parser.parse('ImFont*'), 'font')]),
    # void PopFont ( )
    'PopFont':
    Function(cpptypeinfo.Void(), []),
    # void PushStyleColor ( ImGuiCol idx , ImU32 col )
    # void PushStyleColor ( ImGuiCol idx , ImU32 col )
    'PushStyleColor': [
        Function(cpptypeinfo.Void(), [
            Param(parser.parse('ImGuiCol'), 'idx'),
            Param(parser.parse('ImU32'), 'col')
        ])
    ],
    '__dummy__5':
    None,
    # void PopStyleColor ( int count = 1 )
    'PopStyleColor':
    Function(cpptypeinfo.Void(), [Param(cpptypeinfo.Int32(), 'count', '1')]),
    # void PushStyleVar ( ImGuiStyleVar idx , float val )
    # void PushStyleVar(ImGuiStyleVar idx, const ImVec2& val);
    'PushStyleVar': [
        Function(cpptypeinfo.Void(), [
            Param(parser.parse('ImGuiCol'), 'idx'),
            Param(cpptypeinfo.Float(), 'val')
        ])
    ],
    '__dummy__6':
    None,
    # :void PopStyleVar ( int count = 1 )
    'PopStyleVar':
    Function(cpptypeinfo.Void(), [
        Param(cpptypeinfo.Int32(), 'count', '1'),
    ]),
    # const ImVec4 & GetStyleColorVec4 ( ImGuiCol idx )
    'GetStyleColorVec4':
    Function(parser.parse('const ImVec4 &'),
             [Param(parser.parse('ImGuiCol'), 'idx')]),
    # ImFont * GetFont ( )
    'GetFont':
    Function(parser.parse('ImFont*'), []),
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
    parser.parse('struct ImNewDummy'),
    'operator new': [],
    'operator delete': [],
    'IM_DELETE': [],
    #
    'ImVector':
    parser.parse('struct ImVector'),
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
    parser.typedef('ImDrawIdx', cpptypeinfo.UInt16()),
    'ImDrawCornerFlags_': [],
    'ImDrawListFlags_': [],
    'ImFontAtlasCustomRect': [],
    'ImFontAtlasFlags_': [],
}


class ImGuiTest(unittest.TestCase):
    def test_imgui_h(self) -> None:
        cpptypeinfo.parse_headers(parser,
                                  IMGUI_H,
                                  cpp_flags=[
                                      '-DIMGUI_DISABLE_OBSOLETE_FUNCTIONS',
                                  ])

        for ns in parser.root_namespace.traverse():
            if ns.struct:
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
