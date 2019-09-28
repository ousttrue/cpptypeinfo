import unittest
import cpptypeinfo


class ResolveTest(unittest.TestCase):
    def test_resolve(self) -> None:
        root = cpptypeinfo.push_namespace()
        typedef = cpptypeinfo.Typedef('uint8_t', cpptypeinfo.UInt8())
        func = cpptypeinfo.Function(typedef, [])
        cpptypeinfo.pop_namespace()

        root.resolve_typedef_by_name('uint8_t')
        self.assertEqual(func.result, cpptypeinfo.UInt8())


if __name__ == '__main__':
    unittest.main()
