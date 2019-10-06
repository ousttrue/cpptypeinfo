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

    def test_function(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser, 'typedef void (*T)();', debug=True)
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

typedef T* TP;
''',
                                 debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()
        self.assertEqual(typedef.typeref.ref,
                         cpptypeinfo.usertype.Struct('Tag'))

    def test_struct_forward(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 '''
typedef struct Forward T;
''',
                                 debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()

    def test_struct_forward_pointer(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 '''
typedef struct Forward *T;
''',
                                 debug=True)
        typedef = parser.root_namespace.user_type_map['T']
        if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
            raise Exception()

    def test_linklist(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 '''
typedef struct _LIST_ENTRY {
   struct _LIST_ENTRY *Flink;
   struct _LIST_ENTRY *Blink;
} LIST_ENTRY;
''',
                                 debug=True)
        # typedef = parser.root_namespace.user_type_map['T']
        # if not isinstance(typedef, cpptypeinfo.usertype.Typedef):
        #     raise Exception()

    def test_elaborated(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 '''
typedef struct __crt_locale_pointers
{
    struct __crt_locale_data*    locinfo;
    struct __crt_multibyte_data* mbcinfo;
} __crt_locale_pointers
''',
                                 debug=True)

    def test_callback(self) -> None:
        parser = cpptypeinfo.TypeParser()
        cpptypeinfo.parse_source(parser,
                                 '''
typedef struct _NCB {
    void (*ncb_post)( struct _NCB * ); /* POST routine address        */
} NCB, *PNCB;
''',
                                 debug=True)

if __name__ == '__main__':
    # unittest.main()
    CIndexTypedefTest().test_callback()
