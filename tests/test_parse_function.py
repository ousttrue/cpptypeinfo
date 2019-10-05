import unittest
import cpptypeinfo
from cpptypeinfo.usertype import TypeRef

SOURCE = '''
namespace A
{
    // -target=i686-pc-win32 only. ignored 64bit
    int __stdcall stdcall_func(const char *src);

    extern "C" void* Hello(const char *src);
    __declspec(dllexport) void* Export(const char *src);
    extern "C" __declspec(dllimport) void* C_Import(const char *src);

    void body(); // forward decl
    void body()
    {
    }
}'''


class FunctionTests(unittest.TestCase):
    # def test_function(self) -> None:
    #     parser = cpptypeinfo.TypeParser()
    #     cpptypeinfo.parse_source(parser, SOURCE, debug=True)

    def test_void_void(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'void func();', debug=True)
        func = parser.root_namespace.functions[0]
        self.assertEqual(TypeRef(cpptypeinfo.Void(), False), func.result)
        self.assertEqual(0, len(func.params))


if __name__ == '__main__':
    unittest.main()
