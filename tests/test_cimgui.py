import unittest
import pathlib
import cpptypeinfo

HERE = pathlib.Path(__file__).absolute().parent
CIMGUI_H = HERE.parent / 'libs/cimgui/cimgui.h'


class CImguiTest(unittest.TestCase):
    def test_cimgui(self) -> None:
        ns = cpptypeinfo.push_namespace()
        cpptypeinfo.parse_headers(
            CIMGUI_H, cpp_flags=[f'-DCIMGUI_DEFINE_ENUMS_AND_STRUCTS'])
        cpptypeinfo.pop_namespace()

        for ns in ns.traverse():
            if isinstance(ns, cpptypeinfo.Struct):
                continue

            for k, v in ns.user_type_map.items():
                with self.subTest(name=k):
                    print(f'{ns}{v}')

            for v in ns.functions:
                if v.name:
                    with self.subTest(name=v.name):
                        print(f'{ns}{v}')


if __name__ == '__main__':
    unittest.main()
