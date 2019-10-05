import unittest
import cpptypeinfo
import cpptypeinfo.usertype


class CIndexTypedefTest(unittest.TestCase):
    def test_resolve_function(self) -> None:
        parser = cpptypeinfo.TypeParser()
        typedef = parser.typedef('uint8_t', 'unsigned char')
        self.assertEqual(typedef.get_concrete_type(), cpptypeinfo.UInt8())

    def test_int8(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'typedef char T;', debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()
        self.assertEqual(typedef.typeref.ref, cpptypeinfo.Int8())

    def test_int8_ptr(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'typedef char* T;', debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()
        self.assertEqual(typedef.typeref.ref,
                         cpptypeinfo.usertype.Pointer(cpptypeinfo.Int8()))

    def test_int16(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'typedef short T;', debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()
        self.assertEqual(typedef.typeref.ref, cpptypeinfo.Int16())

    def test_int32(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'typedef int T;', debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()
        self.assertEqual(typedef.typeref.ref, cpptypeinfo.Int32())

    def test_int64(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'typedef long long T;', debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()
        self.assertEqual(typedef.typeref.ref, cpptypeinfo.Int64())

    def test_uint64(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 'typedef unsigned __int64 T;',
                                 debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()
        self.assertEqual(typedef.typeref.ref, cpptypeinfo.UInt64())

    def test_struct(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 '''
typedef struct Tag {
} T;
''',
                                 debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()
        self.assertEqual(typedef.typeref.ref,
                         cpptypeinfo.usertype.Struct('Tag'))


if __name__ == '__main__':
    unittest.main()
