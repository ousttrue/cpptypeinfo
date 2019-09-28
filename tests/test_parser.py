import unittest
from cpptypeinfo import (
    TypeParser,
    Float,
    Double,
    Bool,
    Void,
    Int8,
    Int16,
    Int32,
    Int64,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
)
from cpptypeinfo.user_type import (Pointer, Array, Field, Struct, Param,
                                   Function)


class ParserTest(unittest.TestCase):
    def test_parser(self) -> None:
        parser = TypeParser()
        self.assertEqual(parser.parse('bool'), Bool())
        self.assertEqual(parser.parse('double'), Double())
        self.assertEqual(parser.parse('int'), Int32())
        self.assertNotEqual(parser.parse('int'), UInt32())
        self.assertEqual(parser.parse('const int'), Int32().to_const())
        self.assertNotEqual(parser.parse('int'), Int32().to_const())
        self.assertEqual(parser.parse('char'), Int8())
        self.assertEqual(parser.parse('short'), Int16())
        self.assertEqual(parser.parse('long long'), Int64())
        self.assertEqual(parser.parse('unsigned int'), UInt32())
        self.assertEqual(parser.parse('const unsigned int'),
                         UInt32().to_const())
        self.assertNotEqual(parser.parse('unsigned int'), UInt32().to_const())
        self.assertEqual(parser.parse('unsigned char'), UInt8())
        self.assertEqual(parser.parse('unsigned short'), UInt16())
        self.assertEqual(parser.parse('unsigned long long'), UInt64())

        self.assertEqual(parser.parse('void*'), Pointer(Void()))
        self.assertEqual(parser.parse('const int*'),
                         Pointer(Int32().to_const()))
        self.assertEqual(parser.parse('int const*'),
                         Pointer(Int32().to_const()))
        self.assertEqual(parser.parse('int * const'),
                         Pointer(Int32()).to_const())
        self.assertEqual(parser.parse('const int * const'),
                         Pointer(Int32().to_const()).to_const())

        self.assertEqual(parser.parse('void**'), Pointer(Pointer(Void())))
        self.assertEqual(parser.parse('const void**'),
                         Pointer(Pointer(Void().to_const())))
        self.assertEqual(parser.parse('const int&'),
                         Pointer(Int32().to_const()))

        self.assertEqual(parser.parse('int[ ]'), Array(Int32()))
        self.assertEqual(parser.parse('int[5]'), Array(Int32(), 5))
        self.assertEqual(parser.parse('const int[5]'),
                         Array(Int32().to_const(), 5))
        self.assertEqual(parser.parse('const int*[5]'),
                         Array(Pointer(Int32().to_const()), 5))

        self.assertEqual(parser.parse('struct ImGuiInputTextCallbackData'),
                         Struct('ImGuiInputTextCallbackData'))
        self.assertEqual(
            parser.parse('int (*)(ImGuiInputTextCallbackData *)'),
            Function(Int32(), [
                Param(Pointer(Struct('ImGuiInputTextCallbackData')).to_ref())
            ]))

        vec2 = parser.parse('struct ImVec2').ref
        if not isinstance(vec2, Struct):
            raise Exception()
        vec2.add_field(Field(Float().to_ref(), 'x'))
        vec2.add_field(Field(Float().to_ref(), 'y'))
        self.assertEqual(
            vec2,
            Struct(
                'ImVec2',
                [Field(Float().to_ref(), 'x'),
                 Field(Float().to_ref(), 'y')]))

        parsed = parser.parse('const ImVec2 &')
        self.assertEqual(parsed, Pointer(Struct('ImVec2').to_const()))


if __name__ == '__main__':
    unittest.main()
