import unittest
import cpptypeinfo


class DeclarationTest(unittest.TestCase):
    def test_int(self) -> None:
        decl = cpptypeinfo.parse('int')
        self.assertEquals(decl, cpptypeinfo.Int32())

    def test_ptr(self) -> None:
        decl = cpptypeinfo.parse('int*')
        self.assertEquals(decl, cpptypeinfo.Pointer(cpptypeinfo.Int32()))


if __name__ == '__main__':
    unittest.main()
