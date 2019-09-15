import unittest
import pathlib
from clang import cindex
import cpptypeinfo

HERE = pathlib.Path(__file__).absolute().parent
CIMGUI_H = HERE.parent / 'libs/cimgui/cimgui.h'


class CImguiTest(unittest.TestCase):
    def test_cindex(self) -> None:

        for c, parsed in cpptypeinfo.parse_header(CIMGUI_H):
            print(c, str(parsed))


if __name__ == '__main__':
    unittest.main()
