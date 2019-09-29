import unittest
import cpptypeinfo

SOURCE = '''
namespace A
{
    int __stdcall stdcall_func(const char *src); // -target=i686-pc-win32 only. ignored 64bit
    void __stdcall StdcallFunc(){}

    extern "C" void* Hello(const char *src);
    __declspec(dllexport) void* Export(const char *src);
    extern "C" __declspec(dllimport) void* C_Import(const char *src);

    void body(); // forward decl
    void body()
    {
    }
}'''


class FunctionTests(unittest.TestCase):
    def test_function(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 SOURCE,
                                 cpp_flags=['-target', 'x86_64-windows-msvc'],
                                 debug=True)


if __name__ == '__main__':
    unittest.main()
