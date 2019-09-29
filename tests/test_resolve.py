import unittest
import cpptypeinfo


class ResolveTest(unittest.TestCase):
    def test_resolve_function(self) -> None:
        parser = cpptypeinfo.TypeParser()
        parser.typedef('uint8_t', 'unsigned char')
        func = parser.parse('uint8_t* (uint8_t, const uint8_t *)').ref
        if not isinstance(func, cpptypeinfo.usertype.Function):
            raise Exception()
        parser.resolve_typedef_by_name('uint8_t')
        self.assertEqual(func.result,
                         cpptypeinfo.usertype.Pointer(cpptypeinfo.UInt8()))
        self.assertEqual(func.params[0].typeref, cpptypeinfo.UInt8())
        self.assertEqual(
            func.params[1].typeref,
            cpptypeinfo.usertype.Pointer(cpptypeinfo.UInt8().to_const()))

        # ToDo: struct
        # ToDo: nested namespace
        # ToDo: nested typedef


if __name__ == '__main__':
    unittest.main()
