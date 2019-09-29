import unittest
import cpptypeinfo


class TypedefTest(unittest.TestCase):
    def test_resolve_function(self) -> None:
        parser = cpptypeinfo.TypeParser()
        typedef = parser.typedef('uint8_t', 'unsigned char')
        self.assertEqual(typedef.get_concrete_type(), cpptypeinfo.UInt8())

    # ToDo: struct tag typedef


if __name__ == '__main__':
    unittest.main()
