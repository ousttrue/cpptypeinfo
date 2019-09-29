import unittest
import pathlib
import cpptypeinfo

HERE = pathlib.Path(__file__).absolute().parent
CIMGUI_H = HERE.parent / 'libs/cimgui/cimgui.h'


class CImguiTest(unittest.TestCase):
    def test_cimgui(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_files(
            parser, CIMGUI_H, cpp_flags=[f'-DCIMGUI_DEFINE_ENUMS_AND_STRUCTS'])

        for ns in parser.root_namespace.traverse():
            if isinstance(ns, cpptypeinfo.usertype.Struct):
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
