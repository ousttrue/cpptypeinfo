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

    def test_excpt(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 '''
        int __cdecl __C_specific_handler(
            struct _EXCEPTION_RECORD*   ExceptionRecord,
            void*                       EstablisherFrame,
            struct _CONTEXT*            ContextRecord,
            struct _DISPATCHER_CONTEXT* DispatcherContext
            );
''',
                                 debug=True)
        func = parser.root_namespace.functions[0]
        self.assertEqual(TypeRef(cpptypeinfo.Void(), False), func.result)
        self.assertEqual(1, len(func.params))
        self.assertEqual(TypeRef(cpptypeinfo.Int32()), func.params[0].typeref)


if __name__ == '__main__':
    unittest.main()
