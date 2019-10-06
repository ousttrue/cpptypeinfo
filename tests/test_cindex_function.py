import unittest
import cpptypeinfo
from cpptypeinfo.usertype import TypeRef


class CIndexFunctionTests(unittest.TestCase):
    def test_void_void(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'void func();', debug=True)
        func = parser.root_namespace.functions[0]
        self.assertEqual(TypeRef(cpptypeinfo.Void(), False), func.result)
        self.assertEqual(0, len(func.params))

    def test_void_int(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'void func(int a);', debug=True)
        func = parser.root_namespace.functions[0]
        self.assertEqual(TypeRef(cpptypeinfo.Void(), False), func.result)
        self.assertEqual(1, len(func.params))
        self.assertEqual(TypeRef(cpptypeinfo.Int32()), func.params[0].typeref)


if __name__ == '__main__':
    unittest.main()
