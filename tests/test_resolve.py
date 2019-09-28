import unittest
import cpptypeinfo


class ResolveTest(unittest.TestCase):
    def test_resolve_function(self) -> None:
        parser = cpptypeinfo.TypeParser()
        parser.typedef('uint8_t', 'unsigned char')
        func = parser.parse('uint8_t* ()').ref
        if not isinstance(func, cpptypeinfo.user_type.Function):
            raise Exception()
        parser.resolve_typedef_by_name('uint8_t')
        self.assertEqual(func.result,
                         cpptypeinfo.user_type.Pointer(cpptypeinfo.UInt8()))

        # ToDo: function param
        # ToDo: struct
        # ToDo: nested namespace
        # ToDo: nested typedef


if __name__ == '__main__':
    unittest.main()
